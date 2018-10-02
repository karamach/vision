import math
import numpy as np

from utils.geometry import Geometry as G
from utils.pose import Pose as P
from utils.utils import GPSUtils

class Camera(object):

    view_cameras = {}
    view_ids = []

    def __init__(self, frust_range, angs, view_id=0, xyz=[0, 0, 0, 1], color='black', means = []):
        self.view_id = view_id
        self.origin = xyz
        self.h_ang = angs[0]
        self.v_ang = angs[1]
        self.color = color
        self.unit_frust = Camera._update_unitfrust(self.h_ang, self.v_ang)
        self.frust_range = frust_range
        self.axes_points = [
            [self.frust_range[0], 0, 0, 1],
            [0, self.frust_range[0], 0, 1],
            [0, 0, self.frust_range[0], 1],            
        ]
        self.min_frust, self.max_frust = Camera._update_frust(self.frust_range, self.unit_frust)
        self.transform = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1 ]])

    @staticmethod
    def getNextViewId(view_id):
        idx = Camera.view_ids.index(view_id)        
        return Camera.view_ids[0] if idx == len(Camera.view_ids)-1 else Camera.view_ids[idx+1]        
        
    @staticmethod
    def _update_unitfrust(h_ang, v_ang):
        h_ang, v_ang = h_ang, v_ang
        return np.array([
            [1, math.tan(h_ang/2), math.tan(v_ang/2)],
            [1, -math.tan(h_ang/2), math.tan(v_ang/2)],
            [1, -math.tan(h_ang/2), -math.tan(v_ang/2)],
            [1, math.tan(h_ang/2), -math.tan(v_ang/2)],
        ])
        
    @staticmethod
    def _update_frust(frust_range, unit_frust):
        min_frust = np.array([frust_range[0]*p for p in unit_frust])
        max_frust = np.array([frust_range[1]*p for p in unit_frust])
        min_frust = np.column_stack((min_frust, [1, 1, 1, 1]))
        max_frust = np.column_stack((max_frust, [1, 1, 1, 1]))
        return min_frust, max_frust

    @staticmethod
    def _update_axes_points(frust_range):
        return [
            [frust_range[0], 0, 0, 1],
            [0, frust_range[0], 0, 1],
            [0, 0, frust_range[0], 1],            
        ]

    def getOrigin(self):
        return np.dot(self.transform, self.origin)

    def getFrustums(self):
        min_f = [np.dot(self.transform, p) for p in self.min_frust]
        max_f = [np.dot(self.transform, p) for p in self.max_frust]        
        return min_f, max_f

    def getAxesPoints(self):
        return [np.dot(self.transform, p) for p in self.axes_points]

    def getXYZ(self):
        return P.xyz(self.transform)

    def getYPR(self):
        return P.ypr(self.transform)
    
    def pose(self, ypr, xyz):
        self.transform = np.dot(P.transform(ypr, xyz), self.transform)
        self.unit_frust = Camera._update_unitfrust(self.h_ang, self.v_ang)
        self.min_frust, self.max_frust = Camera._update_frust(self.frust_range, self.unit_frust)
        self.axes_points = Camera._update_axes_points(self.frust_range)

    # gps_data = [viewid, pitch, roll, yaw, x, y, z]
    # intrinsics = [fx, fy, h, w]
    @staticmethod    
    def load_cameras_gps(intrinsics, gps_data, fov_dist, active_views=None):

        def create_camera(view_id, fx, fy, h, w, pry, xyz, d):
            [pitch, roll, yaw] = pry
            h_ang = 2*math.atan(1/(2*fx))
            v_ang = h_ang*h/w
            angs = [h_ang, v_ang]
            frust_range = [1, d]
            ypr = [90-yaw if -90 <= yaw<= 180 else -(270+yaw), -pitch, roll]
            xyz = xyz
            camera = Camera(frust_range, angs, view_id=int(view_id))
            camera.pose([math.radians(a) for a in ypr], xyz)
            return camera
        
        def mean(vals):
            return sum(vals)/len(vals)

        means_input = list(filter(lambda r: int(r[0]) in set(active_views), gps_data)) if active_views else gps_data
        means = [
            mean([g[idx] for g in means_input])
            for idx in [4, 5, 6]
        ]
                                                             
        cameras = [create_camera(int(r[0]), *intrinsics, r[1:4],  GPSUtils.convert_latlon_cartesian(*r[4:7], *means), fov_dist) for r in gps_data]
        Camera.view_cameras = dict([(c.view_id, c) for c in cameras])
        Camera.view_ids = [c.view_id for c in cameras]
        return Camera.view_cameras
        
    @staticmethod
    def load_cameras_solve(intrinsics, solve_pose_data, fov_dist, orientation, origin, scale):

        def create_camera(view_id, fx, fy, h, w, ypr, xyz, d, orientation, origin, scale):
            h_ang = 2*math.atan(1/(2*fx))
            v_ang = h_ang*h/w
            angs = [h_ang, v_ang]
            frust_range = [1, d]
            xyzw = xyz + [1]

            # meaningless transform
            xyzw = P.rot(xyzw, ypr, True)
            
            #xyzw = P.houdini_rpytransform(xyzw, origin, orientation, scale)
            #xyzw = P.curr_pretransform(xyzw, origin, orientation, scale)
            xyzw = P.sim_transform(xyzw, origin, orientation, scale)
            camera = Camera(frust_range, angs, int(view_id), xyzw)
            
            return camera
        
        # r[2] is in the format x, y, z, w 
        cameras = [create_camera(int(r[0]), *intrinsics, P.q2ypr(*r[2]), r[1],  fov_dist, orientation, origin,  scale) for r in solve_pose_data]
        Camera.view_cameras = dict([(c.view_id, c) for c in cameras])
        Camera.view_ids = [c.view_id for c in cameras]
        return Camera.view_cameras
