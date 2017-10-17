import math

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2

class Utils(object):

    @staticmethod
    def load_image(img_path):
        return mpimg.imread(img_path)

    @staticmethod
    def show_image(img):
        plt.imshow(img)
        plt.show()

    @staticmethod
    def gray_scale(img):
        return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    @staticmethod
    def get_slope(x1, y1, x2, y2):
        (xdiff, ydiff) = (x1-x2, y2-y1) if y1<y2 else (x2-x1, y1-y2)
        return math.atan2(ydiff, xdiff)


if '__main__' == __name__:
    img = Utils.load_image('../data/solidWhiteRight.jpg')
    Utils.show_image(img)
    #Utils.show_image(Utils.gray_scale(img))
    
