import math
from geometry import Geometry
from scipy.spatial import ConvexHull
import numpy as np
import datetime

from model.inters import Inters

class CameraFrustControl(object):

    def __init__(self, camera, frust_idx, callback):
        self.camera = camera
        self.callback = callback
        self.frust_idx = frust_idx

    def update(self, val):
        self.camera.frust_range[self.frust_idx] = val
        self.camera.pose(self.camera.curr_ypr,  self.camera.curr_xyz)
        self.callback()
