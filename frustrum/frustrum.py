import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import math
from matplotlib.widgets import Slider
import matplotlib.gridspec as gridspec
from utils import Geometry

class Camera(object):

    def __init__(self, frust_range, angs, color='black'):
        self.origin = [0, 0, 0]
        self.h_ang = angs[0]
        self.v_ang = angs[1]
        self.color = color
        self.unit_frust = np.array([
            [1, math.tan(self.h_ang/2), math.tan(self.v_ang/2)],
            [1, -math.tan(self.h_ang/2), math.tan(self.v_ang/2)],
            [1, -math.tan(self.h_ang/2), -math.tan(self.v_ang/2)],
            [1, math.tan(self.h_ang/2), -math.tan(self.v_ang/2)],
        ])
        self.frust_range = frust_range
        self.min_frust, self.max_frust = Camera._update_frust(self.frust_range, self.unit_frust)

        self.curr_origin = self.origin
        self.curr_min_frust = self.min_frust
        self.curr_max_frust = self.max_frust

        self.curr_ypr = [0, 0, 0]
        self.curr_xyz = [0, 0, 0]

    @staticmethod
    def _update_frust(frust_range, unit_frust):
        min_frust = [frust_range[0]*p for p in unit_frust]
        max_frust = [frust_range[1]*p for p in unit_frust]
        return min_frust, max_frust
                
    def pose(self, ypr, xyz):
        self.min_frust, self.max_frust = Camera._update_frust(self.frust_range, self.unit_frust)        
        [o, min_f, max_f] = [self.origin, self.min_frust, self.max_frust]
        [o], min_f, max_f = Geometry.rot([o], ypr), Geometry.rot(min_f, ypr), Geometry.rot(max_f, ypr)
        [o], min_f, max_f =  Geometry.trans([o], xyz), Geometry.trans(min_f, xyz),  Geometry.trans(max_f, xyz)
        self.curr_origin, self.curr_min_frust, self.curr_max_frust = o, min_f, max_f
        self.curr_ypr, self.curr_xyz = ypr, xyz
        return o, min_f, max_f

class CameraTransControl(object):

    def __init__(self, cameras, idx, ax_idx, slider, fig, handler, ax):
        self.cameras = cameras
        self.idx = int(idx)
        print(self.idx)
        self.fig = fig
        self.handler = handler
        self.ax = ax
        self.ax_idx = ax_idx
        slider.on_changed(self.update)    

    def update(self, val):
        ypr = self.cameras[self.idx].curr_ypr
        xyz = self.cameras[self.idx].curr_xyz
        xyz[self.ax_idx] = val
        self.cameras[self.idx].pose(ypr, xyz)
        self.handler(self.cameras, self.ax)
        self.fig.canvas.draw_idle()

class CameraRotControl(object):

    def __init__(self, cameras, idx, ax_idx, slider, fig, handler, ax):
        self.cameras = cameras
        self.idx = int(idx)
        self.fig = fig
        self.handler = handler
        self.ax = ax
        self.ax_idx = ax_idx
        slider.on_changed(self.update)    

    def update(self, val):
        print('cam_idx  %s' % self.idx)
        ypr = self.cameras[self.idx].curr_ypr
        ypr[self.ax_idx] = math.radians(val)
        xyz = self.cameras[self.idx].curr_xyz
        self.cameras[self.idx].pose(ypr, xyz)
        self.handler(self.cameras, self.ax)
        self.fig.canvas.draw_idle()

class CameraFrustControl(object):

    def __init__(self, cameras, idx, ax_idx, slider, fig, handler, ax):
        self.cameras = cameras
        self.idx = int(idx)
        self.fig = fig
        self.handler = handler
        self.ax = ax
        self.ax_idx = ax_idx
        slider.on_changed(self.update)    

    def update(self, val):
        self.cameras[self.idx].frust_range[self.ax_idx] = val
        ypr = self.cameras[self.idx].curr_ypr
        xyz = self.cameras[self.idx].curr_xyz
        self.cameras[self.idx].pose(ypr, xyz)
        self.handler(self.cameras, self.ax)
        self.fig.canvas.draw_idle()        
        

def get_slider_axes_dims(num_sliders):
    s_axes = [[.7, .85, .15, .01]]
    for i in range(num_sliders-1):
        prev = s_axes[-1]
        s_axes.append([prev[0], prev[1]-.05, prev[2], prev[3]])
    return s_axes    
    
def plot_frustrum(cameras):

    fig = plt.figure(figsize=(8,8))
    gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1])
    ax1 = plt.subplot(gs[0], projection='3d')

    ax_min, ax_max = 0, 200
    
    def reset_axes(ax):
        ax.clear()
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.plot([ax_min, ax_max], [0, 0], [0, 0], color='red')
        ax.plot([0, 0], [ax_min, ax_max], [0, 0], color='green')
        ax.plot([0, 0], [0, 0], [ax_min, ax_max], color='blue')

    def plot_cameras(cameras, ax):
        reset_axes(ax)
        for camera in cameras:
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

            plot_vecs(camera.curr_min_frust, camera.curr_origin, camera.color)
            plot_vecs(camera.curr_max_frust, camera.curr_origin, camera.color)

    names = [
        'c1_x', 'c1_y', 'c1_z', 'c2_x', 'c2_y', 'c2_z',   
        'c1_yaw', 'c1_pitch', 'c1_roll', 'c2_yaw', 'c2_pitch', 'c2_roll',
        'c1_minf', 'c1_maxf', 'c2_minf', 'c2_maxf'
    ]


    slider_axes = get_slider_axes_dims(16)
    
    sliders = [
        Slider(plt.axes(a, facecolor='lightgoldenrodyellow'), names[i], ax_min, ax_max, valinit=0, valstep=1) for i, a in enumerate(slider_axes[:6])
    ]
    sliders += [
        Slider(plt.axes(a, facecolor='lightgoldenrodyellow'), names[i+6], -180, +180, valinit=0, valstep=1) for i, a in enumerate(slider_axes[6:12])
    ]
    sliders += [
        Slider(plt.axes(a, facecolor='lightgoldenrodyellow'), names[i+12], ax_min, ax_max, valinit=0, valstep=1) for i, a in enumerate(slider_axes[12:])
    ]
    
    cameraOriginControls = [
        CameraTransControl(cameras, i/3, i%3, sliders[i], fig, plot_cameras, ax1) for i in range(6)
    ]
    cameraRotControls = [
        CameraRotControl(cameras, (i-6)/3, i%3, sliders[i], fig, plot_cameras, ax1) for i in range(6, 12)
    ]
    cameraFrustControls = [
        CameraFrustControl(cameras, (i-12)/2, i%2, sliders[i], fig, plot_cameras, ax1) for i in range(12, 16)
    ]
    

    plot_cameras(cameras, ax1)
    plt.show()    



def get_slider_axes_dims(num_sliders):
    s_axes = [[.7, .85, .15, .01]]
    for i in range(num_sliders-1):
        prev = s_axes[-1]
        s_axes.append([prev[0], prev[1]-.05, prev[2], prev[3]])
    return s_axes    
    

        
if '__main__' == __name__:

    def rads(angles):
        return [math.radians(a) for a in angles]
    
    colors = ['black', 'magenta']
    frust = [[0, 0], [0, 0]]
    angs = [
        [math.radians(45), math.radians(45)],
        [math.radians(45), math.radians(45)]
    ]
    cameras = [
        Camera(frust_range, angs, color)
        for frust_range, angs, color in zip(frust, angs, colors)
    ]
    
    plot_frustrum(cameras)
    

