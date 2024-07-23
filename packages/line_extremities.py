import copy
import itertools
import json
import os
import random
from collections import deque
from io import BytesIO
import tempfile

import cv2 as cv
import numpy as np
import streamlit as st
import torch
import torch.backends.cudnn
import torch.nn as nn
import torchvision.transforms as T
from PIL import Image
from torchvision.models.segmentation import deeplabv3_resnet101
from tqdm import tqdm

from utils_calibration import SoccerPitch


def generate_class_synthesis(semantic_mask, radius):
    buckets = dict()
    kernel = np.ones((5, 5), np.uint8)
    semantic_mask = cv.erode(semantic_mask, kernel, iterations=1)
    for k, class_name in enumerate(SoccerPitch.lines_classes):
        mask = semantic_mask == k + 1
        if mask.sum() > 0:
            disk_list = synthesize_mask(mask, radius)
            if len(disk_list):
                buckets[class_name] = disk_list

    return buckets


def join_points(point_list, maxdist):
    polylines = []

    if not len(point_list):
        return polylines
    head = point_list[0]
    tail = point_list[0]
    polyline = deque()
    polyline.append(point_list[0])
    remaining_points = copy.deepcopy(point_list[1:])

    while len(remaining_points) > 0:
        min_dist_tail = 1000
        min_dist_head = 1000
        best_head = -1
        best_tail = -1
        for j, point in enumerate(remaining_points):
            dist_tail = np.sqrt(np.sum(np.square(point - tail)))
            dist_head = np.sqrt(np.sum(np.square(point - head)))
            if dist_tail < min_dist_tail:
                min_dist_tail = dist_tail
                best_tail = j
            if dist_head < min_dist_head:
                min_dist_head = dist_head
                best_head = j

        if min_dist_head <= min_dist_tail and min_dist_head < maxdist:
            polyline.appendleft(remaining_points[best_head])
            head = polyline[0]
            remaining_points.pop(best_head)
        elif min_dist_tail < min_dist_head and min_dist_tail < maxdist:
            polyline.append(remaining_points[best_tail])
            tail = polyline[-1]
            remaining_points.pop(best_tail)
        else:
            polylines.append(list(polyline.copy()))
            head = remaining_points[0]
            tail = remaining_points[0]
            polyline = deque()
            polyline.append(head)
            remaining_points.pop(0)
    polylines.append(list(polyline))
    return polylines


def get_line_extremities(buckets, maxdist, width, height, num_points_lines):
    extremities = dict()
    for class_name, disks_list in buckets.items():
        polyline_list = join_points(disks_list, maxdist)
        max_len = 0
        longest_polyline = []
        for polyline in polyline_list:
            if len(polyline) > max_len:
                max_len = len(polyline)
                longest_polyline = polyline
        extremities[class_name] = [
            {'x': longest_polyline[0][1] / width, 'y': longest_polyline[0][0] / height},
            {'x': longest_polyline[-1][1] / width, 'y': longest_polyline[-1][0] / height}, 
            
        ]
        num_points = num_points_lines
        if "Circle" in class_name:
            num_points = len(longest_polyline)#num_points_circles
        if num_points > 2:
            # equally spaced points along the longest polyline
            # skip first and last as they already exist
            for i in range(1, num_points - 1):
                extremities[class_name].insert(
                    len(extremities[class_name]) - 1,
                    {'x': longest_polyline[i * int(len(longest_polyline) / num_points)][1] / width, 'y': longest_polyline[i * int(len(longest_polyline) / num_points)][0] / height}
                )

    return extremities


def get_support_center(mask, start, disk_radius, min_support=0.1):
    x = int(start[0])
    y = int(start[1])
    support_pixels = 1
    result = [x, y]
    xstart = x - disk_radius
    if xstart < 0:
        xstart = 0
    xend = x + disk_radius
    if xend > mask.shape[0]:
        xend = mask.shape[0] - 1

    ystart = y - disk_radius
    if ystart < 0:
        ystart = 0
    yend = y + disk_radius
    if yend > mask.shape[1]:
        yend = mask.shape[1] - 1

    for i in range(xstart, xend + 1):
        for j in range(ystart, yend + 1):
            dist = np.sqrt(np.square(x - i) + np.square(y - j))
            if dist < disk_radius and mask[i, j] > 0:
                support_pixels += 1
                result[0] += i
                result[1] += j
    support = True
    if support_pixels < min_support * np.square(disk_radius) * np.pi:
        support = False

    result = np.array(result)
    result = np.true_divide(result, support_pixels)

    return support, result


def synthesize_mask(semantic_mask, disk_radius):
    mask = semantic_mask.copy().astype(np.uint8)
    points = np.transpose(np.nonzero(mask))
    disks = []
    while len(points):

        start = random.choice(points)
        dist = 10.
        success = True
        while dist > 1.:
            enough_support, center = get_support_center(mask, start, disk_radius)
            if not enough_support:
                bad_point = np.round(center).astype(np.int32)
                cv.circle(mask, (bad_point[1], bad_point[0]), disk_radius, (0), -1)
                success = False
            dist = np.sqrt(np.sum(np.square(center - start)))
            start = center
        if success:
            disks.append(np.round(start).astype(np.int32))
            cv.circle(mask, (disks[-1][1], disks[-1][0]), disk_radius, 0, -1)
        points = np.transpose(np.nonzero(mask))

    return disks


class CustomNetwork:

    def __init__(self, checkpoint):
        print("Loading model" + checkpoint)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = deeplabv3_resnet101(num_classes=len(SoccerPitch.lines_classes) + 1, aux_loss=True)
        self.model.load_state_dict(torch.load(checkpoint, map_location=torch.device('cpu'))["model"], strict=False)
        self.model.to(self.device)
        self.model.eval()
        print("using", self.device)

    def forward(self, img):
        trf = T.Compose(
            [
                T.Resize(256),
                T.ToTensor(),
                T.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ]
        )
        img = trf(img).unsqueeze(0).to(self.device)
        result = self.model(img)["out"].detach().squeeze(0).argmax(0)
        result = result.cpu().numpy().astype(np.uint8)
        return result


def process_video(video_bytes, checkpoint, output_dir, resolution_width, resolution_height, pp_radius, pp_maxdists, num_points_lines, masks):
    lines_palette = [0, 0, 0]
    for line_class in SoccerPitch.lines_classes:
        lines_palette.extend(SoccerPitch.palette[line_class])

    model = CustomNetwork(checkpoint)

    # Create a temporary file to store the video bytes
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video_file:
        temp_video_file.write(video_bytes)
        temp_video_path = temp_video_file.name

    cap = cv.VideoCapture(temp_video_path)
    if not cap.isOpened():
        print("Error opening video stream or file")
        return

    radius = pp_radius
    maxdists = pp_maxdists

    frame_index = 0
    with tqdm(total=int(cap.get(cv.CAP_PROP_FRAME_COUNT)), ncols=160) as t:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            output_prediction_folder = os.path.join(output_dir, "output")
            if not os.path.exists(output_prediction_folder):
                os.makedirs(output_prediction_folder)

            image = Image.fromarray(cv.cvtColor(frame, cv.COLOR_BGR2RGB))

            semlines = model.forward(image)

            if masks:
                mask = Image.fromarray(semlines.astype(np.uint8)).convert('P')
                mask.putpalette(lines_palette)
                mask_file = os.path.join(output_prediction_folder, f"{frame_index:04d}.jpg")
                mask.convert("RGB").save(mask_file)

            skeletons = generate_class_synthesis(semlines, radius)
            extremities = get_line_extremities(skeletons, maxdists, resolution_width, resolution_height, num_points_lines)

            prediction_file = os.path.join(output_prediction_folder, f"{frame_index:04d}.json")
            with open(prediction_file, "w") as f:
                json.dump(extremities, f, indent=4)

            frame_index += 1
            t.update(1)

    cap.release()
    cv.destroyAllWindows()
    os.remove(temp_video_path)  # Clean up the temporary file


def main():
    st.title("Video Processing for Soccer Line Detection")

    checkpoint = "./train_59.pt"
    output_dir = "./outputs"
    resolution_width = 455
    resolution_height = 256
    pp_radius = 4
    pp_maxdists = 30
    num_points_lines = 2
    masks = False

    video_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])
    if video_file is not None:
        st.write("Processing video...")
        video_bytes = video_file.read()
        process_video(video_bytes, checkpoint, output_dir, resolution_width, resolution_height, pp_radius, pp_maxdists, num_points_lines, masks)
        st.write("Processing complete. Check the output directory for results.")

if __name__ == "__main__":
    main()
