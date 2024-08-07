import cv2
import calc_tools as ct

IMG_WIDTH = 1920
IMG_HEIGHT = 1080
MIN_DISTANCE_THRESHOLD = 0.04
OUTPUT_SIZE = (1050, 680)

def process_points_and_return_json(points_data, coordinates_data):

    intersections = []
    line_params = {}

    # 점을 이어 직선의 파라미터를 구한다.
    for key, points in points_data.items():
        if "Goal" in key or "Circle" in key:
            continue
        distance = ct.distance_between_points(points[0], points[1])
        if distance < MIN_DISTANCE_THRESHOLD:
            continue
        m, c = ct.compute_line_params(points[0], points[1], IMG_WIDTH, IMG_HEIGHT)
        line_params[key] = (m, c)


    # # 수평선의 경우 기울기가 너무 다른 선은 제외한다.
    # relevant_slopes = {key: value[0] for key, value in line_params.items() if 'top' in key or 'bottom' in key}
    # avg_slope = sum(relevant_slopes.values()) / len(relevant_slopes)
    # filtered_line_params = {key: value for key, value in line_params.items()
    #                         if key not in relevant_slopes or ct.slope_diff_in_degrees(value[0], avg_slope) <= 5}
    # line_params = filtered_line_params


    # 원들의 기준점을 구한다.
    for key, points in points_data.items():
        # 중심원
        if "Circle central" in key:
            ct.process_middle_circle(points, IMG_WIDTH, IMG_HEIGHT, intersections, line_params)
        # 오른쪽 반원
        elif "Circle right" in key:
            ct.process_circle_right(points, IMG_WIDTH, IMG_HEIGHT, intersections, line_params)
        # 왼쪽 반원
        elif "Circle left" in key:
            ct.process_circle_left(points, IMG_WIDTH, IMG_HEIGHT, intersections, line_params)


    # 나와있는 선들을 가지고 교점을 찾는다.
    keys = list(line_params.keys())
    for i in range(len(keys)):
        for j in range(i+1, len(keys)):
            key1, key2 = keys[i], keys[j]
            intersection = ct.find_intersection(line_params[key1], line_params[key2])
            if intersection:
                x, y = intersection
                if -500 <= x <= IMG_WIDTH + 500 and -300 <= y <= IMG_HEIGHT + 300:
                    intersections.append({
                        "lines": [key1, key2],
                        "point": {"x": x, "y": y}
                    })


    # 만약 circle right 와 circle left 중 하나만 있는 경우 선대칭으로 나머지 하나를 구한다.
    if len(line_params) < 4:
        all_circle_points=[]
        for key in intersections:
            all_circle_points.append(key["lines"][0])

        if "Middle line" in line_params:
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



    # 혹시 교점이 모자란 경우
    # Big rect 중간점 추측
    src_points, dst_points = ct.find_matching_points(intersections, coordinates_data)

    if len(src_points) < 5:
        ct.presume_rect_half(intersections, 'Middle line left', "Side line top", "Big rect. left main", line_params)
        ct.presume_rect_half(intersections, 'Middle line right', "Side line top", "Big rect. right main", line_params)

    # Side top 끝점 추측
    src_points, dst_points = ct.find_matching_points(intersections, coordinates_data)

    if len(src_points) < 5:
        big_rect_right, big_rect_left, circle_right, circle_left = ct.points_circle_center_to_side_line(intersections)

        # Assuming intersections and line_params are defined and populated somewhere above
        ct.presume_side_intersection(big_rect_right, circle_right, "right", intersections, line_params, IMG_WIDTH, IMG_HEIGHT)
        ct.presume_side_intersection(big_rect_left, circle_left, "left", intersections, line_params, IMG_WIDTH, IMG_HEIGHT)

    # Side bottom 중간점 추측
    src_points, dst_points = ct.find_matching_points(intersections, coordinates_data)

    if len(src_points) < 5:
        ct.presume_side_bottom_intersection(
            intersections, 'Side line top', 'Middle line', 'Middle line left', 'Circle central', 
            'Side line bottom', line_params, IMG_WIDTH, IMG_HEIGHT
        )
        ct.presume_side_bottom_intersection(
            intersections, 'Side line top', 'Middle line', 'Middle line right', 'Circle central', 
            'Side line bottom', line_params, IMG_WIDTH, IMG_HEIGHT
        )





    # Find matching points
    src_points, dst_points = ct.find_matching_points(intersections, coordinates_data)

    selected_src_points, selected_dst_points = ct.select_points(src_points, dst_points)

    # Calculate perspective transform matrix
    matrix = cv2.getPerspectiveTransform(selected_src_points, selected_dst_points)
    return matrix

