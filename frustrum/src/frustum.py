import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as a3
import numpy as np
import math
from matplotlib.widgets import Slider, Button, CheckButtons
import matplotlib.gridspec as gridspec
from geometry import Geometry

from model.camera import Camera
from model.inters import Inters

from control.pose_control import CameraTransControl, CameraRotControl
from control.frust_control import CameraFrustControl
from control.inters_control import IntersControl
from control.angle_control import CameraAngleControl

from scipy.spatial import ConvexHull
from matplotlib.patches import Polygon

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


def plot_frustrum(camera, inters):

    fig = plt.figure(figsize=(10,6))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])
    ax1 = plt.subplot(gs[0], projection='3d')
    ax2 = plt.subplot(gs[1], projection='3d')
    ax_mins = [-40, -20]
    ax_maxs = [40, 20]

    # Checkbuttons for visibility control
    rax = plt.axes([0.02, 0.8, 0.1, 0.15])
    labels = ['controls', 'view_poses', 'inters_points', 'inters_hull']
    visibility = [False, False, False, False]
    check = CheckButtons(rax, labels, visibility)

    # intersection button
    b_axes = fig.add_axes([.8, .93, .15, .03])
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
    
    def reset_axes1():
        ax1.clear()
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_zlabel('Z')
        ax1.plot([ax_mins[0], ax_maxs[0]], [0, 0], [0, 0], color='red')
        ax1.plot([0, 0], [ax_mins[0], ax_maxs[0]], [0, 0], color='green')
        ax1.plot([0, 0], [0, 0], [ax_mins[0], ax_maxs[0]], color='blue')
        for txt in fig.texts:
            txt.remove()
        fig.tight_layout()

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
        if not visibility[labels.index('controls')]:
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
        s = 'view_matches=%s\nscore=%.2f\nhull volume=%.2f\nfrust union volume=%.2f' % (inters.get_match(), score, hull.volume, inters.frust_union_volume)
        plt.figtext(.4, .05, s) 
        if visibility[labels.index('inters_hull')]:
            ax2.plot_trisurf(points[:,0], points[:,1], points[:,2], triangles=hull.simplices, edgecolor='Gray')
            
        if visibility[labels.index('inters_points')]:
            ix, iy, iz = [p[0] for p in points],  [p[1] for p in points],  [p[2] for p in points]            
            ax2.scatter(ix, iy, iz, color='black', s=200, marker='o')            
            
    def plot_cameras():
        for camera, col in zip(inters.active_cameras, ['cyan', 'magenta']):
            plot_vecs(camera.curr_min_frust, camera.curr_origin, col)
            plot_vecs(camera.curr_max_frust, camera.curr_origin, col)
                
    def plot_view_poses():
                
        if visibility[labels.index('view_poses')]:
            origins = [c.curr_origin for c in cameras]
            a_points = [c.curr_axes_points for c in cameras]
            for o, [x, y, z] in zip(origins, a_points):
                ax1.plot([o[0]] + [x[0]], [o[1]] + [x[1]], [o[2]] + [x[2]], color='red', linestyle='-')        
                ax1.plot([o[0]] + [y[0]], [o[1]] + [y[1]], [o[2]] + [y[2]], color='green', linestyle='-')        
                ax1.plot([o[0]] + [z[0]], [o[1]] + [z[1]], [o[2]] + [z[2]], color='blue', linestyle='-')
                
            ax1.scatter(
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
        reset_axes1()
        plot_controls()
        plot_view_poses()
        plot_active_camera_origins()
        fig.canvas.draw_idle()

    def plot2():
        reset_axes2()
        plot_cameras()
        plot_intersection()
        fig.canvas.draw_idle()
        

    def checkbox_update(label):
        index = labels.index(label)
        visibility[index] = not visibility[index]
        plot1()
        plot2()
        
    check.on_clicked(checkbox_update)
        
    intersControl = IntersControl(cameras, inters, plot2)
    b_inters.on_clicked(intersControl.update)

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
    inters = Inters('../data/view_matches.txt')
    cameras = Camera.load_cameras('../data/gps_fov.txt')
    plot_frustrum(cameras, inters)
    
