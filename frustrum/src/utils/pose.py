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
    def scale(s, xyzw):
        scale_matrix = np.array([
            [s, 0, 0, 0],
            [0, s, 0, 0],
            [0, 0, s, 0],
            [0, 0, 0, 1]
        ])
        return np.dot(scale_matrix, xyzw)

    # houdini rpy transform
    def houdini_rpytransform(xyzw, origin, orientation, scale):
        xyzw = Pose.trans(origin, xyzw)
        xyzw = Pose.rot(xyzw, orientation[::-1], True)
        xyzw = Pose.scale(scale, xyzw)
        return xyzw

    # current pretransform
    def curr_pretransform(xyzw, origin, orientation, scale):
        xyzw = Pose.trans(origin, xyzw)
        xyzw = Pose.rot(xyzw, orientation, True)
        xyzw = Pose.scale(scale, xyzw)
        return xyzw

    def sim_transform(xyzw, origin, orientation, scale):
        xyzw = Pose.rot(xyzw, orientation, True)
        xyzw = Pose.trans(origin, xyzw)
        xyzw = Pose.scale(scale, xyzw)
        return xyzw
    

    # get a homogenous transform comprising a rotation ypr
    # and translation xyzw
    @staticmethod
    def transform(ypr, t, fixed = True):

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
        H = np.column_stack((R, t))
        H = np.vstack([H, [0, 0, 0, 1]])
        return H
    

    # Body-Y-P-R sequence implies, yaw followed by pitch followed by roll
    # wrt body frame each time and is computed as RyRpR World-Y-P-R sequence
    # implies, yaw followed by pitch followed by roll wrt world frame each
    # time and is computed as RrRpRy
    # So it can be seen Body-Y-P-R = World-R-P-Y    
    # yaw pitch roll rotation in that sequence
    # (Note there are 12 possible rotations ypr, yrp, pyr, pry, rpy, ryp, ypy,
    # yry, rpr, ryr, pyp, prp)
    # If you take instrinsic and extrinsic (rotation wrt fixed or current frame),
    # there are 12 more 
    @staticmethod
    def rot(xyzw, ypr, relative=False):

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

        def extrinsic(y, p, r):
            return roll(r).dot(pitch(p).dot(yaw(y)))

        def intrinsic(y, p, r):
            return yaw(y).dot(pitch(p).dot(roll(r)))

        R = intrinsic(y, p, r) if relative else extrinsic(y, p, r)
        H = np.vstack([R, [0, 0, 0]])
        H = np.column_stack((H, [0, 0, 0, 1]))
        return np.dot(H, xyzw)
        
    def trans(t, xyzw):
        R = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        H = np.column_stack((R, t))                            
        H = np.vstack([H, [0, 0, 0, 1]])
        return np.dot(H, xyzw)

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
         


