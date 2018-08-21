import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as a3
import numpy as np
import math
from matplotlib.widgets import Slider, Button
import matplotlib.gridspec as gridspec
from geometry import Geometry
from model import Camera, Inters, create_model
from control import CameraTransControl, CameraRotControl, CameraFrustControl, IntersControl, CameraAngleControl
from scipy.spatial import ConvexHull
from matplotlib.patches import Polygon

def create_sliders(fig, ax_min, ax_max):
    names = [
        'c1_x', 'c1_y', 'c1_z', 'c2_x', 'c2_y', 'c2_z',   
        'c1_yaw', 'c1_pitch', 'c1_roll', 'c2_yaw', 'c2_pitch', 'c2_roll',
        'c1_minf', 'c1_maxf', 'c2_minf', 'c2_maxf', 'c1_ha', 'c1_va', 'c2_ha', 'c2_va'
    ]
    
    s_axes = [[.7, .85, .15, .01]]    
    for i in range(19):
        prev = s_axes[-1]
        s_axes.append([prev[0], prev[1]-.02, prev[2], prev[3]])

    sliders = [
        Slider(fig.add_axes(a, facecolor='lightgoldenrodyellow'), names[i], ax_min, ax_max, valinit=0, valstep=1)
        for i, a in enumerate(s_axes[:6])
    ]
    sliders += [
        Slider(fig.add_axes(a, facecolor='lightgoldenrodyellow'), names[i+6], -180, +180, valinit=0, valstep=1)
        for i, a in enumerate(s_axes[6:12])
    ]
    sliders += [
        Slider(fig.add_axes(a, facecolor='lightgoldenrodyellow'), names[i+12], 0, 2*ax_max, valinit=0, valstep=1)
        for i, a in enumerate(s_axes[12:16])
    ]
    sliders += [
        Slider(fig.add_axes(a, facecolor='lightgoldenrodyellow'), names[i+16], 0, 180 , valinit=0, valstep=1)
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


def plot_frustrum():

    cameras, inters = create_model()

    fig = plt.figure(figsize=(10,6))
    gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1])
    ax = plt.subplot(gs[0], projection='3d')
    ax_min, ax_max = -200, 200

    # intersection button
    s_axes = [.7, .9, .15, .05]            
    b_inters = Button(fig.add_axes(s_axes), 'hide_intersection' if inters.state else 'show_intersection')

    # sliders
    sliders = create_sliders(fig, ax_min, ax_max)
    
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
        b_inters.label.set_text( 'hide_intersection' if inters.state else 'show_intersection')            

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

    def plot_axes_points(c):
        o = c.curr_origin
        [x, y, z] = c.curr_axes_points
        ax.plot([o[0]] + [x[0]], [o[1]] + [x[1]], [o[2]] + [x[2]], color='red', linestyle='-')        
        ax.plot([o[0]] + [y[0]], [o[1]] + [y[1]], [o[2]] + [y[2]], color='green', linestyle='-')        
        ax.plot([o[0]] + [z[0]], [o[1]] + [z[1]], [o[2]] + [z[2]], color='blue', linestyle='-')        
        

    def plot_intersection():
        points, hull, score = inters.points, inters.hull, inters.score
        if len(points) > 0:
            ix, iy, iz = [p[0] for p in points],  [p[1] for p in points],  [p[2] for p in points]            
            ax.scatter(ix, iy, iz, color='red', marker='o')
            points = np.array([list(point) for point in points])
            plt.figtext(.7, .25, 'score=%.2f\nhull volume=%.2f\nfrust union volume=%.2f' % (score, hull.volume, inters.frust_union_volume))
            ax.plot_trisurf(points[:,0], points[:,1], points[:,2], triangles=hull.simplices, edgecolor='Gray')                
            
    def plot_cameras():
        for camera in cameras:
            plot_vecs(camera.curr_min_frust, camera.curr_origin, camera.color)
            plot_vecs(camera.curr_max_frust, camera.curr_origin, camera.color)
            plot_axes_points(camera)

    def plot():
        reset_axes()
        plot_cameras()
        plot_intersection()
        fig.canvas.draw_idle()

    intersControl = IntersControl(cameras, inters, plot)
    b_inters.on_clicked(intersControl.update)

    cameraControls = create_camera_controls(cameras, plot)   
    for s, c in zip(sliders, cameraControls):
        s.on_changed(c.update)
    
    plot()
    plt.show()    
    
if '__main__' == __name__:

    plot_frustrum()
    
