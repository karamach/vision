#from geometry_py import PnPoint, PnFrustum, PnPointList

import datetime

from scipy.spatial import ConvexHull
from scipy.spatial.qhull import QhullError
import numpy as np
from model.camera import Camera

from utils.geometry import Geometry

class IntersControl:

    def __init__(self, cameras, inters):
        self.cameras = cameras
        self.inters = inters
        self.use_cpp = False

    def compute_intersection(self, c1_f, c2_f):
        if not self.use_cpp:
            return Geometry.frustrum_intersect(c1_f, c2_f)

        return Geometry.frustrum_intersect(c1_f, c2_f)
        '''
        f1 = PnFrustum(*[PnPoint(*point) for point in c1_f])
        f2 = PnFrustum(*[PnPoint(*point) for point in c2_f])
        pois = PnPointList()
        f1.intersect(f2, pois)
        coords = [[v for v in p.get()] for i, p in enumerate(pois)]
        return coords        
        '''

    def incrementAndUpdate(self, val):
        view_ids = [c.view_id for c in self.inters.active_cameras]
        [id1, id2] = view_ids
        id2 = Camera.getNextViewId(id2)
        id1 = id1 if id2 >= view_ids[1] else Camera.getNextViewId(id1)
        self.inters.active_cameras = [Camera.view_cameras[id1], Camera.view_cameras[id2]]
        if  val:
            self.update()
        
    def update(self, val=None):
        [c1, c2] = self.inters.active_cameras
        c1_f = c1.curr_min_frust + c1.curr_max_frust
        c2_f = c2.curr_min_frust + c2.curr_max_frust
        start = datetime.datetime.now()            
        points = self.compute_intersection(c1_f, c2_f)
        end = datetime.datetime.now()
        print('intersection_compute_time=%s' % (end-start))        
        if not points:
            print('[ok][no intersections ..]')
            self.inters.points = []
            self.inters.score = 0
            return
            
        print('[ok][found intersections ..][points=%s]' % points)
        self.inters.points = points
        l1 = abs(c1.frust_range[1] - c2.frust_range[0])
        l2 = abs(c2.frust_range[1] - c1.frust_range[0])
                   
        try:
            self.inters.hull = ConvexHull(np.array(self.inters.points))
            self.inters.frust_union_volume =  float(Geometry.get_frustrum_volume(c1_f, l1)) + float(Geometry.get_frustrum_volume(c2_f, l2)) - float(self.inters.hull.volume)
            self.inters.score = self.inters.hull.volume / self.inters.frust_union_volume
        except QhullError as e:
            print(e)

    
