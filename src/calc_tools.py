import numpy as np
from itertools import combinations
import math

# Function to compute the line parameters
def compute_line_params(point1, point2, IMG_WIDTH, IMG_HEIGHT):
    x1, y1 = point1["x"]*IMG_WIDTH, point1["y"]*IMG_HEIGHT
    x2, y2 = point2["x"]*IMG_WIDTH, point2["y"]*IMG_HEIGHT
    # Line equation: y = mx + c
    if x2 - x1 == 0:  # vertical line
        return None, x1  # return None for slope (undefined), and x-intercept
    m = (y2 - y1) / (x2 - x1)
    c = y1 - m * x1
    return m, c

# 두 선의 교점 반환 함수
def find_intersection(line1, line2):
    m1, c1 = line1
    m2, c2 = line2
    if m1 == m2:
        return None  # 평행할때
    if m1 is None:  # 1번 선이 수직일떄
        x = c1
        y = m2 * x + c2
    elif m2 is None:  # 2번 선이 수직일떄
        x = c2
        y = m1 * x + c1
    else:
        x = (c2 - c1) / (m1 - m2)
        y = m1 * x + c1
    return x, y

def find_matching_points(intersections, coordinates_data):
    def lines_match(lines1, lines2):
        return set(lines1) == set(lines2)

    intersection_points = []
    coordinate_points = []

    for intersection in intersections:
        intersection_lines = intersection['lines']
        intersection_point = intersection['point']

        for coordinate in coordinates_data['coordinates']:
            coordinate_lines = coordinate['lines']
            coordinate_point = coordinate['point']

            if lines_match(intersection_lines, coordinate_lines):
                intersection_points.append([intersection_point['x'], intersection_point['y']])
                coordinate_points.append([coordinate_point['x'], coordinate_point['y']])

    intersection_points_array = np.array(intersection_points, dtype=np.float32)
    coordinate_points_array = np.array(coordinate_points, dtype=np.float32)

    return intersection_points_array, coordinate_points_array

def distance_from_line(point, line_params):
    x, y = point
    m, c = line_params
    if m is None:  # vertical line
        return abs(x - c)
    return abs(m * x - y + c) / (m**2 + 1)**0.5

def distance_from_middle_line(point, line_params):
    x, y = point
    m, c = line_params
    if m is None:  # vertical line
      return x - c
    return (m * x - y + c) / (m**2 + 1)**0.5

def distance_between_points(point1, point2):
    return np.sqrt((point2["x"] - point1["x"]) ** 2 + (point2["y"] - point1["y"]) ** 2)

def find_symmetric_point(point, middle_line_params):
    x, y = point["x"], point["y"]
    m, c = middle_line_params

    if m is not None:
        # Reflection formulas for non-vertical line
        d = (x + (y - c) * m) / (1 + m ** 2)
        x_sym = 2 * d - x
        y_sym = 2 * d * m - y + 2 * c
    else:
        # Reflection for vertical line, c represents the x-intercept
        x_sym = 2 * c - x
        y_sym = y

    return (int(x_sym), int(y_sym))

# 중앙원 기준점 반환 함수
def process_middle_circle(points, IMG_WIDTH, IMG_HEIGHT, intersections, line_params):
    max_x = float('-inf')
    min_x = float('inf')
    max_y = float('-inf')
    min_y = float('inf')

    furthest_point_right = None
    furthest_point_left = None
    lowest_point = None
    highest_point = None

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

    if furthest_point_right and 20 < furthest_point_right[0] < 1900 and 20 < furthest_point_right[1] < 1060:
        intersections.append({
            "lines": ["Middle line right", "Circle central"],
            "point": {"x": furthest_point_right[0], "y": furthest_point_right[1]}
        })

    if furthest_point_left and 20 < furthest_point_left[0] < 1900 and 20 < furthest_point_left[1] < 1060:
        intersections.append({
            "lines": ["Middle line left", "Circle central"],
            "point": {"x": furthest_point_left[0], "y": furthest_point_left[1]}
        })

    if "Middle line" in line_params:
        if lowest_point and 20 < lowest_point[0] < 1900 and 20 < lowest_point[1] < 1060:
            intersections.append({
                "lines": ["Middle line low", "Circle central"],
                "point": {"x": lowest_point[0], "y": lowest_point[1]}
            })

        if highest_point and 20 < highest_point[0] < 1900 and 20 < highest_point[1] < 1060:
            intersections.append({
                "lines": ["Middle line high", "Circle central"],
                "point": {"x": highest_point[0], "y": highest_point[1]}
            })

# 반원 점 구하는 함수
def process_circle_right(points, IMG_WIDTH, IMG_HEIGHT, intersections, line_params):
    max_distance = 0
    furthest_point = None
    for i in range(len(points)):
        circle_point = (int(points[i]["x"] * IMG_WIDTH), int(points[i]["y"] * IMG_HEIGHT))
        distance = distance_from_line(circle_point, line_params["Big rect. right main"])
        if distance > max_distance:
            max_distance = distance
            furthest_point = circle_point
    if furthest_point:
        intersections.append({
            "lines": ["Big rect. right main", "Circle right"],
            "point": {"x": furthest_point[0], "y": furthest_point[1]}
        })
        # cv2.circle(image_cv, furthest_point, 10, (255, 255, 0), -1)

def process_circle_left(points, IMG_WIDTH, IMG_HEIGHT, intersections, line_params):
    max_distance = 0
    furthest_point = None
    for i in range(len(points)):
        circle_point = (int(points[i]["x"] * IMG_WIDTH), int(points[i]["y"] * IMG_HEIGHT))
        distance = distance_from_line(circle_point, line_params["Big rect. left main"])
        if distance > max_distance:
            max_distance = distance
            furthest_point = circle_point
    if furthest_point:
        intersections.append({
            "lines": ["Big rect. left main", "Circle left"],
            "point": {"x": furthest_point[0], "y": furthest_point[1]}
        })
        # cv2.circle(image_cv, furthest_point, 10, (255, 255, 0), -1)

def are_three_or_more_collinear(points):
    if len(points) < 3:
        return False
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            for k in range(j + 1, len(points)):
                (x1, y1), (x2, y2), (x3, y3) = points[i], points[j], points[k]
                if (y2 - y1) * (x3 - x2) == (y3 - y2) * (x2 - x1):
                    return True
    return False

def total_distance(points):
    dist = 0
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            dist += np.linalg.norm(points[i] - points[j])
    return dist

def select_points(src_points, dst_points):
    if len(src_points) < 4 or len(dst_points) < 4:
        return None, None

    n = len(src_points)
    max_dist = -1
    best_combination = None

    for indices in combinations(range(n), 4):
        selected_src_points = [src_points[i] for i in indices]
        selected_dst_points = [dst_points[i] for i in indices]
        
        if not are_three_or_more_collinear(selected_dst_points):
            dist = total_distance(selected_dst_points)
            if dist > max_dist:
                max_dist = dist
                best_combination = (selected_src_points, selected_dst_points)
    
    if best_combination is None:
        return None, None

    selected_src_points, selected_dst_points = best_combination
    return np.array(selected_src_points, dtype=np.float32), np.array(selected_dst_points, dtype=np.float32)


def points_circle_center_to_side_line(data):
    circle_right = None
    circle_left = None
    big_rect_right = None
    big_rect_left = None
    
    for entry in data:
        if 'Big rect. right main' in entry['lines'] and 'Big rect. right top' in entry['lines']:
            big_rect_right = entry['point']
        if 'Big rect. left main' in entry['lines'] and 'Big rect. left top' in entry['lines']:
            big_rect_left = entry['point']
        if 'Middle line right' in entry['lines']:
            circle_right = entry['point']
        if "Middle line left" in entry['lines']:
            circle_left = entry['point']

    return big_rect_right, big_rect_left, circle_right, circle_left

def presume_side_intersection(big_rect, circle, direction, intersections, line_params, IMG_WIDTH, IMG_HEIGHT):
    if big_rect and circle:
        big_rect_tmp = {
            'x': big_rect['x'] / IMG_WIDTH,
            'y': big_rect['y'] / IMG_HEIGHT
        }
        circle_tmp = {
            'x': circle['x'] / IMG_WIDTH,
            'y': circle['y'] / IMG_HEIGHT
        }
        m, c = compute_line_params(big_rect_tmp, circle_tmp, IMG_WIDTH, IMG_HEIGHT)
        line_key = f"big_rect_{direction}, circle_{direction}"
        line_params[line_key] = (m, c)
        base_intersection = find_intersection(line_params[line_key], line_params["Side line top"])
        intersections.append({
            "lines": [f"Side line {direction}", "Side line top"],
            "point": {"x": base_intersection[0], "y": base_intersection[1]}
        })

        point_a = None
        point_b = None

        for intersection in intersections:
            if set(intersection['lines']) == {f"Big rect. {direction} main", "Side line top"}:
                point_a = intersection['point']
            elif set(intersection['lines']) == {f"Big rect. {direction} main", f"Big rect. {direction} top"}:
                point_b = intersection['point']

        if point_a and point_b:
            vector = (point_b['x'] - point_a['x'], point_b['y'] - point_a['y'])
            new_intersection_x = base_intersection[0] + vector[0]
            new_intersection_y = base_intersection[1] + vector[1]

            new_intersection = (new_intersection_x, new_intersection_y)
            intersections.append({
                "lines": [f"Side line {direction}", f"Big rect. {direction} top"],
                "point": {"x": new_intersection[0], "y": new_intersection[1]}
            })


# 수평선 중 기울기가 너무 다르면 제외
def slope_diff_in_degrees(slope1, slope2):
    return abs(math.degrees(math.atan(slope1)) - math.degrees(math.atan(slope2)))


def presume_rect_half(intersections, line_key, side_line_key, big_rect_line_key, line_params):
    if side_line_key not in line_params or big_rect_line_key not in line_params:
        return

    side_line_top = line_params[side_line_key]
    big_rect_line = line_params[big_rect_line_key]
    middle_point = None
    for intersection in intersections:
        if line_key in intersection['lines']:
            middle_point = intersection['point']
            break

    if side_line_top and big_rect_line and middle_point:
        m = side_line_top[0]
        c = middle_point['y'] - m * middle_point['x']

        line_params[big_rect_line_key + " center"] = (m, c)

        intersection_point = find_intersection(big_rect_line, line_params[big_rect_line_key + " center"])

        intersections.append({
            "lines": [big_rect_line_key, "half"],
            "point": {"x": intersection_point[0], "y": intersection_point[1]}
        })

        
def presume_side_bottom_intersection(intersections, top_line_key, middle_line_key, middle_line_intersection_key, circle_intersection_key, side_line_bottom_key, line_params, IMG_WIDTH, IMG_HEIGHT):
    side_line_top = middle_left = None

    for intersection in intersections:
        if top_line_key in intersection['lines'] and middle_line_key in intersection['lines']:
            side_line_top = intersection['point']
        if middle_line_intersection_key in intersection['lines'] and circle_intersection_key in intersection['lines']:
            middle_left = intersection['point']

    if side_line_bottom_key in line_params:
        side_line_bottom = line_params[side_line_bottom_key]
    else:
        side_line_bottom = None

    if side_line_top and middle_left and side_line_bottom:
        side_line_top_x = side_line_top['x'] / IMG_WIDTH
        side_line_top_y = side_line_top['y'] / IMG_HEIGHT
        middle_left_x = middle_left['x'] / IMG_WIDTH
        middle_left_y = middle_left['y'] / IMG_HEIGHT

        m, c = compute_line_params({'x': side_line_top_x, 'y': side_line_top_y}, {'x': middle_left_x, 'y': middle_left_y}, IMG_WIDTH, IMG_HEIGHT)
        line_params["Side top to circle left"] = (m, c)
        intersection = find_intersection(line_params["Side top to circle left"], side_line_bottom)
        intersections.append({
            "lines": [side_line_bottom_key, middle_line_intersection_key],
            "point": {"x": intersection[0], "y": intersection[1]}
        })