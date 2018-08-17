import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import math
from matplotlib.widgets import Slider, Button
import matplotlib.gridspec as gridspec
from geometry import Geometry
from model import Camera, Inters
from control import CameraTransControl, CameraRotControl, CameraFrustControl, IntersControl
from scipy.spatial import ConvexHull


def create_sliders(fig, ax_min, ax_max):
    names = [
        'c1_x', 'c1_y', 'c1_z', 'c2_x', 'c2_y', 'c2_z',   
        'c1_yaw', 'c1_pitch', 'c1_roll', 'c2_yaw', 'c2_pitch', 'c2_roll',
        'c1_minf', 'c1_maxf', 'c2_minf', 'c2_maxf'
    ]
    
    s_axes = [[.7, .85, .15, .01]]    
    for i in range(15):
        prev = s_axes[-1]
        s_axes.append([prev[0], prev[1]-.05, prev[2], prev[3]])

    sliders = [
        Slider(fig.add_axes(a, facecolor='lightgoldenrodyellow'), names[i], ax_min, ax_max, valinit=0, valstep=1)
        for i, a in enumerate(s_axes[:6])
    ]
    sliders += [
        Slider(fig.add_axes(a, facecolor='lightgoldenrodyellow'), names[i+6], -180, +180, valinit=0, valstep=1)
        for i, a in enumerate(s_axes[6:12])
    ]
    sliders += [
        Slider(fig.add_axes(a, facecolor='lightgoldenrodyellow'), names[i+12], ax_min, ax_max, valinit=0, valstep=1)
        for i, a in enumerate(s_axes[12:])
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
    return cameraControls

def plot_frustrum(cameras, inters):

    fig = plt.figure(figsize=(8,8))
    gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1])
    ax = plt.subplot(gs[0], projection='3d')
    ax_min, ax_max = 0, 200
    
    def reset_axes(ax):
        ax.clear()
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.plot([ax_min, ax_max], [0, 0], [0, 0], color='red')
        ax.plot([0, 0], [ax_min, ax_max], [0, 0], color='green')
        ax.plot([0, 0], [0, 0], [ax_min, ax_max], color='blue')

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

    def get_sphere_points(r, c):
        # draw sphere
        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        x = r*np.cos(u)*np.sin(v) + c[0]
        y = r*np.sin(u)*np.sin(v) + c[1]
        z = r*np.cos(v) + c[2]
        return x, y, z
            
    def plot_intersection():
        points, radius, origin = inters.points, inters.radius, inters.origin     
        if len(points) > 0:
            ix, iy, iz = [p[0] for p in points],  [p[1] for p in points],  [p[2] for p in points]
            print(radius, origin)
            x, y, z = get_sphere_points(radius, origin)
            ax.plot_wireframe(x, y, z, color='red')
            ax.scatter(ix, iy, iz, color='black', marker='o')
            
    def plot_cameras():
        for camera in cameras:
            plot_vecs(camera.curr_min_frust, camera.curr_origin, camera.color)
            plot_vecs(camera.curr_max_frust, camera.curr_origin, camera.color)

    def plot():
        reset_axes(ax)
        plot_cameras()
        plot_intersection()
        fig.canvas.draw_idle()


    cameraControls = create_camera_controls(cameras, plot)   
    sliders = create_sliders(fig, ax_min, ax_max)
    for s, c in zip(sliders, cameraControls):
        s.on_changed(c.update)
    intersControl = IntersControl(cameras, inters, plot)

    s_axes = [.1, .9, .15, .05]            
    b_inters = Button(fig.add_axes(s_axes), 'show_inters')
    b_inters.on_clicked(intersControl.update)
    
    plot()
    plt.show()    
    
if '__main__' == __name__:

    def rads(angles):
        return [math.radians(a) for a in angles]
    
    colors = ['magenta', 'cyan']
    frust = [[0, 0], [0, 0]]
    angs = [
        [math.radians(45), math.radians(45)],
        [math.radians(45), math.radians(45)]
    ]
    cameras = [
        Camera(frust_range, angs, color)
        for frust_range, angs, color in zip(frust, angs, colors)
    ]
    inters = Inters()
    
    plot_frustrum(cameras, inters)
    
