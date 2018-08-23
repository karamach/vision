import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as a3
import numpy as np
import math
from matplotlib.widgets import Slider, Button, CheckButtons
import matplotlib.gridspec as gridspec
from geometry import Geometry
from model import Camera, Inters, create_model
from control import CameraTransControl, CameraRotControl, CameraFrustControl, IntersControl, CameraAngleControl
from scipy.spatial import ConvexHull
from matplotlib.patches import Polygon

def create_slider_axes(fig):
    s_axes = [[.7, .85, .15, .01]]    
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
    gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1])
    ax = plt.subplot(gs[0], projection='3d')
    ax_min, ax_max = -1000, 1000

    # Checkbuttons for visibility control
    rax = plt.axes([0.05, 0.8, 0.1, 0.15])
    labels = ['hull', 'points', 'min_frustum', 'max_frustum', 'axes_points', 'controls']
    visibility = [False, False, False, False, False, False]
    check = CheckButtons(rax, labels, visibility)

    # intersection button
    b_axes = fig.add_axes([.7, .9, .15, .05])
    b_inters = Button(b_axes, 'compute_intersection')

    # sliders
    slider_axes = create_slider_axes(fig)
    names = [
        'c1_x', 'c1_y', 'c1_z', 'c2_x', 'c2_y', 'c2_z',   
        'c1_yaw', 'c1_pitch', 'c1_roll', 'c2_yaw', 'c2_pitch', 'c2_roll',
        'c1_minf', 'c1_maxf', 'c2_minf', 'c2_maxf', 'c1_ha', 'c1_va', 'c2_ha', 'c2_va'
    ]
    sliders = create_sliders(fig, ax_min, ax_max, slider_axes, names)

    # point annotation
    annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    # fig texts
    fig_txt = []
    
    def reset_axes():
        ax.clear()
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.plot([ax_min, ax_max], [0, 0], [0, 0], color='red')
        ax.plot([0, 0], [ax_min, ax_max], [0, 0], color='green')
        ax.plot([0, 0], [0, 0], [ax_min, ax_max], color='blue')
        for txt in fig.texts:
            txt.remove()

    def plot_controls():
        if not visibility[labels.index('controls')]:
            for s in slider_axes:
                s.set_visible(False)
            b_axes.set_visible(False)
        else:
            for s in slider_axes:
                s.set_visible(True)
            b_axes.set_visible(True)
        

    def plot_vecs(vecs, origin, color):
        for i, v in enumerate(vecs):                
            [x, y, z] = v
            ax.plot([origin[0]] + [x], [origin[1]] + [y], [origin[2]] + [z], color=color, linestyle='--')        
            ax.plot(
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
        
        if visibility[labels.index('hull')]:
            plt.figtext(.7, .25, 'score=%.2f\nhull volume=%.2f\nfrust union volume=%.2f' % (score, hull.volume, inters.frust_union_volume))
            ax.plot_trisurf(points[:,0], points[:,1], points[:,2], triangles=hull.simplices, edgecolor='Gray')
            
        if visibility[labels.index('points')]:
            ix, iy, iz = [p[0] for p in points],  [p[1] for p in points],  [p[2] for p in points]            
            ax.scatter(ix, iy, iz, color='black', s=200, marker='o')            
            
    def plot_cameras():
        for camera in cameras:
            if visibility[labels.index('min_frustum')]:
                plot_vecs(camera.curr_min_frust, camera.curr_origin, camera.color)
            if visibility[labels.index('max_frustum')]:
                plot_vecs(camera.curr_max_frust, camera.curr_origin, camera.color)
        
        if visibility[labels.index('axes_points')]:
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

    def plot():
        reset_axes()
        plot_controls()
        plot_cameras()
        plot_intersection()
        fig.canvas.draw_idle()

    def checkbox_update(label):
        index = labels.index(label)
        visibility[index] = not visibility[index]
        plot()
        
    check.on_clicked(checkbox_update)
        
    intersControl = IntersControl(cameras, inters, plot)
    b_inters.on_clicked(intersControl.update)

    cameraControls = create_camera_controls(cameras, plot)   
    for s, c in zip(sliders, cameraControls):
        s.on_changed(c.update)

    def onpick(event):
        idx = event.ind[0]
        [x, y, z] = [int(v) for v in cameras[idx].curr_origin]
        ax.text(x, y, z, cameras[idx].pose_str(), size=10, zorder=1, color='k')
        fig.canvas.draw_idle()
        
    fig.canvas.mpl_connect('pick_event', onpick)

        
    plot()
    plt.show()    
    
if '__main__' == __name__:
    inters = Inters()
    cameras = Camera.load_cameras('./gps_fov.txt')
    plot_frustrum(cameras, inters)
    
