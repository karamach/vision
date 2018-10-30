import pickle
import argparse
import cv2
import numpy as np

import PyOpenImageIO as oiio

def match(from_features_file, to_features_file, match_output):
    
    def load_features(feature_file):
        with open(feature_file, 'rb') as inp:
            return pickle.load(inp)

    [from_features, to_features]  = [
        load_features(feature_file)
        for feature_file in [from_features_file, to_features_file]
    ]

    [kp_sift1, des_sift1, kp_surf1, des_surf1] = from_features
    [kp_sift2, des_sift2, kp_surf2, des_surf2] = to_features
    
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    matches = bf.match(des_sift1, des_sift2)
    matches = [[ma.distance, ma.imgIdx, ma.queryIdx, ma.trainIdx] for ma in matches]    
    with open(match_output, 'wb') as o:
        pickle.dump(matches, o)
                
if '__main__' == __name__:

    parser = argparse.ArgumentParser(description='match featires')
    parser.add_argument('--from_features', help='from features file', required=True)
    parser.add_argument('--to_features', help='to features file', required=True)
    parser.add_argument('--match_output', help='match output file', required=True)
    args = parser.parse_args()
    match(args.from_features, args.to_features, args.match_output)
