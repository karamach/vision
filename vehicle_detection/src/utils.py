from os import listdir
from os.path import isfile, join
import os

from sklearn.preprocessing import StandardScaler
from sklearn.cross_validation import train_test_split
import matplotlib.pyplot as plt
import scipy.ndimage
import scipy.misc
import cv2
import numpy as np

class Utils(object):

    conv_map = {('RGB', 'HSV'): cv2.COLOR_RGB2HSV,
                ('RGB', 'LUV'): cv2.COLOR_RGB2LUV,
                ('RGB', 'HLS'): cv2.COLOR_RGB2HLS,
                ('RGB', 'YUV'): cv2.COLOR_RGB2YUV,
                ('RGB', 'HSV'): cv2.COLOR_RGB2HSV,
                ('RGB', 'Gray'): cv2.COLOR_RGB2GRAY,
                ('RGB', 'BGR'): cv2.COLOR_RGB2BGR,
                ('BGR', 'HSV'): cv2.COLOR_BGR2HSV,
                ('BGR', 'LUV'): cv2.COLOR_BGR2LUV,
                ('BGR', 'HLS'): cv2.COLOR_BGR2HLS,
                ('BGR', 'YUV'): cv2.COLOR_BGR2YUV,
                ('BGR', 'HSV'): cv2.COLOR_BGR2HSV,
                ('BGR', 'Gray'): cv2.COLOR_BGR2GRAY,
                ('BGR', 'RGB'): cv2.COLOR_BGR2RGB,
                ('Gray', 'RGB'): cv2.COLOR_GRAY2RGB
                }

    def __init__(self):
        pass

    @staticmethod
    def show_image(img, cmap=''):
        if cmap == '':
            plt.imshow(img)
        else:
            plt.imshow(img, cmap)
        plt.show()

    @staticmethod
    def show_images(imgs, cmap=''):
        fig, axes = plt.subplots(nrows=len(imgs))
        for ax, img in zip(axes, imgs):
            ax.imshow(img)
        plt.show()

    @staticmethod
    def read_image(path):
        return scipy.ndimage.imread(path)

    @staticmethod
    def write_image(img, path):
        #cv2.imwrite(path, img)
        scipy.misc.imsave(path, img)

    @staticmethod
    def convert_image(img, src, dst):

        if src == dst:
            return img
        elif (src, dst) in Utils.conv_map:
            return cv2.cvtColor(img, Utils.conv_map[(src, dst)])
        else:
            return None

    @staticmethod
    def list_files(paths):
        files = []
        for path in paths:
            items = [join(path, f) for f in listdir(path) if isfile(join(path, f))]
            for item in items:
                files.append(item)
        files = list(filter(lambda name: '.jpg' in name or '.png' in name or '.jpeg' in name, files))
        return files

    @staticmethod
    def feature_scaler(feature_list):
        x = np.vstack(feature_list).astype(np.float64)
        scaler = StandardScaler().fit(x)
        scaled_x = scaler.transform(x)
        return scaled_x, scaler

    @staticmethod
    def split_data(scaled_x, y, test_size, rand_state):
        x_train, x_test, y_train, y_test = train_test_split(scaled_x, y, test_size=test_size, random_state=rand_state)
        return x_train, x_test, y_train, y_test

    @staticmethod
    def slide_window(img, x_start_stop, y_start_stop, xy_window, xy_overlap):

        if x_start_stop[0] is None:
            x_start_stop[0] = 0
        if x_start_stop[1] is None:
            x_start_stop[1] = img.shape[1]
        if y_start_stop[0] is None:
            y_start_stop[0] = 0
        if y_start_stop[1] is None:
            y_start_stop[1] = img.shape[0]

        # Compute the span of the region to be searched
        xspan = x_start_stop[1] - x_start_stop[0]
        yspan = y_start_stop[1] - y_start_stop[0]

        # Compute the number of pixels per step in x/y
        nx_pix_per_step = np.int(xy_window[0] * (1 - xy_overlap[0]))
        ny_pix_per_step = np.int(xy_window[1] * (1 - xy_overlap[1]))

        # Compute the number of windows in x/y
        nx_buffer = np.int(xy_window[0] * (xy_overlap[0]))
        ny_buffer = np.int(xy_window[1] * (xy_overlap[1]))
        nx_windows = np.int((xspan - nx_buffer) / nx_pix_per_step)
        ny_windows = np.int((yspan - ny_buffer) / ny_pix_per_step)

        # Loop through finding x and y window positions
        window_list = []
        for ys in range(ny_windows):
            for xs in range(nx_windows):
                # Calculate window position
                startx, starty = xs * nx_pix_per_step + x_start_stop[0], ys * ny_pix_per_step + y_start_stop[0]
                endx, endy = startx + xy_window[0], starty + xy_window[1]
                window_list.append(((startx, starty), (endx, endy)))

        return window_list

    @staticmethod
    def draw_boxes(img, bboxes, color=(0, 0, 255), thick=6):
        imcopy = np.copy(img)
        for bbox in bboxes:
            cv2.rectangle(imcopy, bbox[0], bbox[1], color, thick)
        return imcopy

    @staticmethod
    def draw_labeled_bboxes(img, labels):
        for object in range(1, labels[1]+1):
            # Find pixels with each object label value
            nonzero = (labels[0] == object).nonzero()
            # Identify x and y values of those pixels
            nonzeroy = np.array(nonzero[0])
            nonzerox = np.array(nonzero[1])
            # Define a bounding box based on min/max x and y
            bbox = ((np.min(nonzerox), np.min(nonzeroy)), (np.max(nonzerox), np.max(nonzeroy)))
            # Draw the box on the image
            cv2.rectangle(img, bbox[0], bbox[1], (0, 255, 0), 6)
        return img

def test_show_images():
    img1 = Utils.read_image('../test_images/test1.jpg')
    img2 = Utils.read_image('../test_images/test2.jpg')
    Utils.show_images([img1, img2])


def test_bounding_boxes():
    img = Utils.read_image('../test_images/test1.jpg')
    bboxes = [((100, 100), (200, 200)), ((300, 300), (400, 400))]
    boxed_img = Utils.draw_boxes(img, bboxes)
    Utils.show_images([img, boxed_img])

if "__main__" == __name__:
    test_show_images()
    #test_bounding_boxes()


