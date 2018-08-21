import math
import numpy as np

from geometry import Geometry as G
from geometry import Pose as P

class Camera(object):

    def __init__(self, frust_range, angs, color='black'):
        self.origin = [0, 0, 0]
        self.h_ang = angs[0]
        self.v_ang = angs[1]
        self.color = color
        self.unit_frust = Camera._update_unitfrust(self.h_ang, self.v_ang)
        self.frust_range = frust_range
        self.axes_points = [
            [self.frust_range[0], 0, 0],
            [0, self.frust_range[0], 0],
            [0, 0, self.frust_range[0]],            
        ]
        self.min_frust, self.max_frust = Camera._update_frust(self.frust_range, self.unit_frust)

        self.curr_axes_points = self.axes_points
        self.curr_origin = self.origin
        self.curr_min_frust = self.min_frust
        self.curr_max_frust = self.max_frust

        self.curr_ypr = [0, 0, 0]
        self.curr_xyz = [0, 0, 0]

    @staticmethod
    def _update_unitfrust(h_ang, v_ang):
        h_ang, v_ang = math.radians(h_ang), math.radians(v_ang)
        return np.array([
            [1, math.tan(h_ang/2), math.tan(v_ang/2)],
            [1, -math.tan(h_ang/2), math.tan(v_ang/2)],
            [1, -math.tan(h_ang/2), -math.tan(v_ang/2)],
            [1, math.tan(h_ang/2), -math.tan(v_ang/2)],
        ])
        
    @staticmethod
    def _update_frust(frust_range, unit_frust):
        min_frust = [frust_range[0]*p for p in unit_frust]
        max_frust = [frust_range[1]*p for p in unit_frust]
        return min_frust, max_frust

    @staticmethod
    def _update_axes_points(frust_range):
        return [
            [frust_range[0], 0, 0],
            [0, frust_range[0], 0],
            [0, 0, frust_range[0]],            
        ]
                
    def pose(self, ypr, xyz):
        self.unit_frust = Camera._update_unitfrust(self.h_ang, self.v_ang)
        self.min_frust, self.max_frust = Camera._update_frust(self.frust_range, self.unit_frust)
        [o, min_f, max_f] = [self.origin, self.min_frust, self.max_frust]
        [o], min_f, max_f = P.rot([o], ypr), P.rot(min_f, ypr), P.rot(max_f, ypr)
        [o], min_f, max_f =  P.trans([o], xyz), P.trans(min_f, xyz),  P.trans(max_f, xyz)
        
        self.axes_points = Camera._update_axes_points(self.frust_range)
        a_points = [P.rot([p], ypr)[0] for p in self.axes_points]
        a_points = [P.trans([p], xyz)[0] for p in a_points]
        
        self.curr_axes_points = a_points
        self.curr_origin, self.curr_min_frust, self.curr_max_frust = o, min_f, max_f
        self.curr_ypr, self.curr_xyz = ypr, xyz
        return o, min_f, max_f

    def __str__(self):
        out = '-' * 25
        out += '\norigin=%s\nh_ang=%s\nv_ang=%s\ncolor=%s\n'
        out += 'unit_frust=%s\nfrust_range=%s\nmin_frust=%s\n'
        out += 'max_frust=%s\ncurr_origin=%s\ncurr_min_frust=%s\n'
        out += 'curr_max_frust=%s\ncurr_ypr=%s\ncurr_xyz=%s\n'
        return out % (
            self.origin, self.h_ang, self.v_ang, self.color,
            self.unit_frust, self.frust_range, self.min_frust,
            self.max_frust, self.curr_origin, self.curr_min_frust,
            self.curr_max_frust, self.curr_ypr, self.curr_xyz
        )
        
class Inters:

    def __init__(self):
        self.reset()

    def reset(self):
        self.points = []
        self.hull = None
        self.score = 0
        self.state = False
        self.frust_union_volume = 0

def create_model():
    def rads(angles):
        return [math.radians(a) for a in angles]
    
    colors = ['magenta', 'cyan']
    frust = [[0, 0], [0, 0]]
    angs = [
        [math.radians(0), math.radians(0)],
        [math.radians(0), math.radians(0)]
    ]
    cameras = [
        Camera(frust_range, angs, color)
        for frust_range, angs, color in zip(frust, angs, colors)
    ]
    inters = Inters()
    return cameras, inters    
    
        
