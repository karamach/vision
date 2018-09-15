import math
import numpy as np

class Pose:

    @staticmethod
    def ypr(R):
        return [
            math.atan2(R[1][0], R[0][0]),
            math.atan2( -R[2][0], math.sqrt(R[2][1]*R[2][1] + R[2][2]*R[2][2])),
            math.atan2(R[2][1], R[2][2])
        ]

    @staticmethod
    def xyz(R):
        return [
             R[0][3],
             R[1][3],
             R[2][3]
        ]            
            

    @staticmethod
    def transform(ypr, xyz, fixed = True):

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

        R = roll(r).dot(pitch(p).dot(yaw(y))) if fixed else yaw(y).dot(pitch(p).dot(roll(r)))
        return np.vstack([np.column_stack((R, xyz)), [0, 0, 0, 1]])
    

    # Body-Y-P-R sequence implies, yaw followed by pitch followed by roll wrt body frame each time and is computed as RyRpRr
    # World-Y-P-R sequence implies, yaw followed by pitch followed by roll wrt world frame each time and is computed as RrRpRy
    # So it can be seen Body-Y-P-R = World-R-P-Y
    
    # yaw pitch roll rotation in that sequence
    # (Note there are 12 possible rotations ypr, yrp, pyr, pry, rpy, ryp, ypy, yry, rpr, ryr, pyp, prp)
    # If you take instrinsic and extrinsic (rotation wrt fixed or current frame), there are 12 more 
    @staticmethod
    def rot(points, ypr, intrinsic=False):

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

        R = yaw(y).dot(pitch(p).dot(roll(r))) if intrinsic else roll(r).dot(pitch(p).dot(yaw(y)))
        H = np.vstack([np.column_stack((R, [0, 0, 0])), [0, 0, 0, 1]])
        return [np.dot(H, point) for point in points]
        
    def trans(points, xyz):
        [x, y, z] = xyz
        return [point + np.array([x, y, z]) for point in points]

    @staticmethod
    def q2ypr(x, y, z, w):
	
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        r = math.atan2(t0, t1)
	
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        p = math.asin(t2)

        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        y = math.atan2(t3, t4)

        return [y, p, r]
         


