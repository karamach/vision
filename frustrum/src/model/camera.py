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
        self.last_xyz = [0, 0, 0]
        self.last_ypr = [0, 0, 0]

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
        print('TRANFORM -- \n', self.transform)
        min_f = [np.dot(self.transform, p) for p in self.min_frust]
        max_f = [np.dot(self.transform, p) for p in self.max_frust]        
        return min_f, max_f

    def getAxesPoints(self):
        return [np.dot(self.transform, p) for p in self.axes_points]

    def getXYZ(self):
        return P.xyz(self.transform)

    def getYPR(self):
        return P.ypr(self.transform)

    def setLast(self, ypr, xyz):
        self.last_ypr = ypr
        self.last_xyz = xyz
    
    def pose(self, ypr, xyz):
        self.setLast(ypr, xyz)
        self.transform = np.dot(P.transform(ypr, xyz, False), self.transform)
        self.unit_frust = Camera._update_unitfrust(self.h_ang, self.v_ang)
        self.min_frust, self.max_frust = Camera._update_frust(self.frust_range, self.unit_frust)
        self.axes_points = Camera._update_axes_points(self.frust_range)

    # gps_data = [viewid, pitch, roll, yaw, x, y, z]
    # intrinsics = [fx, fy, h, w]
    @staticmethod    
    def load_cameras_gps(intrinsics, gps_data, fov_dist, active_views=None):

        # NED :  north(X)-east(Y)-down(Z)
        #        Standing on origin facing X, Yaw(L to R about Z), Pitch(Down to Up about Y), Roll(L to R about X)
        # ENU :  east(X)-north(Y)-up(Z)
        #        Standing on origin facing X, Yaw(R to L about Z), Pitch(Up to Down about Y), Roll(L to R about X)
        def ned2enu(ypr):
            [yaw, pitch, roll] = ypr
            return [90-yaw if -90 <= yaw<= 180 else -(270+yaw), -pitch, roll]

        def create_camera(view_id, fx, fy, h, w, ypr, xyz, d):
            [yaw, pitch, roll] = ypr
            h_ang = 2*math.atan(1/(2*fx))
            v_ang = h_ang*h/w
            angs = [h_ang, v_ang]
            frust_range = [1, d]
            ypr = [90-yaw if -90 <= yaw<= 180 else -(270+yaw), -pitch, roll]
            xyz = xyz
            camera = Camera(frust_range, angs, view_id=int(view_id))
            camera.setLast([math.radians(a) for a in ypr], xyz)            
            camera.pose(camera.last_ypr, camera.last_xyz)
            return camera
        
        def mean(vals):
            return sum(vals)/len(vals)

        print('[decimal_view_poses ..]', gps_data)
        
        means_input = gps_data
        means = [
            mean([g[idx] for g in means_input])
            for idx in [1, 2, 3]
        ]

        print('means = ', means)
        cameras = [create_camera(int(r[0]), *intrinsics, r[4:],  GPSUtils.convert_latlon_cartesian(*r[1:4], *means), fov_dist) for r in gps_data]
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
