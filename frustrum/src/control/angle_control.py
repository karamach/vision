import math
from utils.geometry import Geometry
from scipy.spatial import ConvexHull
import numpy as np
import datetime

from model.inters import Inters

class CameraAngleControl(object):

    def __init__(self, camera, angle_idx, callback):
        self.camera = camera
        self.callback = callback
        self.angle_idx = angle_idx

    def update(self, val):
        if self.angle_idx == 0: self.camera.h_ang = val
        else: self.camera.v_ang = val
        self.camera.pose([0, 0, 0],  [0, 0, 0])
        if self.callback:
            self.callback()
                        
