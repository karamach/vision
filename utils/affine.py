import math
import numpy
from scipy.misc import imread
from skimage.color import rgb2gray
import matplotlib.pyplot as plt

# Affine = Trans * Scaling * Rot * Trans
def create_affine_transform_mat(tx1, ty1, scale, rot, tx2, ty2):
    t1 = numpy.array([[1, 0, tx1], [0, 1 , ty1], [0, 0, 1]])
    s = numpy.array([[scale, 0, 0], [0, scale , 0], [0, 0, 1]])
    r = numpy.array([[math.cos(rot), -math.sin(rot), 0], [math.sin(rot), math.cos(rot), 0], [0, 0, 1]])
    t2 = numpy.array([[1, 0, tx2], [0,1 , ty2], [0, 0, 1]])
    return numpy.dot(numpy.dot(numpy.dot(t1, s), r), t2) 

def compute_affine_singlepixel(p_dst, out_img, img, A_inv):
    out_size = out_img.shape
    p_src = numpy.round(numpy.dot(A_inv, p_dst))
    if (p_src[0] >= 0 and p_src[0] < out_size[1] and p_src[1] >= 0 and p_src[1] < out_size[0]):
        out_img[p_dst[1]:p_dst[1]+1, p_dst[0]:p_dst[0]+1] = img[p_src[1]:p_src[1]+1, p_src[0]:p_src[0]+1]

# p_dest = A*p_src for gray scale input img
def compute_affine(img, A, out_size):
    A_inv = numpy.linalg.inv(A)
    out_img = numpy.zeros(out_size)
    [[compute_affine_singlepixel(numpy.transpose(numpy.array([j, i, 1])), out_img, img, A_inv) for j in range(out_size[1])] for i in range(out_size[0])]
    return out_img    

def show(img):
    plt.imshow(img, cmap='gray')
    plt.show()

if '__main__' == __name__:
    img = imread('data/mug.jpg')
    gray_img = rgb2gray(img)

    # rotate 30 degrees around center and scale to .8 size
    A = create_affine_transform_mat(gray_img.shape[1]/2, gray_img.shape[0]/2, .8, -3.14*30/180, -gray_img.shape[1]/2, -gray_img.shape[0]/2)
    out_img = compute_affine(gray_img, A, gray_img.shape)
    show(out_img)    
