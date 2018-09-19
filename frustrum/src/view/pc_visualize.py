import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as a3
import numpy as np
import math
from random import randint

from plyfile import PlyData, PlyElement

if '__main__' == __name__:

    plydata = PlyData.read('/Users/karthikramachandran/projects/karamach/vision/frustrum/data/GUADALUPE_SPILLWAY_20180815_001_depth000.ply')

    data =  plydata.elements[0].data
    
    idx = [randint(0, len(data)) for i  in range(10000)]

    x_coords = [data[i]['x'] for i in idx]
    y_coords = [data[i]['y'] for i in idx]
    z_coords = [data[i]['z'] for i in idx]
    colors = [[data[i]['red'], data[i]['green'], data[i]['blue']] for i in idx]
        
    fig = plt.figure(figsize=(10,6))
    ax = plt.subplot(111, projection='3d')

    ax.scatter(x_coords, y_coords, z_coords, c=colors)

    '''
    for x, y, z, c in zip(x_coords, y_coords, z_coords, colors):        
        ax.scatter(x, y, z, color=c)
    '''
    plt.show()
    
    
