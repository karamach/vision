from control.inters_control import IntersControl
# TODO Have to include inters control first due to  CppIntersControl dependency pybind11 causing issue. Need to investigate. KR

import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as a3
import numpy as np
import math
from matplotlib.widgets import Slider, Button, CheckButtons
import matplotlib.gridspec as gridspec
from utils.geometry import Geometry

from model.camera import Camera
from model.inters import Inters

from control.pose_control import CameraTransControl, CameraRotControl
from control.frust_control import CameraFrustControl
from control.angle_control import CameraAngleControl

from scipy.spatial import ConvexHull
from matplotlib.patches import Polygon

import argparse

def create_slider_axes(fig):
    s_axes = [[.05, .65, .15, .01]]    
    for i in range(19):
        prev = s_axes[-1]
        s_axes.append([prev[0], prev[1]-.02, prev[2], prev[3]])

    axes = [fig.add_axes(a, facecolor='lightgoldenrodyellow') for a in s_axes]
    return axes    

def create_sliders(fig, ax_min, ax_max, s_axes, names):
    
    sliders = [
        Slider(a, names[i], ax_min, ax_max, valinit=0, valstep=1)
        for i, a in enumerate(s_axes[:6])
    ]
    sliders += [
        Slider(a, names[i+6], -180, +180, valinit=0, valstep=1)
        for i, a in enumerate(s_axes[6:12])
    ]
    sliders += [
        Slider(a, names[i+12], 0, 2*ax_max, valinit=0, valstep=1)
        for i, a in enumerate(s_axes[12:16])
    ]
    sliders += [
        Slider(a, names[i+16], 0, 180 , valinit=0, valstep=1)
        for i, a in enumerate(s_axes[16:])
    ]
    return sliders

def create_camera_controls(cameras, callback):
    cameraControls = [
        CameraTransControl(cameras[int(i/3)], i%3, callback) for i in range(6)
    ]
    cameraControls += [
        CameraRotControl( cameras[int((i-6)/3)], i%3, callback) for i in range(6, 12)
    ]
    cameraControls += [
        CameraFrustControl(cameras[int((i-12)/2)], i%2, callback) for i in range(12, 16)
    ]
    cameraControls += [
        CameraAngleControl(cameras[int((i-16)/2)], i%2, callback) for i in range(16, 20)
    ]
    return cameraControls


def plot_frustrum(cameras, inters):

    fig = plt.figure(figsize=(20,20), dpi=100)
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 4])
    ax2 = plt.subplot(gs[1], projection='3d')
    ax_mins = [-40, -20]
    ax_maxs = [40, 20]

    # Checkbuttons for visibility control
    rax = plt.axes([0.02, 0.8, 0.1, 0.15])
    labels = ['show_controls','show_inters_points', 'show_inters_hull',  'use_cpp']
    visibility = [False, False, False, False]
    check = CheckButtons(rax, labels, visibility)

    # intersection button
    b_axes = fig.add_axes([.05, .1, .15, .03])
    b_inters = Button(b_axes, 'compute_intersection')

    # sliders
    slider_axes = create_slider_axes(fig)
    names = [
        'c1_x', 'c1_y', 'c1_z', 'c2_x', 'c2_y', 'c2_z',   
        'c1_yaw', 'c1_pitch', 'c1_roll', 'c2_yaw', 'c2_pitch', 'c2_roll',
        'c1_minf', 'c1_maxf', 'c2_minf', 'c2_maxf', 'c1_ha', 'c1_va', 'c2_ha', 'c2_va'
    ]
    sliders = create_sliders(fig, ax_mins[1], ax_maxs[1], slider_axes, names)

    # fig texts
    fig_txt = []
    
    def reset_axes2():
        ax2.clear()
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        ax2.set_zlabel('Z')
        ax2.plot([ax_mins[0], ax_maxs[0]], [0, 0], [0, 0], color='red')
        ax2.plot([0, 0], [ax_mins[0], ax_maxs[0]], [0, 0], color='green')
        ax2.plot([0, 0], [0, 0], [ax_mins[0], ax_maxs[0]], color='blue')
        for txt in fig.texts:
            txt.remove()
        fig.tight_layout()
        

    def plot_controls():
        if not visibility[labels.index('show_controls')]:
            for s in slider_axes:
                s.set_visible(False)
        else:
            for s in slider_axes:
                s.set_visible(True)
        b_axes.set_visible(True)
        

    def plot_vecs(vecs, origin, color):
        for i, v in enumerate(vecs):                
            [x, y, z] = v
            ax2.plot([origin[0]] + [x], [origin[1]] + [y], [origin[2]] + [z], color=color, linestyle='--')        
            ax2.plot(
                [v[0] for v in vecs] + [vecs[0][0]],
                [v[1] for v in vecs] + [vecs[0][1]],
                [v[2] for v in vecs] + [vecs[0][2]],
                color=color
            )

    def plot_intersection():        
        points, hull, score = inters.points, inters.hull, inters.score
        if not len(points):
            return
        
        points = np.array([list(point) for point in points])
        hull_volume = 0 if not hull else hull.volume
        s = 'i_score=%.2f\nhull volume=%.2f\nfrust union volume=%.2f\n' % (score, hull_volume, inters.frust_union_volume)
        plt.figtext(.4, .025, s) 
        if visibility[labels.index('show_inters_hull')]:
            ax2.plot_trisurf(points[:,0], points[:,1], points[:,2], triangles=hull.simplices, edgecolor='Gray')
            
        if visibility[labels.index('show_inters_points')]:
            ix, iy, iz = [p[0] for p in points],  [p[1] for p in points],  [p[2] for p in points]            
            ax2.scatter(ix, iy, iz, color='black', s=200, marker='o')            
            
    def plot_cameras():
        for camera, col in zip(inters.active_cameras, ['cyan', 'magenta']):
            plot_vecs(camera.curr_min_frust, camera.curr_origin, col)
            plot_vecs(camera.curr_max_frust, camera.curr_origin, col)
                
    def plot2():
        reset_axes2()
        plot_cameras()
        plot_intersection()
        fig.canvas.draw_idle()
        
    intersControl = IntersControl(cameras, inters)

    def checkbox_update(label):
        index = labels.index(label)
        visibility[index] = not visibility[index]
        intersControl.use_cpp = visibility[-1]
        plot2()
        
    check.on_clicked(checkbox_update)
        
    b_inters.on_clicked(intersControl.update)

    cameraControls = create_camera_controls(cameras, plot2)   
    for s, c in zip(sliders, cameraControls):
        s.on_changed(c.update)

    plot2()
    plt.show()    
    
if '__main__' == __name__:
    
    cameras = [Camera([0, 0], [20, 20], 'black', 0), Camera([0, 0], [20, 20], 'red', 0)]
    inters = Inters([])
    inters.active_cameras = cameras
    
    plot_frustrum(cameras, inters)
    
