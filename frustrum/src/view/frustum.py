from control.inters_control import IntersControl

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
    s_axes = [[.17, .95, .15, .01]]    
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

    fig = plt.figure(figsize=(10,6))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])
    ax_mins, ax_maxs = [-40, -20], [40, 20]
    [ax1, ax2] = [plt.subplot(gs[i], projection='3d') for i in range(2)]

    # Checkbuttons for visibility control
    rax = plt.axes([0.02, 0.8, 0.1, 0.15])
    labels = ['controls', 'view_poses', 'inters_points', 'inters_hull']
    visibility = [False, False, False, False]
    check = CheckButtons(rax, labels, visibility)

    # intersection button
    b_axes = fig.add_axes([.8, .93, .15, .03])
    b_inters = Button(b_axes, 'compute_intersection')

    # next button
    b1_axes = fig.add_axes([.9, .07, .07, .03])
    b1_nxt = Button(b1_axes, 'next')
    
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
    
    def reset_axes(ax):
        ax.clear()
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.plot([ax_mins[0], ax_maxs[0]], [0, 0], [0, 0], color='red')
        ax.plot([0, 0], [ax_mins[0], ax_maxs[0]], [0, 0], color='green')
        ax.plot([0, 0], [0, 0], [ax_mins[0], ax_maxs[0]], color='blue')
        for txt in fig.texts:
            txt.remove()
        fig.tight_layout()

    def plot_controls():
        controls_visibility = visibility[labels.index('controls')]
        for s in slider_axes:
            s.set_visible(controls_visibility)
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

    def plot_intersection(ax):        
        points, hull, score = inters.points, inters.hull, inters.score
        if not len(points):
            return
        
        points = np.array([list(point) for point in points])
        hull_volume = 0 if not hull else hull.volume
        views = ','.join([str(c.view_id) for c in inters.active_cameras])
        s = 'views=%s\ni_score=%.2f\nhull volume=%.2f\nfrust union volume=%.2f\nview_matches=%s' % (views, score, hull_volume, inters.frust_union_volume, inters.get_match())
        plt.figtext(.4, .025, s) 
        if visibility[labels.index('inters_hull')]:
            ax.plot_trisurf(points[:,0], points[:,1], points[:,2], triangles=hull.simplices, edgecolor='Gray')
            
        if visibility[labels.index('inters_points')]:
            ix, iy, iz = [p[0] for p in points],  [p[1] for p in points],  [p[2] for p in points]            
            ax.scatter(ix, iy, iz, color='black', s=200, marker='o')            
            
    def plot_cameras():
        for camera, col in zip(inters.active_cameras, ['cyan', 'magenta']):
            plot_vecs(camera.curr_min_frust, camera.curr_origin, col)
            plot_vecs(camera.curr_max_frust, camera.curr_origin, col)
                
    def plot_view_poses(ax):
                
        if visibility[labels.index('view_poses')]:
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
            
    def plot_active_camera_origins():
        if visibility[labels.index('view_poses')]:
            active_origins = [c.curr_origin for c in inters.active_cameras]
            ax1.scatter(
                [o[0] for o in active_origins],
                [o[1] for o in active_origins],
                [o[2] for o in active_origins],
                c='red', s=50, marker='o', picker=5
            )

    def plot1():
        reset_axes(ax1)
        plot_controls()
        plot_view_poses(ax1)
        plot_active_camera_origins()
        fig.canvas.draw_idle()

    def plot2():
        reset_axes(ax2)
        plot_cameras()
        plot_intersection(ax2)
        fig.canvas.draw_idle()
        
    def checkbox_update(label):
        index = labels.index(label)
        visibility[index] = not visibility[index]
        plot1()
        plot2()
        
    check.on_clicked(checkbox_update)
        
    intersControl = IntersControl(cameras, inters, [plot1, plot2])
    b_inters.on_clicked(intersControl.update)
    b1_nxt.on_clicked(intersControl.incrementAndUpdate)    

    cameraControls = create_camera_controls(cameras, plot2)   
    for s, c in zip(sliders, cameraControls):
        s.on_changed(c.update)

    def onpick(event):
        idx = event.ind[0]
        [x, y, z] = [int(v) for v in cameras[idx].curr_origin]
        if len(inters.active_cameras) == 0:
            inters.active_cameras.append(cameras[idx])
        elif len(inters.active_cameras) == 1:
            inters.active_cameras.append(cameras[idx])
        else:
            inters.active_cameras[0] = inters.active_cameras[1]
            inters.active_cameras[1] = cameras[idx]
        if len(inters.active_cameras) == 2:
            print(inters.active_cameras[0], inters.active_cameras[1])
        plot1()
        plot2()
        
    fig.canvas.mpl_connect('pick_event', onpick)
        
    plot1()
    plot2()
    plt.show()    
    
if '__main__' == __name__:

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--matches_file', required=True)
    parser.add_argument('--gps_file', required=True)
    parser.add_argument('--view1', required=False)
    parser.add_argument('--view2', required=False)
    args = parser.parse_args()

    inters = Inters(Inters.load_matches(args.matches_file))
    view_cameras = Camera.load_cameras(args.gps_file)
    if args.view1 and args.view2:
        v1, v2 = args.view1, args.view2
        inters.active_cameras = [view_cameras[v1], view_cameras[v2]]
    plot_frustrum(list(view_cameras.values()), inters)
    
