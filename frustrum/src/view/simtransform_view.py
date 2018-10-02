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

def plot_poses(gpsPoints, gpsColors, solvePoints, solveColors,  pointCloudPoints,
               pointCloudColors):
    
    fig = plt.figure(figsize=(10,6))
    gs = gridspec.GridSpec(3, 2, width_ratios=[4, 1])
    ax_mins, ax_maxs = [-40, -20], [40, 20]
    
    ax1 = plt.subplot(gs[:, 0], projection='3d')
    ax2 = plt.subplot(gs[0, 1], projection='3d')
    ax3 = plt.subplot(gs[1, 1], projection='3d')
    ax4 = plt.subplot(gs[2, 1], projection='3d')

    def reset_axes(ax):
        ax.clear()
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.plot([ax_mins[0], ax_maxs[0]], [0, 0], [0, 0], color='red')
        ax.plot([0, 0], [ax_mins[0], ax_maxs[0]], [0, 0], color='green')
        ax.plot([0, 0], [0, 0], [ax_mins[0], ax_maxs[0]], color='blue')
        ax.set_xlabel('X', fontsize=10)
        ax.set_ylabel('Y', fontsize=10)        
        ax.set_ylabel('Z', fontsize=10)        
        fig.tight_layout()

    def plot_view_poses(ax, points_list, labels, colors_list):

        for label, points, colors in zip(labels, points_list, colors_list):                
            ax.scatter(
                [point[0] for point in points],
                [point[1] for point in points],
                [point[2] for point in points],
                s=2, marker='o', picker=5, facecolors='none', edgecolors=colors, label=label
            )
        ax.set_xlabel('X', fontsize=10)
        ax.set_ylabel('Y', fontsize=10)        
        ax.set_ylabel('Z', fontsize=10)        
        ax.legend()
        ax.grid(True)

    def plot_pointcloud_poses(ax, points_list, labels, colors_list):

        for label, points, col in zip(labels, points_list, colors_list):                
            ax.scatter(
                [point[0] for point in points],
                [point[1] for point in points],
                [point[2] for point in points],
                c=col, label=label
            )
        ax.legend()
        ax.grid(True)        
        
    plot_view_poses(ax2, [gpsPoints], ['gps'], [gpsColors])
    plot_view_poses(ax3, [solvePoints], ['solve'], [solveColors])
    if pointCloudPoints and pointCloudColors:
        plot_view_poses(ax4, [pointCloudPoints], ['pointCloud'], [pointCloudColors])
    
    plot_view_poses(ax1, [gpsPoints, solvePoints], ['gps', 'solve'], [gpsColors, solveColors])
    if pointCloudPoints and pointCloudColors:
        plot_pointcloud_poses(ax1, [pointCloudPoints], ['pointCloud'], [pointCloudColors])
    
    fig.canvas.draw_idle()    
    plt.show()    
