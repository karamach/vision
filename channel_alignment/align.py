import os
import sys
from functools import reduce
import scipy.io
import matplotlib.pyplot as plt
import numpy
import cv2

# Sum of squared difference
def compute_ssd(arr1, arr2):
    return numpy.sum((arr1-arr2)**2)

# Normalized cross correlation arr1.arr2/(|arr1||arr2|) # TODO Needs fix
def compute_ncc(arr1, arr2):
    norm_arr1 = arr1/numpy.sqrt(numpy.sum(arr1 ** 2))
    norm_arr2 = arr2/numpy.sqrt(numpy.sum(arr2 ** 2))    
    return numpy.sum(numpy.multiply(norm_arr1, norm_arr2))

def load_data(data):
    red = scipy.io.loadmat(os.path.join(data, 'red.mat'))
    blue = scipy.io.loadmat(os.path.join(data, 'blue.mat'))
    green = scipy.io.loadmat(os.path.join(data, 'green.mat'))
    return numpy.array(red['red']), numpy.array(green['green']), numpy.array(blue['blue'])

def pad(arr, s_window):
    n_r, n_c = arr.shape
    padded = numpy.zeros((n_r+2*s_window, n_c+2*s_window))
    padded[s_window:n_r+s_window, s_window:n_c+s_window] = arr
    return padded

def compute_best_fit(arr1, arr2, s_window):
    n_r, n_c = arr1.shape
    best_i, best_j, min_eval =  0, 0, sys.maxsize
    for i in range(2*s_window):
        for j in range(2*s_window):
            eval_score = compute_ssd(arr1, arr2[i:i+n_r, j:j+n_c])
            #eval_score = compute_ncc(arr1, arr2[i:i+n_r, j:j+n_c])  # TODO needs fix
            if eval_score < min_eval:
                best_i, best_j, min_eval = i, j, eval_score
    return best_i, best_j, min_eval

def find_best_alignment(r, g, b, s_window):
    n_r, n_c = r.shape

    # use blue as the base, expand blue for easy comparison
    b_padded = pad(b, s_window)
    print('[Pad_b .. OK]')

    # calculate minssd and best i, j for r-b alignment    
    r_best = compute_best_fit(r, b_padded, s_window)
    print ('[ComputeSSD_r_b .. OK][best_ri=%d][best_rj=%d][minr_ssd=%d]' % (r_best[0], r_best[1], r_best[2]))
                              
    # calculate minssd and best i, j for g-b alignment    
    g_best = compute_best_fit(g, b_padded, s_window)
    print ('[ComputeSSD_g_b .. OK][best_gi=%d][best_gj=%d][ming_ssd=%d]' % (g_best[0], g_best[1], g_best[2]))

    return {'rb': r_best, 'gb': g_best}        

def align(r, g, b, best_alignment, s_window):

    b_padded = pad(b, s_window)
    rgb = numpy.zeros((b_padded.shape[0], b_padded.shape[1], 3), dtype=numpy.uint8)
    rgb[:, :, 2] = b_padded

    # rb best alignment
    row_rb, col_rb, _ = best_alignment['rb']
    rgb[row_rb:row_rb+r.shape[0], col_rb:col_rb+r.shape[1], 0] = r

    # gb best alignment
    row_gb, col_gb, _ = best_alignment['gb']
    rgb[row_gb:row_gb+g.shape[0], col_gb:col_gb+g.shape[1], 1] = g

    # limit output to actual size before padding
    return rgb[s_window:s_window+b.shape[0], s_window:s_window+b.shape[1], :]

def show(img):
    plt.imshow(img)
    plt.show()

if '__main__' == __name__:
    s_window = 30
    r, g, b = load_data('./data')
    best_alignment = find_best_alignment(r, g, b, s_window)
    rgb = align(r, g, b, best_alignment, s_window)
    show(rgb)
