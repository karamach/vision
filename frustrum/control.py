import math
from geometry import Geometry
from scipy.spatial import ConvexHull

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
        self.camera.pose( self.camera.curr_ypr,  self.camera.curr_xyz)
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
        points = Geometry.frustrum_intersect(c1_f, c2_f)
        if points:
            print('[ok][found intersections ..]')
            self.inters.points = points
            self.inters.hull = ConvexHull(np.array(self.inters.points))
            self.inters.score = self.inters.hull.volume / (Geometry.get_frustrum_volume(c1_f) + Geometry.get_frustrum_volume(c2_f))
        else:
            print('[ok][no intersections ..]')            
        self.callback()
