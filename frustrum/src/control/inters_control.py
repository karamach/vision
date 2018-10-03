from viewintersection_py import PyPoint3, PyRot3, PyPose3, PyPoint3List, PnPointList, ViewIntersectionOp    

import datetime
import time

from scipy.spatial import ConvexHull
from scipy.spatial.qhull import QhullError
import numpy as np
from model.camera import Camera

from utils.geometry import Geometry

class IntersControl:

    def __init__(self, cameras, inters, use_cpp=False):
        self.cameras = cameras
        self.inters = inters
        self.use_cpp = use_cpp

    def incrementAndUpdate(self, val):
        view_ids = [c.view_id for c in self.inters.active_cameras]
        [id1, id2] = view_ids
        id2 = Camera.getNextViewId(id2)
        id1 = id1 if id2 >= view_ids[1] else Camera.getNextViewId(id1)
        if id1 == len(view_ids):
            return False

        self.inters.active_cameras = [Camera.view_cameras[id1], Camera.view_cameras[id2]]
        if  val:
            self.update()
        return True
        
    def update(self, val=None):
        points = self.compute_intersection()
        self.inters.points = [] if not points else points
        self.inters.score = len(self.inters.points)
        #try:
            #l1 = abs(c1.frust_range[1] - c2.frust_range[0])
            #l2 = abs(c2.frust_range[1] - c1.frust_range[0])
            #self.inters.hull = ConvexHull(np.array(self.inters.points))
            #self.inters.frust_union_volume =  float(Geometry.get_frustrum_volume(c1_f, l1)) + float(Geometry.get_frustrum_volume(c2_f, l2)) - float(self.inters.hull.volume)
            #self.inters.score = self.inters.hull.volume / self.inters.frust_union_volume
        #except QhullError as e:
            #print(e)
            
    def compute_intersection(self):
        [c1, c2] = self.inters.active_cameras
        c1_curr_min_frust, c1_curr_max_frust = c1.getFrustums()
        c2_curr_min_frust, c2_curr_max_frust = c2.getFrustums()
        c1_f = c1_curr_min_frust + c1_curr_max_frust
        c2_f = c2_curr_min_frust + c2_curr_max_frust        
        if not self.use_cpp:
            return Geometry.frustrum_intersect(c1_f, c2_f)

        [f1_points, f2_points] = [PyPoint3List(), PyPoint3List()]
        for p in c1_f:
            f1_points.push_back(PyPoint3(*p[:3]))
        for p in c2_f:
            f2_points.push_back(PyPoint3(*p[:3]))
        [pose1, pose2] = [PyPose3(PyRot3(*c.last_ypr), PyPoint3(*c.last_xyz)) for c in [c1, c2]]

        print('[ok][f1_points ..][val=%s]' % str(list(c1_f)))
        print('[ok][f2_points ..][val=%s]' % str(list(c2_f)))
        
        pois = PnPointList()        
        ViewIntersectionOp.computeIntersection(f1_points, pose1, f2_points, pose2, pois, False)
        return [[v for v in p.get()] for i, p in enumerate(pois)]
            
    def compute_all_intersections(self):
        while self.incrementAndUpdate(True):
            time.sleep(2)
            print('view1=%06d view2=%06d inters_score=%02d' % (self.inters.active_cameras[0].view_id, self.inters.active_cameras[1].view_id, self.inters.score))
            print('----------------------------------------')

            
            
