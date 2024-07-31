import cv2
import numpy as np
import calc_tools as ct
import os

IMG_WIDTH = 1920
IMG_HEIGHT = 1080
MIN_DISTANCE_THRESHOLD = 0.1
OUTPUT_SIZE = (1050, 680)

def process_points_and_return_json(points_data, coordinates_data, frame_index, frame):
    # Initialize necessary variables
    intersections = []
    line_params = {}

    # Process points to calculate line parameters and intersections
    for key, points in points_data.items():
        if "Goal" in key or "Circle" in key:
            continue

        distance = ct.distance_between_points(points[0], points[1])
        if distance < MIN_DISTANCE_THRESHOLD:
            continue

        m, c = ct.compute_line_params(points[0], points[1], IMG_WIDTH, IMG_HEIGHT)
        line_params[key] = (m, c)

    all_detected_points=[]
    for key in points_data:
        all_detected_points.append(key)

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
                if 30 < point[0] < 1890 and 30 < point[1] < 1050:
                    intersections.append({
                        "lines": [line_name, "Circle central"],
                        "point": {"x": point[0], "y": point[1]}
                    })

            add_intersection("Middle line right", furthest_point_right)
            add_intersection("Middle line left", furthest_point_left)
            if "Middle line" in all_detected_points:
                add_intersection("Middle line low", lowest_point)
                add_intersection("Middle line high", highest_point)

    # Process circle right and left points
    def process_circle_side(key, line_key):
        max_distance = 0
        furthest_point = None
        if key in points_data:  # Ensure key exists in points_data
            for i in range(len(points_data[key])):
                circle_point = (
                    int(points_data[key][i]["x"] * IMG_WIDTH),
                    int(points_data[key][i]["y"] * IMG_HEIGHT)
                )
                distance = ct.distance_from_line(circle_point, line_params[line_key])
                if distance > max_distance:
                    max_distance = distance
                    furthest_point = circle_point
            if furthest_point:  # Ensure furthest_point is not None
                intersections.append({
                    "lines": [line_key, key],
                    "point": {"x": furthest_point[0], "y": furthest_point[1]}
                })

    # Check for existence of both keys in points_data before processing
    if "Circle right" in points_data and "Big rect. right main" in line_params:
        process_circle_side("Circle right", "Big rect. right main")

    if "Circle left" in points_data and "Big rect. left main" in line_params:
        process_circle_side("Circle left", "Big rect. left main")

    # 대칭점 계산
    all_circle_points=[]
    for key in intersections:
        all_circle_points.append(key["lines"][0])

    if "Middle line" in line_params:
        # print(line_params["Middle line"][0])
        if "Middle line right" in all_circle_points:
            if not "Middle line left" in all_circle_points:
                right = all_circle_points.index("Middle line right")
                left = ct.find_symmetric_point(intersections[right]["point"], line_params["Middle line"])
                intersections.append({
                    "lines": ["Middle line left", "Circle central"],
                    "point": {"x": left[0], "y": left[1]}
                })

        if "Middle line left" in all_circle_points:
            if not "Middle line right" in all_circle_points:
                left = all_circle_points.index("Middle line left")
                right = ct.find_symmetric_point(intersections[left]["point"], line_params["Middle line"])
                intersections.append({
                    "lines": ["Middle line right", "Circle central"],
                    "point": {"x": right[0], "y": right[1]}
                })

    # 여기까지 원 위의 점
    # 여기부터 직선 교점

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
                if -200 <= x <= IMG_WIDTH and -200 <= y <= IMG_HEIGHT:
                    intersections.append({
                        "lines": [key1, key2],
                        "point": {"x": x, "y": y}
                    })

    # Find matching points
    src_points, dst_points = ct.find_matching_points(intersections, coordinates_data)

    selected_src_points, selected_dst_points = ct.select_points(src_points, dst_points)

    # Calculate perspective transform matrix
    matrix = cv2.getPerspectiveTransform(selected_src_points, selected_dst_points)
    return matrix


    # # Dot at minimap
    # player_points = np.array([[1000, 600], [700, 400], [1000, 400], [700, 600]], dtype=np.float32)

    # # player_points를 (1, N, 2) 형태로 변환
    # player_points = player_points.reshape(-1, 1, 2)
    # # 투시 변환 적용하여 새로운 좌표 계산
    # transformed_player_points = cv2.perspectiveTransform(player_points, matrix)
    # # 원래 형태로 변환
    # transformed_player_points = transformed_player_points.reshape(-1, 2)
    # field_img = cv2.imread('./img/field.jpg')


    # for point in transformed_player_points:
    #     player_point = (int(point[0]), int(point[1]))
    #     radius = 10
    #     color = (255, 255, 255)
    #     thickness = -1
    #     transformed_image = cv2.circle(field_img, player_point, radius, color, thickness)


    # save file..
    # save_path = os.path.join('./outputs/minimap_tmp', f"{frame_index}.jpg")

    # image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # tv_image = cv2.warpPerspective(image, matrix, OUTPUT_SIZE)
    # cv2.imwrite(save_path, tv_image)