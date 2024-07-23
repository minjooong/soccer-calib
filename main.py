# import cv2
# import numpy as np
# import torch
# import torchvision.transforms as T
# from PIL import Image

# from pathlib import Path
# from torchvision.models.segmentation import deeplabv3_resnet101
# from typing import Union
from packages.utils_calibration import SoccerPitch

import json

import packages.calc_tools as ct

# IMG_PATH = Path('./sample_data')
# SPLIT_PATH = Path('example')
# OUT_PATH = Path('./outputs')
# CHECKPOINT_PATH = Path('../train_59.pt')
# JSON_PATH = Path('./outputs/np2_nc2_r4_md30')

IMG_WIDTH = 1920
IMG_HEIGHT = 1080

lines_palette = [0, 0, 0]
for line_class in SoccerPitch.lines_classes:
    lines_palette.extend(SoccerPitch.palette[line_class])

with open('coordinates.json', 'r') as f:
  coordinates_data = json.load(f)

import os
os.system("streamlit run ./packages/line_extremities.py")

