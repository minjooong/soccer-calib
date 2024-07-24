import cv2
import numpy as np
import json
import calc_tools as ct

IMG_WIDTH = 1920
IMG_HEIGHT = 1080
MIN_DISTANCE_THRESHOLD = 0.1
OUTPUT_SIZE = (1050, 680)

def process_points_and_return_json(points_data, coordinates_data):
    # Initialize necessary variables
    intersections = []
    line_params = {}
    furthest_points = {}

    # Process points to calculate line parameters and intersections
    for key, points in points_data.items():
        if "Goal" in key or "Circle" in key:
            continue

        distance = ct.distance_between_points(points[0], points[1])
        if distance < MIN_DISTANCE_THRESHOLD:
            continue

        m, c = ct.compute_line_params(points[0], points[1], IMG_WIDTH, IMG_HEIGHT)
        line_params[key] = (m, c)

    # Process circle central points to find furthest points
    for key, points in points_data.items():
        if "Circle central" in key:
            max_x = float('-inf')
            min_x = float('inf')
            max_y = float('-inf')
            min_y = float('inf')

            for i in range(len(points)):
                circle_point = (int(points[i]["x"] * IMG_WIDTH), int(points[i]["y"] * IMG_HEIGHT))
                if circle_point[0] > max_x:
                    max_x = circle_point[0]
                    furthest_point_right = circle_point
                if circle_point[0] < min_x:
                    min_x = circle_point[0]
                    furthest_point_left = circle_point
                if circle_point[1] > max_y:
                    max_y = circle_point[1]
                    lowest_point = circle_point
                if circle_point[1] < min_y:
                    min_y = circle_point[1]
                    highest_point = circle_point

            def add_intersection(line_name, point):
                if 80 < point[0] < 1840 and 80 < point[1] < 1000:
                    intersections.append({
                        "lines": [line_name, "Circle central"],
                        "point": {"x": point[0], "y": point[1]}
                    })

            add_intersection("Middle line right", furthest_point_right)
            add_intersection("Middle line left", furthest_point_left)
            add_intersection("Middle line low", lowest_point)
            add_intersection("Middle line high", highest_point)

    # Process circle right and left points
    def process_circle_side(key, line_key):
        max_distance = 0
        for i in range(len(points_data[key])):
            circle_point = (int(points_data[key][i]["x"] * IMG_WIDTH), int(points_data[key][i]["y"] * IMG_HEIGHT))
            distance = ct.distance_from_line(circle_point, line_params[line_key])
            if distance > max_distance:
                max_distance = distance
                furthest_point = circle_point
        intersections.append({
            "lines": [line_key, key],
            "point": {"x": furthest_point[0], "y": furthest_point[1]}
        })

    if "Circle right" in points_data:
        process_circle_side("Circle right", "Big rect. right main")

    if "Circle left" in points_data:
        process_circle_side("Circle left", "Big rect. left main")

    # Find intersections between lines
    keys = list(line_params.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            key1, key2 = keys[i], keys[j]
            m1, c1 = line_params[key1]
            m2, c2 = line_params[key2]
            intersection = ct.find_intersection(m1, c1, m2, c2)
            if intersection:
                x, y = intersection
                if 0 <= x <= IMG_WIDTH and 0 <= y <= IMG_HEIGHT:
                    intersections.append({
                        "lines": [key1, key2],
                        "point": {"x": x, "y": y}
                    })

    # Find matching points
    src_points, dst_points = ct.find_matching_points(intersections, coordinates_data)

    # Select src and dst points for perspective transform
    sum_values = [x + y for x, y in src_points]
    diff_values = [x - y for x, y in src_points]

    min_sum_idx = np.argmin(sum_values)
    max_sum_idx = np.argmax(sum_values)
    diff_values[min_sum_idx] = np.inf
    diff_values[max_sum_idx] = np.inf
    min_diff_idx = np.argmin(diff_values)
    diff_values[min_sum_idx] = -np.inf
    diff_values[max_sum_idx] = -np.inf
    max_diff_idx = np.argmax(diff_values)

    selected_src_points = np.array([
        src_points[min_sum_idx],
        src_points[min_diff_idx],
        src_points[max_sum_idx],
        src_points[max_diff_idx]
    ], dtype=np.float32)

    selected_dst_points = np.array([
        dst_points[min_sum_idx],
        dst_points[min_diff_idx],
        dst_points[max_sum_idx],
        dst_points[max_diff_idx]
    ], dtype=np.float32)

    # Calculate perspective transform matrix
    matrix = cv2.getPerspectiveTransform(selected_src_points, selected_dst_points)
    print(matrix)
    



# 투시 변환 적용
# transformed_image = cv2.warpPerspective(image_cv, matrix, OUTPUT_SIZE)

# 결과 이미지 저장
# cv2.imwrite('./outputs/transformed_image.jpg', transformed_image)
