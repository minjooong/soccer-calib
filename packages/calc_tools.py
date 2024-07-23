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