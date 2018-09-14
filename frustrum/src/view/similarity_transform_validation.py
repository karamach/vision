import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as a3
import numpy as np
import math
from matplotlib.widgets import Button, CheckButtons
import matplotlib.gridspec as gridspec

from utils.geometry import Geometry

from model.camera import Camera
from model.inters import Inters

from control.pose_control import CameraTransControl, CameraRotControl
from control.frust_control import CameraFrustControl
from control.angle_control import CameraAngleControl

import argparse

def plot_poses(cameras1, cameras2):
    
    fig = plt.figure(figsize=(10,6))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])
    ax_mins, ax_maxs = [-40, -20], [40, 20]
    [ax1, ax2] = [plt.subplot(gs[i], projection='3d') for i in range(2)]

    def reset_axes(ax):
        ax.clear()
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.plot([ax_mins[0], ax_maxs[0]], [0, 0], [0, 0], color='red')
        ax.plot([0, 0], [ax_mins[0], ax_maxs[0]], [0, 0], color='green')
        ax.plot([0, 0], [0, 0], [ax_mins[0], ax_maxs[0]], color='blue')
        fig.tight_layout()

    def plot_view_poses(ax, cameras):
                
        origins = [c.curr_origin for c in cameras]
        a_points = [c.curr_axes_points for c in cameras]
        for o, [x, y, z] in zip(origins, a_points):
            ax.plot([o[0]] + [x[0]], [o[1]] + [x[1]], [o[2]] + [x[2]], color='red', linestyle='-')        
            ax.plot([o[0]] + [y[0]], [o[1]] + [y[1]], [o[2]] + [y[2]], color='green', linestyle='-')        
            ax.plot([o[0]] + [z[0]], [o[1]] + [z[1]], [o[2]] + [z[2]], color='blue', linestyle='-')
                
        ax.scatter(
            [o[0] for o in origins],
            [o[1] for o in origins],
            [o[2] for o in origins],
            color='black', s=10, marker='o', picker=5
        )            

    plot_view_poses(ax1, cameras1)
    plot_view_poses(ax2, cameras2)
    
    fig.canvas.draw_idle()    
    plt.show()    
