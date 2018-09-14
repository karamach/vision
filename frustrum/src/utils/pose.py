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

#       R = yaw(y).dot(pitch(p).dot(roll(r)))  # current body frame
        R = roll(r).dot(pitch(p).dot(yaw(y)))  # fixed frame
        return [np.dot(R, point) for point in points]        
        
    def trans(points, xyz):
        [x, y, z] = xyz
        return [point + np.array([x, y, z]) for point in points]


