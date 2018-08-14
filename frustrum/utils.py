import numpy as np
import math
from functools import reduce

class Geometry(object):

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

    @staticmethod
    def plane_intersect(a, b):
        """
        a, b   4-tuples/lists
               Ax + By +Cz + D = 0
               A, B, C, D in order  
        output: 2 points on line of intersection, np.arrays, shape (3,)
        """
        a_vec, b_vec = np.array(a[:3]), np.array(b[:3])
        aXb_vec = np.cross(a_vec, b_vec)

        A = np.array([a_vec, b_vec, aXb_vec])
        d = np.array([-a[3], -b[3], 0.]).reshape(3,1)

        # could add np.linalg.det(A) == 0 test to prevent linalg.solve throwing error
        p_inter = np.linalg.solve(A, d).T
        print(p_inter)
        return p_inter[0], (p_inter + aXb_vec)[0]

    @staticmethod
    def get_plane(points):
        normal_vec = np.cross(points[2]-points[0], points[1]-points[0])
        return normal_vec[0], normal_vec[1], normal_vec[2], -np.dot(normal_vec, points[0])

    # convention of points is clockwise min starting with top left followed by clockwise max
    # convention of result planes is front, back, left, right, top, bottom
    @staticmethod
    def get_frustrum_planes(f):
        planes = [
            Geometry.get_plane(points)
            for points in Geometry.get_frustrum_plane_points(f)
        ]
        return planes

    @staticmethod
    def get_frustrum_plane_points(f):
        return [
            f[:3],
            f[4:],
            [f[0], f[3], f[7], f[4]],
            [f[1], f[2], f[6], f[5]],
            [f[0], f[4], f[5], f[1]],
            [f[3], f[7], f[6], f[2]]
        ]
    
    @staticmethod
    def check_point_in_rect(point, rect):
        rect = np.append(rect, [rect[0]], axis=0)
        nvecs = [np.cross(rect[i+1]-rect[i], point-rect[i]) for i in range(len(rect)-1)]

        def proc(vec):
            vec = list(filter(lambda v: v != 0, vec))
            vec = list(map(lambda v: 1 if v>0 else 0, vec))
            return not vec or (sum(vec) == len(vec) or sum(vec) == 0)
            
        return proc([nvec[0] for nvec in nvecs]) and proc([nvec[1] for nvec in nvecs]) and proc([nvec[2] for nvec in nvecs])
    
    @staticmethod
    def are_planes_parallel(pl1, pl2):
        mat = np.array([
            [pl1[0], pl1[1], pl1[2]],
            [pl2[0], pl2[1], pl2[2]]
        ])
        rank =  np.linalg.matrix_rank(mat)                          
        print('rank=%s' % rank)
        return rank == 1
                        
    @staticmethod
    def are_frustrums_equal(f1, f2):
        return sum([np.array_equal(p1, p2) for p1, p2 in zip(f1, f2)]) == 8
    
    # convention is clockwise min starting with top left followed by clockwise max 
    @staticmethod
    def frustrum_intersect(f1, f2):
        print('f1: %s\n f2: %s' % (f1, f2))
        if Geometry.are_frustrums_equal(f1, f2):
            print('[ok][frustrum equals ..][val=true]')
            return f1
        else:
            print('[ok][frustrum equals ..][val=false]')

        f1_planes = Geometry.get_frustrum_plane_points(f1)
        f2_planes = Geometry.get_frustrum_plane_points(f2)
        intersect_points = []
        for i, f1_pl in enumerate(f1_planes):
            for j, f2_pl in enumerate(f2_planes):
                print('[----------------\nplanes .. %s %s\n%s\n%s]' % (i, j, f1_pl, f2_pl))
                f1_npl = Geometry.get_plane(f1_pl)
                f2_npl = Geometry.get_plane(f2_pl)
                is_parallel = Geometry.are_planes_parallel(f1_npl, f2_npl)
                print('is_parallel=%s' % is_parallel)
                if not is_parallel:
                    (p1, p2) = Geometry.plane_intersect(f1_npl, f2_npl) 
                    print('intersection_points=%s %s' % (p1, p2))                   
                    valid_intersection = [
                        1 if (Geometry.check_point_in_rect(p1, pl) and Geometry.check_point_in_rect(p2, pl)) else 0
                        for pl in [f1_pl, f2_pl]
                    ]
                    if sum(valid_intersection) == 2:
                        intersect_points.append(p1)
                        intersect_points.append(p2)
                    print('valid_intersection=%s' % (len(intersect_points) > 0))                   
                    
        return intersect_points    

def test_plane_intersect():
    points1 = np.array([
        [4, 4, 6],
        [0, 0, 6],
        [0, 0, 2],
        [4, 4, 2]
    ])
    points2 = np.array([
        [0, 4, 4],
        [4, 0, 4],
        [4, 0, 0],
        [0, 4, 0]
    ])
    pl1 = Geometry.get_plane(points1)
    pl2 = Geometry.get_plane(points2)
    intersection = Geometry.plane_intersect(pl1, pl2)
    print(intersection)

    

def test_get_plane():
    points = np.array([
        [1, 2, -2],
        [3, -2, 1],
        [5, 1, -4]
    ])
    ret = Geometry.get_plane(points)
    print(ret)

def test_point_in_rect():
    rect = np.array([
        [5, 5, 5],
        [0, 0, 5],
        [0, 0, 0],        
        [5, 5, 0]
    ])
    point = np.array([-1, -1, -1])
    print(Geometry.check_point_in_rect(point, rect))

if '__main__' == __name__:
    test_plane_intersect()
    #test_point_in_rect()
