import numpy as np

class SoccerPitch:
    """Static class variables that are specified by the rules of the game """
    GOAL_LINE_TO_PENALTY_MARK = 11.0
    PENALTY_AREA_WIDTH = 40.32
    PENALTY_AREA_LENGTH = 16.5
    GOAL_AREA_WIDTH = 18.32
    GOAL_AREA_LENGTH = 5.5
    CENTER_CIRCLE_RADIUS = 9.15
    GOAL_HEIGHT = 2.44
    GOAL_LENGTH = 7.32

    lines_classes = [
        'Big rect. left bottom',
        'Big rect. left main',
        'Big rect. left top',
        'Big rect. right bottom',
        'Big rect. right main',
        'Big rect. right top',
        'Circle central',
        'Circle left',
        'Circle right',
        'Goal left crossbar',
        'Goal left post left ',
        'Goal left post right',
        'Goal right crossbar',
        'Goal right post left',
        'Goal right post right',
        'Goal unknown',
        'Line unknown',
        'Middle line',
        'Side line bottom',
        'Side line left',
        'Side line right',
        'Side line top',
        'Small rect. left bottom',
        'Small rect. left main',
        'Small rect. left top',
        'Small rect. right bottom',
        'Small rect. right main',
        'Small rect. right top'
    ]

    symetric_classes = {
        'Side line top': 'Side line bottom',
        'Side line bottom': 'Side line top',
        'Side line left': 'Side line right',
        'Middle line': 'Middle line',
        'Side line right': 'Side line left',
        'Big rect. left top': 'Big rect. right bottom',
        'Big rect. left bottom': 'Big rect. right top',
        'Big rect. left main': 'Big rect. right main',
        'Big rect. right top': 'Big rect. left bottom',
        'Big rect. right bottom': 'Big rect. left top',
        'Big rect. right main': 'Big rect. left main',
        'Small rect. left top': 'Small rect. right bottom',
        'Small rect. left bottom': 'Small rect. right top',
        'Small rect. left main': 'Small rect. right main',
        'Small rect. right top': 'Small rect. left bottom',
        'Small rect. right bottom': 'Small rect. left top',
        'Small rect. right main': 'Small rect. left main',
        'Circle left': 'Circle right',
        'Circle central': 'Circle central',
        'Circle right': 'Circle left',
        'Goal left crossbar': 'Goal right crossbar',
        'Goal left post left ': 'Goal right post left',
        'Goal left post right': 'Goal right post right',
        'Goal right crossbar': 'Goal left crossbar',
        'Goal right post left': 'Goal left post left ',
        'Goal right post right': 'Goal left post right',
        'Goal unknown': 'Goal unknown',
        'Line unknown': 'Line unknown'
    }

    # RGB values
    palette = {
        'Big rect. left bottom': (127, 0, 0),
        'Big rect. left main': (102, 102, 102),
        'Big rect. left top': (0, 0, 127),
        'Big rect. right bottom': (86, 32, 39),
        'Big rect. right main': (48, 77, 0),
        'Big rect. right top': (14, 97, 100),
        'Circle central': (0, 0, 255),
        'Circle left': (255, 127, 0),
        'Circle right': (0, 255, 255),
        'Goal left crossbar': (255, 255, 200),
        'Goal left post left ': (165, 255, 0),
        'Goal left post right': (155, 119, 45),
        'Goal right crossbar': (86, 32, 139),
        'Goal right post left': (196, 120, 153),
        'Goal right post right': (166, 36, 52),
        'Goal unknown': (0, 0, 0),
        'Line unknown': (0, 0, 0),
        'Middle line': (255, 255, 0),
        'Side line bottom': (255, 0, 255),
        'Side line left': (0, 255, 150),
        'Side line right': (0, 230, 0),
        'Side line top': (230, 0, 0),
        'Small rect. left bottom': (0, 150, 255),
        'Small rect. left main': (254, 173, 225),
        'Small rect. left top': (87, 72, 39),
        'Small rect. right bottom': (122, 0, 255),
        'Small rect. right main': (255, 255, 255),
        'Small rect. right top': (153, 23, 153)
    }