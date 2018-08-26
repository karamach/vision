import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider

import queue
import threading
import time

from model import Camera, Model

class View(object):

    def __init__(self, msg_q):
        self. msg_q = msg_q
        self.fig = plt.figure(figsize=(8,8))
        self.gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1])
        self.ax = plt.subplot(self.gs[0], projection='3d')
        self.ax_min, self.ax_max = 100, 100
        self.resetAxes()
        plt.show()

    def resetAxes(self):
        self.ax.clear()
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.plot([self.ax_min, self.ax_max], [0, 0], [0, 0], color='red')
        self.ax.plot([0, 0], [self.ax_min, self.ax_max], [0, 0], color='green')
        self.ax.plot([0, 0], [0, 0], [self.ax_min, self.ax_max], color='blue')

    def _plotVecs(self, vecs, origin, color):
        for i, v in enumerate(vecs):                
            [x, y, z] = v
            self.ax.plot(
                [origin[0]] + [x],
                [origin[1]] + [y],
                [origin[2]] + [z],
                color=color, linestyle='--'
            )        
            self.ax.plot(
                [v[0] for v in vecs] + [vecs[0][0]],
                [v[1] for v in vecs] + [vecs[0][1]],
                [v[2] for v in vecs] + [vecs[0][2]],
                color=color
            )
        
    def plot(self):
            print('[ok][got model ..][cameras=%s]' % model.cameras)
            
'''            
            for camera in model.cameras:
                self._plotVecs(camera.curr_min_frust, camera.curr_origin, camera.color)
                self._plotVecs(camera.curr_max_frust, camera.curr_origin, camera.color)
'''

class Controller:

    def __init__(self, q, model):
        self.q = q
        self.model = model

    def run(self):
        print('start')
        import time
        c = self.model.cameras[0]
        for i in range(0, 50, 10):
            c.frust_range = [20, 40]            
            c.pose(c.curr_ypr, [i, c.curr_xyz[1], c.curr_xyz[2]])
            q.put(model, True)
            print('[ok][sent model ..]')
            time.sleep(3)                    
    
                
if '__main__' == __name__:

    from model import create_cameras
    
    cameras = create_cameras()
    model = Model(cameras)
    q = queue.Queue()
    view = View(q)
    cont = Controller(q, model)

    t = threading.Thread(target=cont.run)
    t.start()
    view.plot()
    q.join()
  
