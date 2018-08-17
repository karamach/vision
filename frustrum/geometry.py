from sympy.geometry import Line3D, Plane, Segment3D
from sympy import Point3D, intersection, Polygon
import numpy as np

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
    def check_point_in_rect(p, r):
        r = np.array(r)
        r = np.append(r, [r[0]], axis=0)
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
        s = Segment3D(*[Point3D(*point) for point in s])
        pl = Plane(*[Point3D(*point) for point in r[:3]])
        if pl.is_parallel(s):
            if pl.distance(s) != 0:
                return []

            segments = [Segment3D(r[i], r[(i+1)%len(r)]) for i in range(len(r))]
            intersections = [intersection(s, seg) for seg in segments]
            intersections = [
                list(inters[0].points) if len(inters) > 0 and not Segment3D.are_concurrent(segments[i], s) else inters
                for i, inters in enumerate(intersections)
            ]
            intersections = sum([i for i in intersections if i is not None and len(i) > 0], [])
            return intersections
        else:
            inter = intersection(pl, s)
            return inter if Geometry.check_point_in_rect(inter[0], r) and s.contains(inter[0]) else []
    
    @staticmethod
    def are_parallel_noncoplanar(r1, r2):
        pl1 = Plane(*[Point3D(*point) for point in r1[:3]])
        pl2 = Plane(*[Point3D(*point) for point in r2[:3]])
        return pl1.is_parallel(pl2) and pl1.distance(pl2) > 0
        
        
    @staticmethod
    def rectangle_intersections(rects1, rects2):
        inters = []
        for r1 in rects1:
            for r2 in rects2:
                if Geometry.are_parallel_noncoplanar(r1, r2):
                    print('parallel')
                    continue
                
                segs1 = [[r1[i], r1[(i+1)%len(r1)]] for i in range(len(r1))]
                inter1 = [Geometry.segment_rectangle_intersection(s, r2) for s in segs1]
                for s, i in zip(segs1, inter1):
                    if i is not None and len(i)>0:
                        pass #print(i)
                inter1 = [p for p in inter1 if p is not None and len(p) > 0]
                if len(inter1) > 0:
                    for i in inter1:
                        inters.append(i)
                
                segs2 = [[r2[i], r2[(i+1)%len(r2)]] for i in range(len(r2))]
                inter2 = [Geometry.segment_rectangle_intersection(s, r1) for s in segs2]
                for s, i in zip(segs2, inter2):
                    if i is not None and len(i)>0:
                        pass #print(i)
                inter2 = [p for p in inter2 if p is not None and len(p) > 0]
                if len(inter2) > 0:
                    for i in inter2:
                        inters.append(i)

        inters = sum(inters, [])
        return inters
                
                
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

    # convention is clockwise min starting with top left followed by clockwise max 
    @staticmethod
    def frustrum_intersect(f1, f2):
        print(f1)
        print(f2)
        rects1 = Geometry.get_frustrum_rects(f1)
        rects2 = Geometry.get_frustrum_rects(f2)
        inters = Geometry.rectangle_intersections(rects1, rects2)
        inters = [tuple([float(p.x), float(p.y), float(p.z)]) for p in inters]
        points = set(inters)
        ix, iy, iz = [p[0] for p in points],  [p[1] for p in points],  [p[2] for p in points]
        origin = [np.mean(np.array(ar)) for ar in [ix, iy, iz]]
        radius = max([Point3D(*origin).distance(Point3D(*p)) for p in points])
        return points, float(radius), origin
                  
        

def test_frustrums_intersection():
    f1 = [
        [142., 146.81832586,  58.81832586], [142.        ,  29.18167414,  58.81832586], [142.        ,  29.18167414, -58.81832586], [142.        , 146.81832586, -58.81832586],
        [ 40.        , 104.56854249,  16.56854249], [40.        , 71.43145751, 16.56854249], [ 40.        ,  71.43145751, -16.56854249], [ 40.        , 104.56854249, -16.56854249]]
    f2 = [[133.       ,  55.0904038,  55.0904038], [133.       , -55.0904038,  55.0904038], [133.       , -55.0904038, -55.0904038], [133.       ,  55.0904038, -55.0904038],
          [40.        , 16.56854249, 16.56854249], [ 40.        , -16.56854249,  16.56854249], [ 40.        , -16.56854249, -16.56854249], [ 40.        ,  16.56854249, -16.56854249]]    

    intersections = Geometry.frustrum_intersect(f1, f2)
    for item in intersections:
        print(' inter=', item)
    
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
    

if '__main__' == __name__:
    #test_segment_rectangle_intersection()
    #test_point_in_rectangle()
    test_frustrums_intersection()
