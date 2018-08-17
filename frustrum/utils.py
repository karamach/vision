import numpy as np
import math
from functools import reduce
from sympy.geometry import Line3D, Plane
from sympy import Point3D, intersection

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
    def plane_intersect1(a, b):
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
    def plane_intersect(points1, points2):
        pl1 = Plane(*points1)
        pl2 = Plane(*points2)
        return intersection(pl1, pl2)

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
        return rank == 1

    @staticmethod
    def angle_between_lines(l1, l2):
        d1 = np.array([l1[1][0]-l1[0][0], l1[1][1]-l1[0][1], l1[1][2]-l1[0][2]])
        d2 = np.array([l2[1][0]-l2[0][0], l2[1][1]-l2[0][1], l2[1][2]-l2[0][2]])
        angle = np.arccos(np.dot(d1, d2)/(np.linalg.norm(d1)*np.linalg.norm(d2)))
        return angle

    def are_lines_parallel(l1, l2):
        angle = round(Geometry.angle_between_lines(l1, l2), 2)
        return angle == 0 or angle == 3.14
   

    @staticmethod
    def lines_intersection(lines1, lines2):

        def line_intersection(l1, l2):
            l1 = Line3D(Point3D(l1[0][0], l1[0][1], l1[0][2]), Point3D(l1[1][0], l1[1][1], l1[1][2]))
            l2 = Line3D(Point3D(l2[0][0], l2[0][1], l2[0][2]), Point3D(l2[1][0], l2[1][1], l2[1][2]))
            inters = intersection(l1, l2)
            print(inters)
            return inters        
        
        def line_intersection1(l1, l2):
            # Finds the intersection of 2 lines l1, l2 represented as numpy arrays of 2 points on the line
            # (x-x0)/xn = (y-y0)/yn = (z-z0)/zn
            # use the den that is not equal in two lines and find value of variable using that. then find other
            # variables
            l1, l2 = np.array(l1), np.array(l2)
            res = [0 for i in range(3)]
        
            d1 = np.array([l1[1][0]-l1[0][0], l1[1][1]-l1[0][1], l1[1][2]-l1[0][2]])
            d2 = np.array([l2[1][0]-l2[0][0], l2[1][1]-l2[0][1], l2[1][2]-l2[0][2]])

            def is_valid_idx(d1, d2, idx):
                return d1[idx] != d2[idx] and d1[idx] != 0 and d2[idx] != 0

            valid_idx = [i for i in range(3) if is_valid_idx(d1, d2, i)]
            print(valid_idx)
            print(d1, d2)
            if len(valid_idx) == 0:
                return None
            
            idx = valid_idx[0]
            res[idx] = (l1[0][idx]*d2[idx] - l2[0][idx]*d1[idx])/(d2[idx]-d1[idx])
            print('res[idx=', res[idx])
            remaining_idx = set([0, 1, 2]) - set([idx])            
            for i in remaining_idx:
                res[i] = l1[0][i] + (d1[i] * (res[idx]-l1[0][idx])/d1[idx])  # x0 + xn*(z-z0)/zn
            print(l1)
            print(l2)
            print(res)
            print('---')
            return np.array(res)

        line_pairs = [[l1, l2] for l2 in lines2 for l1 in lines1]
        line_pairs = [line_pair for line_pair in line_pairs if not Geometry.are_lines_parallel(line_pair[0], line_pair[1])]
        intersections = [line_intersection(line_pair[0], line_pair[1]) for line_pair in line_pairs]
        intersections = [inters for inters in intersections if inters is not None]
        return intersections

    @staticmethod
    def rect_line_intersection(r, l):
        r_tmp = np.append(r, [r[0]], axis=0)
        r_lines = [[r_tmp[i], r_tmp[i+1]] for i in range(len(r_tmp)-1)]
        return Geometry.lines_intersection(r_lines, [l])
                                 
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

        print('[ok][frustrum equals ..][val=false]')
        f1_planes = Geometry.get_frustrum_plane_points(f1)
        f2_planes = Geometry.get_frustrum_plane_points(f2)
        plane_pairs = [[f1_pl, f2_pl] for f2_pl in f2_planes for f1_pl in f1_planes]
        plane_pairs_n = [[Geometry.get_plane(pl) for pl in plane_pair] for plane_pair in plane_pairs] # normalize
        valid_plane_idx = [ifx for idx, plane_pair in enumerate(plane_pairs_n) if not Geometry.are_planes_parallel(plane_pair[0], plane_pair[1])]
        plane_pairs_n = [plane_pairs_n[i] for i in valid_plane_idx]
        plane_pairs = [plane_pairs[i] for i in valid_plane_idx]
        plane_inters_lines = [Geometry.plane_intersect(plane_pair[0], plane_pair[1]) for plane_pair in plane_pairs_n]
        plane_insters_points = [Geometry.rect_line_intersection(plane_pairs[i][0], plane_inters_lines[i])]
        return plane_inters_points    

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
    #pl1 = Geometry.get_plane(points1)
    #pl2 = Geometry.get_plane(points2)
    #intersection = Geometry.plane_intersect(pl1, pl2)
    intersection = Geometry.plane_intersect(points1[:3], points2[:3])
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

def test_line_intersect():
    l1 = np.array([
        [0, 0, 0],
        [5, 5, 5]
    ])
    l2 = np.array([
        [0, 5, 0],
        [5, 0, 5]
    ])
    p_intersect = Geometry.lines_intersection(l1, l2)
    print(p_intersect)

def test_rectangle_intersect():
    r1 = np.array([[5, 5, 5], [0, 0, 5], [0, 0, 0], [5, 5, 0]])
    r2 = np.array([[0, 5, 5], [5, 0, 5], [5, 0, 0], [0, 5, 0]])
    r1_pl = Geometry.get_plane(r1)
    r2_pl = Geometry.get_plane(r2)    
    is_parallel = Geometry.are_planes_parallel(r1_pl, r2_pl)
    if is_parallel:
        print('is_parallel=%s' % is_parallel)
        return
    
        (p1, p2) = Geometry.plane_intersect(r1_pl, r2_pl)
        print('p1, p2 = %s %s' %(p1, p2))
        r1_tmp = np.append(r1, [r1[0]], axis=0)
        lines = [[r1_tmp[i], r1_tmp[i+1]] for i in range(len(r1_tmp)-1)]
        print('lines1=%s'% lines)
        inter1 = Geometry.lines_intersection(lines, [[p1, p2]])
        r2_tmp = np.append(r2, [r2[0]], axis=0)
        lines = [[r2_tmp[i], r2_tmp[i+1]] for i in range(len(r2_tmp)-1)]
        print('lines2=%s'% lines)
        inter2 = Geometry.lines_intersection(lines, [[p1, p2]])
        print(inter1, inter2)
        
def test_lines_parallel():
    l1 = np.array([
        [0, 0, 0],
        [5, 5, 5]
    ])
    l2 = np.array([
        [0, 5, 0],
        [5, 0, 5]
    ])

    angle = Geometry.angle_between_lines(l1, l2)
    print(math.degrees(angle))

def test_rect_line_intesect():
    r1 = np.array([[5, 5, 5], [0, 0, 5], [0, 0, 0], [5, 5, 0]])
    l1 = np.array([[2.5, 2.5, 0], [5, 5, 5]])
    intersections = Geometry.rect_line_intersection(r1, l1)
    print('inters')
    for inters in intersections:
        print(inters)
    
if '__main__' == __name__:
    test_plane_intersect()    
    #test_point_in_rect()
    #test_line_intersect()
    #test_rectangle_intersect()
    #test_lines_parallel()
    #test_rect_line_intesect()
