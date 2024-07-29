import numpy as np

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

# Function to find intersection of two lines
def find_intersection(m1, c1, m2, c2):
    if m1 == m2:
        return None  # Parallel lines
    if m1 is None:  # First line is vertical
        x = c1
        y = m2 * x + c2
    elif m2 is None:  # Second line is vertical
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

# 3개 이상 안 겹치게 하기
def select_points(src_points, dst_points):
    x_values = [x for x, y in src_points]
    y_values = [y for x, y in src_points]

    # Find indices for max and min x values
    max_x_idx = np.argmax(x_values)
    min_x_idx = np.argmin(x_values)

    # Find indices for max and min y values
    y_values[max_x_idx] = -np.inf
    y_values[min_x_idx] = -np.inf
    max_y_idx = np.argmax(y_values)
    y_values[max_x_idx] = np.inf
    y_values[min_x_idx] = np.inf
    min_y_idx = np.argmin(y_values)

    # Selected src_points and dst_points
    selected_indices = [max_x_idx, min_x_idx, max_y_idx, min_y_idx]
    selected_src_points = [
        src_points[max_x_idx],
        src_points[min_x_idx],
        src_points[max_y_idx],
        src_points[min_y_idx]
    ]

    selected_dst_points = [
        dst_points[max_x_idx],
        dst_points[min_x_idx],
        dst_points[max_y_idx],
        dst_points[min_y_idx]
    ]

    # Function to check if there are three or more identical x or y coordinates
    def has_three_or_more_identical_coordinates(points):
        x_counts = np.bincount([x for x, y in points])
        y_counts = np.bincount([y for x, y in points])
        return max(x_counts) >= 3 or max(y_counts) >= 3

    # Check and adjust selected_dst_points if necessary
    if has_three_or_more_identical_coordinates(selected_dst_points):
        remaining_indices = set(range(len(dst_points))) - set(selected_indices)
        for i, point in enumerate(selected_dst_points):
            for idx in remaining_indices:
                temp_points = selected_dst_points.copy()
                temp_points[i] = dst_points[idx]
                if not has_three_or_more_identical_coordinates(temp_points):
                    selected_dst_points[i] = dst_points[idx]
                    selected_src_points[i] = src_points[idx]  # Update the corresponding src point
                    selected_indices[i] = idx  # Update the index
                    break
            if not has_three_or_more_identical_coordinates(selected_dst_points):
                break

    return np.array(selected_src_points, dtype=np.float32), np.array(selected_dst_points, dtype=np.float32)