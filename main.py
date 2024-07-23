import cv2
import numpy as np
import torch
import torchvision.transforms as T
from PIL import Image
from pathlib import Path
from torchvision.models.segmentation import deeplabv3_resnet101
from typing import Union
from packages.utils_calibration import SoccerPitch

import json

import packages.calc_tool as ct

IMG_PATH = Path('./sample_data')
SPLIT_PATH = Path('example')
OUT_PATH = Path('./outputs')
CHECKPOINT_PATH = Path('../train_59.pt')
JSON_PATH = Path('./outputs/np2_nc2_r4_md30')

IMG_WIDTH = 1920
IMG_HEIGHT = 1080

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

with open('coordinates.json', 'r') as f:
  coordinates_data = json.load(f)

import os
os.system("python ./packages/line_extremities.py")