import math
from geometry import Geometry
from scipy.spatial import ConvexHull
import numpy as np
from model import Inters
import datetime

class ResetControl:

    def __init__(self, cameras, inters, callback):
        self.cameras = cameras
        self.inters = inters
        self.callback = callback
        self.score = 0
        
