import math
import numpy as np

from utils import Geometry as G

class Camera(object):

    def __init__(self, frust_range, angs, color='black'):
        self.origin = [0, 0, 0]
        self.h_ang = angs[0]
        self.v_ang = angs[1]
        self.color = color
        self.unit_frust = np.array([
            [1, math.tan(self.h_ang/2), math.tan(self.v_ang/2)],
            [1, -math.tan(self.h_ang/2), math.tan(self.v_ang/2)],
            [1, -math.tan(self.h_ang/2), -math.tan(self.v_ang/2)],
            [1, math.tan(self.h_ang/2), -math.tan(self.v_ang/2)],
        ])
        self.frust_range = frust_range
        self.min_frust, self.max_frust = Camera._update_frust(self.frust_range, self.unit_frust)

        self.curr_origin = self.origin
        self.curr_min_frust = self.min_frust
        self.curr_max_frust = self.max_frust

        self.curr_ypr = [0, 0, 0]
        self.curr_xyz = [0, 0, 0]

    @staticmethod
    def _update_frust(frust_range, unit_frust):
        min_frust = [frust_range[0]*p for p in unit_frust]
        max_frust = [frust_range[1]*p for p in unit_frust]
        return min_frust, max_frust
                
    def pose(self, ypr, xyz):
        self.min_frust, self.max_frust = Camera._update_frust(self.frust_range, self.unit_frust) 
        [o, min_f, max_f] = [self.origin, self.min_frust, self.max_frust]
        [o], min_f, max_f = G.rot([o], ypr), G.rot(min_f, ypr), G.rot(max_f, ypr)
        [o], min_f, max_f =  G.trans([o], xyz), G.trans(min_f, xyz),  G.trans(max_f, xyz)
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
        self.points = []
        self.hull = None
        self.score = 0
