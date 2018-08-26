import datetime

from scipy.spatial import ConvexHull
from scipy.spatial.qhull import QhullError
import numpy as np

from utils.geometry import Geometry


class IntersControl:

    def __init__(self, cameras, inters, callback):
        self.cameras = cameras
        self.inters = inters
        self.callback = callback

    def update(self, val):
        [c1, c2] = self.inters.active_cameras
        c1_f = c1.curr_min_frust + c1.curr_max_frust
        c2_f = c2.curr_min_frust + c2.curr_max_frust
        start = datetime.datetime.now()            
        points = Geometry.frustrum_intersect(c1_f, c2_f)
        end = datetime.datetime.now()
        print('intersection_compute_time=%s' % (end-start))        
        if not points:
            print('[ok][no intersections ..]')
            self.inters.reset()
            self.callback()
            return
            
        print('[ok][found intersections ..][points=%s]' % points)
        self.inters.points = points
        try:
            self.inters.hull = ConvexHull(np.array(self.inters.points))
        except QhullError as e:
            print(e)
        l1 = abs(c1.frust_range[1] - c2.frust_range[0])
        l2 = abs(c2.frust_range[1] - c1.frust_range[0])
        self.inters.frust_union_volume =  float(Geometry.get_frustrum_volume(c1_f, l1)) + float(Geometry.get_frustrum_volume(c2_f, l2)) - float(self.inters.hull.volume)
        self.inters.score = self.inters.hull.volume / self.inters.frust_union_volume
        if self.callback:
            self.callback()
