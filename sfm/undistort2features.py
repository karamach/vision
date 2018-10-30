import pickle
import argparse
import cv2
import numpy as np

import PyOpenImageIO as oiio

def plot_keypoints(pixels, kp, out):
    img_with_kp = cv2.drawKeypoints(pixels, kp,
                                    flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS, outImage=None)
    cv2.imwrite(out, img_with_kp)

def extract_features(img, out):
    img = oiio.ImageBuf(img)
    rgb_pixels = img.get_pixels()
    gray_pixels = 255*np.dot(rgb_pixels[...,:3], [0.299, 0.587, 0.114])
    gray_pixels = gray_pixels.astype(np.uint8)
    sift = cv2.xfeatures2d.SIFT_create()
    kp_sift, des_sift = sift.detectAndCompute(gray_pixels, None)
    
#    surf = cv2.xfeatures2d.SURF_create()
#    kp_surf, des_surf = surf.detectAndCompute(gray_pixels, None)

    with open(out, 'wb') as o:
        pickle.dump([kp_sift, des_sift], o)
                
if '__main__' == __name__:

    parser = argparse.ArgumentParser(description='raw2exr')
    parser.add_argument('--input_image', help='input undistorted exr image', required=True)
    parser.add_argument('--output_features', help='output features', required=True)
    args = parser.parse_args()
    extract_features(args.input_image, args.output_features)
    
