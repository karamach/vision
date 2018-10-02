from control.inters_control import IntersControl

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

from scipy.spatial import ConvexHull
from matplotlib.patches import Polygon

import argparse

def plot_frustrum(cameras, inters):
    
    fig = plt.figure(figsize=(10,6))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 3])
    ax_mins, ax_maxs = [-40, -20], [40, 20]
    [ax1, ax2] = [plt.subplot(gs[i], projection='3d') for i in range(2)]

    # Checkbuttons for visibility control
    rax = plt.axes([0.02, 0.8, 0.1, 0.15])
    labels = ['inters_points', 'inters_hull', 'compute_intersection', 'use_cpp']
    visibility = dict([(label, False) for label in labels])
    check = CheckButtons(rax, labels, [visibility[label] for label in labels])

    # next button
    b1_prev_axes = fig.add_axes([.83, .04, .07, .03])
    b1_prev = Button(b1_prev_axes, 'prev')    
    b1_nxt_axes = fig.add_axes([.9, .04, .07, .03])
    b1_nxt = Button(b1_nxt_axes, 'next')    

    # fig texts
    fig_txt = None

    # active camera pose plot
    active_camera_scatter = None

    def reset_axes(ax):
        ax.clear()
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.plot([ax_mins[0], ax_maxs[0]], [0, 0], [0, 0], color='red')
        ax.plot([0, 0], [ax_mins[0], ax_maxs[0]], [0, 0], color='green')
        ax.plot([0, 0], [0, 0], [ax_mins[0], ax_maxs[0]], color='blue')
        fig.tight_layout()

    def plot_vecs(vecs, origin, color):
        for i, v in enumerate(vecs):                
            [x, y, z, w] = v
            ax2.plot([origin[0]] + [x], [origin[1]] + [y], [origin[2]] + [z], color=color, linestyle='--')
            ax2.plot(
                [v[0] for v in vecs] + [vecs[0][0]],
                [v[1] for v in vecs] + [vecs[0][1]],
                [v[2] for v in vecs] + [vecs[0][2]],
                color=color
            )

    def plot_intersection(ax):
        nonlocal visibility
        if (not visibility['compute_intersection']):
            return
        
        intersControl.update()                    
        views = ','.join([str(c.view_id) for c in inters.active_cameras])
        points, hull, score = inters.points, inters.hull, inters.score
        if not len(points):
            s = 'views=%s\ni_score=%.2f\nview_matches=%s'
            s = s % (views, score,  inters.get_match())
            nonlocal fig_txt
            if fig_txt:
                fig_txt.remove()            
            fig_txt = plt.figtext(.4, .025, s) 
            return
        
        points = np.array([list(point) for point in points])
        if visibility['inters_hull']:
            ax.plot_trisurf(points[:,0], points[:,1], points[:,2], triangles=hull.simplices, edgecolor='Gray')
            
        if visibility['inters_points']:
            ix, iy, iz = [p[0] for p in points],  [p[1] for p in points],  [p[2] for p in points]            
            ax.scatter(ix, iy, iz, color='black', s=200, marker='o')            
            
    def plot_cameras():
        for camera, col in zip(inters.active_cameras, ['cyan', 'magenta']):
            curr_min_frust, curr_max_frust = camera.getFrustums()
            plot_vecs(curr_min_frust, camera.getOrigin(), col)
            plot_vecs(curr_max_frust, camera.getOrigin(), col)


    def plot_view_poses(ax):
                
        origins = [c.getOrigin() for c in cameras]
        a_points = [c.getAxesPoints() for c in cameras]
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
            
    def plot_active_camera_origins():
        nonlocal active_camera_scatter
        nonlocal ax1
        
        active_origins = [c.getOrigin() for c in inters.active_cameras]
        if active_camera_scatter:
            active_camera_scatter.remove()
        active_camera_scatter = ax1.scatter(
            [o[0] for o in active_origins],
            [o[1] for o in active_origins],
            [o[2] for o in active_origins],
            c='red', s=50, marker='o', picker=5
        )            

    def plot_data():
        views = ','.join([str(c.view_id) for c in inters.active_cameras])
        s = 'views=%s\ni_score=%.2f\nview_matches=%s' % (views, inters.score, inters.get_match())
        nonlocal fig_txt
        if fig_txt:
            fig_txt.remove()
        fig_txt = plt.figtext(.4, .025, s)

    def plot2():
        reset_axes(ax2)
        plot_cameras()
        
    def checkbox_update(label):
        visibility[label] = not visibility[label]
        intersControl.use_cpp = visibility['use_cpp']
        plot2()
        
    check.on_clicked(checkbox_update)
        
    intersControl = IntersControl(cameras, inters)
    intersControl.use_cpp = visibility['use_cpp']

    def onnext(val):
        nonlocal intersControl
        nonlocal visibility
        intersControl.incrementAndUpdate(visibility['compute_intersection'])
        plot_active_camera_origins()
        plot_data()
        plot2()
        fig.canvas.draw_idle()        
    
    b1_nxt.on_clicked(onnext)    

    def onpick(event):
        idx = event.ind[0]
        [x, y, z, w] = [int(v) for v in cameras[idx].getOrigin()]
        if len(inters.active_cameras) == 0:
            inters.active_cameras.append(cameras[idx])
        elif len(inters.active_cameras) == 1:
            inters.active_cameras.append(cameras[idx])
        else:
            inters.active_cameras[0] = inters.active_cameras[1]
            inters.active_cameras[1] = cameras[idx]
        if len(inters.active_cameras) == 2:
            print(inters.active_cameras[0], inters.active_cameras[1])

        plot_active_camera_origins()
        
        reset_axes(ax2)
        plot_cameras()
        plot_intersection(ax2)
        plot_data()
        
    fig.canvas.mpl_connect('pick_event', onpick)

    plot_view_poses(ax1)
    plot_active_camera_origins()
    
    reset_axes(ax2)
    plot_cameras()
    plot_intersection(ax2)
    plot_data()
    
    plt.show()    
