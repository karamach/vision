import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math

def get_unit_points(h_ang, v_ang):
    return [
        [1, -math.tan(h_ang/2), math.tan(v_ang/2)],
        [1, math.tan(h_ang/2), math.tan(v_ang/2)],
        [1, math.tan(h_ang/2), -math.tan(v_ang/2)],
        [1, -math.tan(h_ang/2), -math.tan(v_ang/2)]
    ]

def plot_frustrum(unit_points, beg_dist, end_dist):
    beg_points = [[beg_dist*p for p in points] for points in unit_points]
    end_points = [[end_dist*p for p in points] for points in unit_points]
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    beg_x, beg_y, beg_z = [p[0] for p in beg_points],  [p[1] for p in beg_points],  [p[2] for p in beg_points]
    end_x, end_y, end_z = [p[0] for p in end_points],  [p[1] for p in end_points],  [p[2] for p in end_points]
    ax.plot(beg_x + [beg_x[0]], beg_y + [beg_y[0]],  beg_z + [beg_z[0]])
    ax.plot(end_x + [end_x[0]], end_y + [end_y[0]], end_z + [end_z[0]])
        
    plt.show()

if '__main__' == __name__:
    h_ang, v_ang = math.radians(90.0), math.radians(90.0)    
    unit_points = get_unit_points(h_ang, v_ang)
    plot_frustrum(unit_points, 1, 5)
