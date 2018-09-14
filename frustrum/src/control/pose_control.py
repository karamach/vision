import math
import datetime

from utils.geometry import Geometry
from scipy.spatial import ConvexHull
import numpy as np

from model.inters import Inters

class CameraTransControl(object):

    def __init__(self, camera, pos_idx, callback):
        self.camera = camera
        self.callback = callback
        self.pos_idx = pos_idx

    def update(self, val):
        ypr = self.camera.getYPR()
        xyz = self.camera.getXYZ()
        xyz[self.pos_idx] = val
        self.camera.pose(ypr, xyz)
        if self.callback:
            self.callback()

class CameraRotControl(object):

    def __init__(self, camera, angle_idx, callback):
        self.camera = camera
        self.callback = callback
        self.angle_idx = angle_idx

    def update(self, val):
        ypr = self.camera.getYPR()
        xyz = self.camera.getXYZ()
        ypr[self.angle_idx] = math.radians(val)
        self.camera.pose(ypr, xyz)
        if self.callback:
            self.callback()
