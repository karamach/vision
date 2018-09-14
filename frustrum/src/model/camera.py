import math
import numpy as np

from utils.geometry import Geometry as G
from utils.pose import Pose as P
from utils.utils import GPSUtils

class Camera(object):

    view_cameras = {}
    view_ids = []

    def __init__(self, frust_range, angs, color='black', view_id=0):
        self.view_id = view_id
        self.origin = [0, 0, 0, 1]
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
        c_ypr, c_xyz = P.ypr(self.transform), P.xyz(self.transform)
        ypr = [a1-a2 for a1, a2 in zip(ypr, c_ypr)]
        xyz = [p1-p2 for p1, p2 in zip(xyz, c_xyz)]
        
        self.transform = np.dot( P.transform(ypr, xyz), self.transform)
        self.unit_frust = Camera._update_unitfrust(self.h_ang, self.v_ang)
        self.min_frust, self.max_frust = Camera._update_frust(self.frust_range, self.unit_frust)
        self.axes_points = Camera._update_axes_points(self.frust_range)
        
    def pose1(self, ypr, xyz, scale=1):
   
        self.unit_frust = Camera._update_unitfrust(self.h_ang, self.v_ang)
        self.min_frust, self.max_frust = Camera._update_frust(self.frust_range, self.unit_frust)
        
        [o, min_f, max_f] = [self.origin, self.min_frust, self.max_frust]
        #[o, min_f, max_f] = [self.curr_origin, self.curr_min_frust, self.curr_max_frust]
        [o], min_f, max_f = P.rot([o], ypr), P.rot(min_f, ypr), P.rot(max_f, ypr)
        [o], min_f, max_f =  P.trans([o], xyz), P.trans(min_f, xyz),  P.trans(max_f, xyz)
        
        self.axes_points = Camera._update_axes_points(self.frust_range)
        a_points = [P.rot([p], ypr)[0] for p in self.axes_points]
        a_points = [P.trans([p], xyz)[0] for p in a_points]
        
        self.curr_axes_points = a_points
        self.curr_origin, self.curr_min_frust, self.curr_max_frust = o, min_f, max_f
        self.curr_ypr, self.curr_xyz = ypr, xyz
        
        return o, min_f, max_f

    def pose_str(self):
        return '%s,%s;%s' % (self.view_id, str(self.curr_origin), str([math.degrees(a) for a in self.curr_ypr]))
        
    def __str__(self):
        out = '-' * 25
        out += '\nview_id=%s\norigin=%s\nh_ang=%s\nv_ang=%s\ncolor=%s\n'
        out += 'unit_frust=%s\nfrust_range=%s\nmin_frust=%s\n'
        out += 'max_frust=%s\ncurr_origin=%s\ncurr_min_frust=%s\n'
        out += 'curr_max_frust=%s\ncurr_ypr=%s\ncurr_xyz=%s\n'
        return out % (self.view_id,
            self.origin, self.h_ang, self.v_ang, self.color,
            self.unit_frust, self.frust_range, self.min_frust,
            self.max_frust, self.curr_origin, self.curr_min_frust,
            self.curr_max_frust, self.curr_ypr, self.curr_xyz
        )

    @staticmethod
    def load_cameras_gps(intrinsics, gps_data, fov_dist):

        def create_camera(view_id, fx, fy, h, w, pitch, roll, yaw, x, y, z, d):
            h_ang = 2*math.atan(1/(2*fx))
            v_ang = h_ang*h/w
            angs = [h_ang, v_ang]
            frust_range = [1, d]
            ypr = [90-yaw if -90 <= yaw<= 180 else -(270+yaw), -pitch, roll]
            xyz = [x, y, z]
            camera = Camera(frust_range, angs, view_id=int(view_id))
            camera.pose([math.radians(a) for a in ypr], xyz)
            return camera
        
        def mean(vals):
            return sum(vals)/len(vals)
        
        means = mean([g[4] for g in gps_data]), mean([g[5] for g in gps_data]), mean([g[6] for g in gps_data])
        gps_data = [g[:4] + GPSUtils.convert_latlon_cartesian(*g[4:], *means) for g in gps_data]
        cameras = [create_camera(int(r[0]), *intrinsics, *r[1:],  fov_dist) for r in gps_data]
        Camera.view_cameras = dict([(c.view_id, c) for c in cameras])
        Camera.view_ids = [c.view_id for c in cameras]
        return Camera.view_cameras
        
    @staticmethod
    def load_cameras_solve(intrinsics, solve_pose_data, fov_dist, orientation, origin, scale):

        def create_camera(view_id, fx, fy, h, w, yaw, pitch, roll, x, y, z, d, origin, scale):
            h_ang = 2*math.atan(1/(2*fx))
            v_ang = h_ang*h/w
            angs = [h_ang, v_ang]
            frust_range = [1, d]
            ypr = [yaw, pitch, roll]
            xyz = [x, y, z]
            camera = Camera(frust_range, angs, view_id=int(view_id))
            print(camera.view_id)
            print('before solve  pose .. ', camera.curr_origin)
            camera.pose([0, 0, 0], xyz)
            print('after solve pose .. ', camera.curr_origin, xyz)
            camera.pose(ypr, [0, 0, 0])
            print('after sim  rot .. ', camera.curr_origin, ypr)
            return camera

        cameras = [create_camera(int(r[0]), *intrinsics, *orientation, *r[1],  fov_dist, origin, 1) for r in solve_pose_data]
        Camera.view_cameras = dict([(c.view_id, c) for c in cameras])
        Camera.view_ids = [c.view_id for c in cameras]
        return Camera.view_cameras
