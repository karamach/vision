import math
from geometry import Geometry
from scipy.spatial import ConvexHull
import numpy as np
from model import Inters
import datetime

class CameraTransControl(object):

    def __init__(self, camera, pos_idx, callback):
        self.camera = camera
        self.callback = callback
        self.pos_idx = pos_idx

    def update(self, val):
        xyz = self.camera.curr_xyz
        xyz[self.pos_idx] = val
        self.camera.pose(self.camera.curr_ypr, xyz)
        self.callback()

class CameraRotControl(object):

    def __init__(self, camera, angle_idx, callback):
        self.camera = camera
        self.callback = callback
        self.angle_idx = angle_idx

    def update(self, val):
        ypr = self.camera.curr_ypr
        ypr[self.angle_idx] = math.radians(val)
        self.camera.pose(ypr, self.camera.curr_xyz)
        self.callback()

class CameraFrustControl(object):

    def __init__(self, camera, frust_idx, callback):
        self.camera = camera
        self.callback = callback
        self.frust_idx = frust_idx

    def update(self, val):
        self.camera.frust_range[self.frust_idx] = val
        self.camera.pose(self.camera.curr_ypr,  self.camera.curr_xyz)
        self.callback()

class CameraAngleControl(object):

    def __init__(self, camera, angle_idx, callback):
        self.camera = camera
        self.callback = callback
        self.angle_idx = angle_idx

    def update(self, val):
        if self.angle_idx == 0: self.camera.h_ang = val
        else: self.camera.v_ang = val
        self.camera.pose(self.camera.curr_ypr,  self.camera.curr_xyz)
        self.callback()
                        
class IntersControl:

    def __init__(self, cameras, inters, callback):
        self.cameras = cameras
        self.inters = inters
        self.callback = callback
        self.score = 0
    
    def update(self, val):
        c1_f = self.cameras[0].curr_min_frust + self.cameras[0].curr_max_frust
        c2_f = self.cameras[1].curr_min_frust + self.cameras[1].curr_max_frust
        start = datetime.datetime.now()            
        points = Geometry.frustrum_intersect(c1_f, c2_f)
        end = datetime.datetime.now()
        print('intersection_compute_time=%s' % (end-start))        
        if not points:
            print('[ok][no intersections ..]')
            self.inters.reset()
            self.callback()
            return
            
        print('[ok][found intersections ..]')
        self.inters.points = points
        self.inters.hull = ConvexHull(np.array(self.inters.points))
        l1 = abs(self.cameras[0].frust_range[1] - self.cameras[0].frust_range[0])
        l2 = abs(self.cameras[1].frust_range[1] - self.cameras[0].frust_range[0])
        self.inters.frust_union_volume =  float(Geometry.get_frustrum_volume(c1_f, l1)) + float(Geometry.get_frustrum_volume(c2_f, l2)) - float(self.inters.hull.volume)
        self.inters.score = self.inters.hull.volume / self.inters.frust_union_volume
        self.callback()

class ResetControl:

    def __init__(self, cameras, inters, callback):
        self.cameras = cameras
        self.inters = inters
        self.callback = callback
        self.score = 0
        
