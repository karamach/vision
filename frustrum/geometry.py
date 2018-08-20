from sympy.geometry import Line3D, Plane, Segment3D
from sympy import Point3D, intersection, Polygon
import numpy as np
import datetime

import math

class Pose:

    @staticmethod
    def rot(points, ypr):

        [y, p, r] = ypr
        
        def yaw(alpha):
            return np.array([
                [math.cos(alpha), -math.sin(alpha), 0],
                [math.sin(alpha), math.cos(alpha), 0],
                [0, 0, 1]
        ])

        def pitch(beta):
            return np.array([
                [math.cos(beta), 0, math.sin(beta)],
                [0, 1, 0],
                [-math.sin(beta), 0, math.cos(beta)]
        ])

        def roll(gamma):
            return np.array([
                [1, 0, 0],
                [0, math.cos(gamma), -math.sin(gamma)],
                [0, math.sin(gamma), math.cos(gamma)]
        ])

        R = yaw(y).dot(pitch(p).dot(roll(r)))
        return [np.dot(R, point) for point in points]        
        
    def trans(points, xyz):
        [x, y, z] = xyz
        return [point + np.array([x, y, z]) for point in points]

class Geometry:

    @staticmethod
    def check_point_in_polygon(p, rects):
        f_pl = Plane(*rects[0][:3], eval=False)
        b_pl = Plane(*rects[1][:3], eval=False)
        l_pl = Plane(*rects[2][:3], eval=False)
        r_pl = Plane(*rects[3][:3], eval=False)
        t_pl = Plane(*rects[4][:3], eval=False)
        d_pl = Plane(*rects[5][:3], eval=False)        

        point = p

        proj_f_pl = f_pl.projection(point)        
        if proj_f_pl == point:
            return Geometry.check_point_in_rect(p, rects[0])

        proj_b_pl = b_pl.projection(point)
        if proj_b_pl == point:
            return Geometry.check_point_in_rect(p, rects[1])

        if point.distance(proj_f_pl) > proj_f_pl.distance(proj_b_pl) or point.distance(proj_b_pl) > proj_f_pl.distance(proj_b_pl):
            return False

        proj_l_pl = l_pl.projection(point)        
        if proj_l_pl == point:
            return Geometry.check_point_in_rect(p, rects[2])

        proj_r_pl = r_pl.projection(point)
        if proj_r_pl == point:
            return Geometry.check_point_in_rect(p, rects[3])

        if point.distance(proj_l_pl) > proj_l_pl.distance(proj_r_pl) or point.distance(proj_r_pl) > proj_l_pl.distance(proj_r_pl):
            return False

        proj_t_pl = t_pl.projection(point)
        if proj_t_pl == point:
            return Geometry.check_point_in_rect(p, rects[4])

        proj_d_pl = d_pl.projection(point)
        if proj_d_pl == point:
            return Geometry.check_point_in_rect(p, rects[5])

        if point.distance(proj_t_pl) > proj_t_pl.distance(proj_d_pl) or point.distance(proj_d_pl) > proj_t_pl.distance(proj_d_pl):
            return False

        return True


    @staticmethod
    def check_point_in_rect(p, r):
        r = np.array(r + [r[0]])
        nvecs = [
            np.cross(r[i+1]-r[i], p-r[i])
            for i in range(len(r)-1)
        ]

        def proc(vec):
            vec = [v for v in vec if v != 0]
            vec = [1 if v > 0 else 0 for v in vec]
            return not vec or (sum(vec) == len(vec) or sum(vec) == 0)
            
        return proc([nvec[0] for nvec in nvecs]) and proc([nvec[1] for nvec in nvecs]) and proc([nvec[2] for nvec in nvecs])
    
    @staticmethod
    def segment_rectangle_intersection(s, r):
        s, pl = Segment3D(*s), Plane(*r[:3])
        
        # if both points in rect, return points
        [p1, p2] = [Geometry.check_point_in_rect(p, r) for p in s.points]
        if p1 or p2:
            return list(s.points)

        # since neither point is on rectagle, if segment is parallel to plane, it has to be outside
        if pl.is_parallel(s):
            return []
                        
        pois = intersection(pl, s)
        pois = [p for p in pois if Geometry.check_point_in_rect(p, r)]
        return pois + list(s.points)

    @staticmethod
    def are_parallel_noncoplanar(r1, r2):
        pl1, pl2 = Plane(*r1[:3]), Plane(*r2[:3])
        return pl1.is_parallel(pl2) and pl1.distance(pl2) > 0

    @staticmethod
    def rectangle_intersections(rects1, rects2):
        def get_points(r1, r2):
            segs = [[r1[i], r1[(i+1)%len(r1)]] for i in range(len(r1))]
            inter = [Geometry.segment_rectangle_intersection(s, r2) for s in segs]
            inter = [p for p in inter if p]
            inter = [item for sublist in inter for item in sublist]
            return inter
                
        points = [get_points(r1, r2) + get_points(r2, r1) for r2 in rects2 for r1 in rects1 if not Geometry.are_parallel_noncoplanar(r1, r2)]        
        return set(sum(points, []))
                
        
    # convention is clockwise min starting with top left followed by clockwise max 
    @staticmethod
    def get_frustrum_rects(f):
        rect_points = [
            f[:4],
            f[4:],
            [f[0], f[3], f[7], f[4]],
            [f[1], f[2], f[6], f[5]],
            [f[0], f[4], f[5], f[1]],
            [f[3], f[7], f[6], f[2]]
        ]
        return [[Point3D(x, y, z) for [x, y, z] in points] for points in rect_points]

    @staticmethod
    def get_frustrum_volume(f):
        points = Geometry.get_frustrum_rects(f)
        f_pl = Plane(*rects[0][:3])
        b_pl = Plane(*rects[1][:3])
        d = f_pl.distance(b_pl)
        a_f = rects[0][0].distance(rects[0][1])* rects[0][1].distance(rects[0][2])
        a_b = rects[1][0].distance(rects[1][1])* rects[1][1].distance(rects[1][2])
        return a_f*d + (a_b*d-a_f*d)/2

    # convention is clockwise min starting with top left followed by clockwise max 
    @staticmethod
    def frustrum_intersect(f1, f2):
        [f1, f2] = [[[int(math.ceil(v)) for v in r] for r in f] for f in [f1, f2]]
        [poly1, poly2] = [Geometry.get_frustrum_rects(f) for f in [f1, f2]]
        inters = Geometry.rectangle_intersections(poly1, poly2)
        inters = [point for point in inters if Geometry.check_point_in_polygon(point, poly1) and Geometry.check_point_in_polygon(point, poly2)]
        inters = [tuple([float(p.x), float(p.y), float(p.z)]) for p in inters]
        if not inters:
            return inters, 0, [0, 0, 0]
        return inters
                  
        

def test_frustrums_intersection():
    import datetime
    start = datetime.datetime.now()
    f1 = [
        [142., 146.81832586,  58.81832586],
        [142.        ,  29.18167414,  58.81832586],
        [142.        ,  29.18167414, -58.81832586],
        [142.        , 146.81832586, -58.81832586],
        [40.        , 104.56854249,  16.56854249],
        [40.        , 71.43145751, 16.56854249],
        [ 40.        ,  71.43145751, -16.56854249],
        [ 40.        , 104.56854249, -16.56854249]
    ]
    f2 = [
        [133.       ,  55.0904038,  55.0904038],
        [133.       , -55.0904038,  55.0904038],
        [133.       , -55.0904038, -55.0904038],
        [133.       ,  55.0904038, -55.0904038],
        [40.        , 16.56854249, 16.56854249],
        [ 40.        , -16.56854249,  16.56854249],
        [ 40.        , -16.56854249, -16.56854249],
        [ 40.        ,  16.56854249, -16.56854249]
    ]

    intersections, _, _ = Geometry.frustrum_intersect(f1, f2)
    end = datetime.datetime.now()
    print('time=%s' % (end-start))
    for i in intersections:
        print(i)
    
    
def test_segment_rectangle_intersection():
#[Point3D(0, 10, 10), Point3D(0, -10, 10)] [Point3D(0, 15, 10), Point3D(0, 15, -10), Point3D(10, 15, -10), Point3D(10, 15, 10)] [Point3D(0, 15, 10)]    
    r = [[0, 15, 10], [0, 15, -10], [10,15, -10], [10,15,10]]
    s1 = [[0, 0, 0], [0, 20, 0]]       # coplanar
    s2 = [[0, 0, 20], [20, 20, 20]]    # parallel
    s3 = [[0, 0, 0], [0, 0, 20]]       # intersecting
    s = [[0, 10, 10], [0, -10, 10]]       
#    assert(2 == Geometry.segment_plane(s1, r))
#    assert(0 == Geometry.segment_plane(s2, r))
#    assert(1 == Geometry.segment_plane(s3, r))

    print(Geometry.segment_rectangle_intersection(s, r))

def test_point_in_rectangle():
    r = [[0, 0, 0], [10, 0, 0], [10,10, 0], [0,10,0]]
    p = [9, 9, 1]
    print(Geometry.check_point_in_rect(p, r))

def test_rectangle_intersection():
    r1 = [[[0, 0, 0], [10, 0, 0], [10,10, 0], [0,10,0]]]
    r2 = [[[5, 1, 0], [5, 1, 10], [5, 9, 10], [5,9,0]]]
    inters = Geometry.rectangle_intersections(r1, r2)
    for inter in set(sum(inters, [])):
        print(inter)

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
