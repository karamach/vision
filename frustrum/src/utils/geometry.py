from sympy.geometry import Line3D, Plane, Segment3D
from sympy import Point3D, intersection, Polygon
import numpy as np
import datetime
from scipy.spatial import ConvexHull
from scipy.spatial.qhull import QhullError
import traceback

from multiprocessing import Pool
from functools import reduce
import traceback

import math
                   
class Geometry:
    
    @staticmethod
    def point_in_polygon(point, rects):

        planes = [Plane(*r[:3]) for r in rects]

        # if the projection of the point on plane is same as plane and point is in rectangle, it is inside
        projs = [pl.projection(point) for pl in planes]
        if any([proj == point and Geometry.check_point_in_rect(point, r) for proj, r in zip(projs, rects)]):
            return True

        # if the distance of the point to one of the planes is more than dist between planes, it is outside
        pl_dist = [projs[i].distance(projs[i+1]) for i in range(0, len(projs), 2)]
        dist = [point.distance(proj) for proj in projs]
        if any([d > pl_dist[i//2] for i, d in enumerate(dist)]):
            return False

        return True

    @staticmethod
    def check_point_in_polygons(point_polys):
        (point, polys) = point_polys
        return all([Geometry.point_in_polygon(point, poly) for poly in polys])

    @staticmethod
    def check_point_in_rect(p, r):
        
        def proc(vec):
            vec = [v for v in vec if v != 0]
            vec = [1 if v > 0 else 0 for v in vec]
            return not vec or (sum(vec) == len(vec) or sum(vec) == 0)

        r = np.append(r, [r[0]], axis=0)
        nvecs = [
            np.cross(r[i+1]-r[i], p-r[i])
            for i in range(len(r)-1)
        ]
        return proc([nvec[0] for nvec in nvecs]) and proc([nvec[1] for nvec in nvecs]) and proc([nvec[2] for nvec in nvecs])

    @staticmethod
    def segment_intersection(s1, s2):
        pois = intersection(s1, s2)
        return pois if (not pois or not isinstance(pois[0], Segment3D)) else list(pois[0].points)
    
    @staticmethod
    def segment_rectangle_intersection(s, r):

        s, pl = Segment3D(*s), Plane(*r[:3])
        
        # if one of the points in rect, return both points
        if any([Geometry.check_point_in_rect(p, r) for p in s.points]):
            return list(s.points)

        if not pl.is_parallel(s):
            pois = [p for p in intersection(pl, s) if Geometry.check_point_in_rect(p, r)]
            return pois + list(s.points)

        if pl.distance(s) != 0: # if plane and seg are parallel with non 0 distance, no intersection
            return []

        segments = [Segment3D(r[i], r[(i+1)%len(r)]) for i in range(len(r))]
        pois = [Geometry.segment_intersection(s, seg) for seg in segments]
        pois = [item for sublist in pois for item in sublist]
        pois = [p for p in pois if p and Geometry.check_point_in_rect(p, r)]
        return pois + list(s.points)
        

    @staticmethod
    def are_parallel_noncoplanar(r1, r2):
        pl1, pl2 = Plane(*r1[:3]), Plane(*r2[:3])
        return pl1.is_parallel(pl2) and pl1.distance(pl2) > 0

    def get_points(rect_pair):
        (r1, r2) = rect_pair
        segs = [[r1[i], r1[(i+1)%len(r1)]] for i in range(len(r1))]       
        inter = [p for p in [Geometry.segment_rectangle_intersection(s, r2) for s in segs] if p]
        inter = [item for sublist in inter for item in sublist]
        return inter

    @staticmethod
    def rectangle_intersections_parallel(rects1, rects2):
        pairs = [(r1, r2) for r2 in rects2 for r1 in rects1 if not Geometry.are_parallel_noncoplanar(r1, r2)]
        pairs += [(r2, r1) for (r1, r2) in pairs]
        points = Pool(16).map(Geometry.get_points, pairs)
        points = [item for sublist in points for item in sublist]
        return set(points)
                        
    # convention is clockwise min starting with top left followed by clockwise max 
    @staticmethod
    def get_frustrum_rects(f):
        rect_points = [
            f[:4], f[4:],
            [f[0], f[3], f[7], f[4]],
            [f[1], f[2], f[6], f[5]],
            [f[0], f[4], f[5], f[1]],
            [f[3], f[7], f[6], f[2]]
        ]
        return [[Point3D(x, y, z) for [x, y, z] in points] for points in rect_points]

    @staticmethod
    def get_frustrum_volume(f, l):
        rects = Geometry.get_frustrum_rects(f)
        areas = [float(r[1].distance(r[0]))*float(r[2].distance(r[1])) for r in rects[:2]]
        return (l/3)*(areas[0] + areas[1] + math.sqrt(areas[0]*areas[1]))

    # convention is clockwise min starting with top left followed by clockwise max 
    @staticmethod
    def frustrum_intersect(f1, f2):
        print(f1)
        print(f2)
        [f1, f2] = [[[v for v in r] for r in f] for f in [f1, f2]]
        [poly1, poly2] = [Geometry.get_frustrum_rects(f) for f in [f1, f2]]
        start = datetime.datetime.now()        
        points = Geometry.rectangle_intersections_parallel(poly1, poly2)
        end = datetime.datetime.now()
        #print('rect_inters=%s' % (end-start))

        polys = [poly1, poly2]
        point_polys = [(p, polys) for p in points]
        valid_idx = Pool(8).map(Geometry.check_point_in_polygons, point_polys)
        points = [p for i, p in enumerate(points) if valid_idx[i]]
        points = [tuple([float(p.x), float(p.y), float(p.z)]) for p in points]
        return points                          

    @staticmethod
    def frustrum_intersection_score(v1, v2, pois):
        try:
            hull = ConvexHull(np.array(pois))
            union_vol = v1 + v2 - hull.volume
            return hull.volume/union_vol
        except QhullError as e:
            print(e)
            return 0
            
    
def test_frustrums_intersection():
    import datetime
    start = datetime.datetime.now()


    f1 = [
        [41.33343944, -1.54369543, 20.08393261],
        [41.34371328, -0.56976876, 20.07792906],
        [40.60659891, -0.56976876, 18.81650898],
        [40.59632506, -1.54369543, 18.82251253],
        [24.06616139, 15.08603392, 24.60276534],
        [0.72658453,  3.99927529, 38.24131286],
        [-21.38496584, 3.99927529, 0.40192944],
        [1.95461102,  15.08603392, -13.23661808]
    ]
    f2 = [
        [41.33343944, -1.54369543, 20.08393261],
        [41.34371328, -0.56976876, 20.07792906],
        [40.60659891, -0.56976876, 18.81650898],
        [40.59632506, -1.54369543, 18.82251253],
        [24.06616139, 15.08603392, 24.60276534],
        [0.72658453,  3.99927529, 38.24131286],
        [-21.38496584,   3.99927529,   0.40192944],
        [1.95461102,  15.08603392, -13.23661808]
    ]    

    intersections = Geometry.frustrum_intersect(f1, f2)
    end = datetime.datetime.now()
    print('tot=%s' % (end-start))
    for i in intersections:
        print(i)
    
    
def test_segment_rectangle_intersection():
#[Point3D(0, 10, 10), Point3D(0, -10, 10)] [Point3D(0, 15, 10), Point3D(0, 15, -10), Point3D(10, 15, -10), Point3D(10, 15, 10)] [Point3D(0, 15, 10)]    
    r = [[0, 15, 10], [0, 15, -10], [10,15, -10], [10,15,10]]
    s1 = [[0, 0, 0], [0, 20, 0]]       # coplanar
    s2 = [[0, 0, 20], [20, 20, 20]]    # parallel
    s3 = [[0, 0, 0], [0, 0, 20]]       # intersecting
    s = [[0, 10, 10], [0, -10, 10]]       
    print(Geometry.segment_rectangle_intersection(s1, r))
#    assert(0 == Geometry.segment_plane(s2, r))
#    assert(1 == Geometry.segment_plane(s3, r))


def test_point_in_rectangle():
    r = [[0, 0, 0], [10, 0, 0], [10,10, 0], [0,10,0]]
    p = [9, 9, 1]
    print(Geometry.check_point_in_rect(p, r))

def test_check_point_in_frustrum():
    start = datetime.datetime.now()    
    f = [
        [0, 10, 10], [0, -10, 10], [0, -10, -10], [0, 10, -10],
        [10, 10, 10], [10, -10, 10], [10, -10, -10], [10, 10, -10],        
    ]
    rects = Geometry.get_frustrum_rects(f)
    print(Geometry.check_point_in_polygon([0, 0, 0], rects)) # true
    print(Geometry.check_point_in_polygon([0, 10, 10], rects)) # true
    print(Geometry.check_point_in_polygon([0, -10, 10], rects)) # true
    print(Geometry.check_point_in_polygon([5, 5, 5], rects)) #true
    print(Geometry.check_point_in_polygon([-5, 5, 5], rects)) # front false
    print(Geometry.check_point_in_polygon([15, 5, 5], rects)) # back false
    print(Geometry.check_point_in_polygon([5, 15, 5], rects)) # left false 
    print(Geometry.check_point_in_polygon([5,-15, 5], rects)) # right false
    print(Geometry.check_point_in_polygon([5,5, 15], rects)) # top false 
    print(Geometry.check_point_in_polygon([5,5, -15], rects)) # down false
    
    end = datetime.datetime.now()
    print('time=%s' % (end-start))
    
if '__main__' == __name__:
    #test_segment_rectangle_intersection()
    #test_point_in_rectangle()
    test_frustrums_intersection()
    #test_check_point_in_frustrum()



'''
    @staticmethod
    def rectangle_intersections(rects1, rects2):
        num_rects = len(rects1)*len(rects2)
        count = [0]
        
        def get_points(r1, r2):
            if count[0]%2 == 0:
                print('%s of %s' % (int(count[0]/2), num_rects))
            segs = [[r1[i], r1[(i+1)%len(r1)]] for i in range(len(r1))]
            inter = [p for p in [Geometry.segment_rectangle_intersection(s, r2) for s in segs] if p]
            inter = [item for sublist in inter for item in sublist]
            count[0] += 1
            return inter
                
        points = [get_points(r1, r2) + get_points(r2, r1) for r2 in rects2 for r1 in rects1 if not Geometry.are_parallel_noncoplanar(r1, r2)]
        points = [item for sublist in points for item in sublist]
        return set(points)

    @staticmethod
    def check_point_in_polygons(point_polys):


        
        
        def check_point_in_polygon(point, rects):
            f_pl = Plane(*rects[0][:3])
            b_pl = Plane(*rects[1][:3])
            l_pl = Plane(*rects[2][:3])
            r_pl = Plane(*rects[3][:3])
            t_pl = Plane(*rects[4][:3])
            d_pl = Plane(*rects[5][:3])

            

            proj_f_pl = f_pl.projection(point)        
            if proj_f_pl == point:
                return Geometry.check_point_in_rect(point, rects[0])

            proj_b_pl = b_pl.projection(point)
            if proj_b_pl == point:
                return Geometry.check_point_in_rect(point, rects[1])

            if point.distance(proj_f_pl) > proj_f_pl.distance(proj_b_pl) or point.distance(proj_b_pl) > proj_f_pl.distance(proj_b_pl):
                return False

            proj_l_pl = l_pl.projection(point)        
            if proj_l_pl == point:
                return Geometry.check_point_in_rect(point, rects[2])

            proj_r_pl = r_pl.projection(point)
            if proj_r_pl == point:
                return Geometry.check_point_in_rect(point, rects[3])

            if point.distance(proj_l_pl) > proj_l_pl.distance(proj_r_pl) or point.distance(proj_r_pl) > proj_l_pl.distance(proj_r_pl):
                return False

            proj_t_pl = t_pl.projection(point)
            if proj_t_pl == point:
                return Geometry.check_point_in_rect(point, rects[4])

            proj_d_pl = d_pl.projection(point)
            if proj_d_pl == point:
                return Geometry.check_point_in_rect(point, rects[5])

            if point.distance(proj_t_pl) > proj_t_pl.distance(proj_d_pl) or point.distance(proj_d_pl) > proj_t_pl.distance(proj_d_pl):
                return False

            return True

        (point, polys) = point_polys
        return reduce(lambda x, y: x and y, [check_point_in_polygon(point, poly) for poly in polys])



'''
