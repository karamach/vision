import pickle
import argparse
import cv2
import numpy as np

GOOD_MATCH_PERCENT = .15

def solve(match_features_file, from_features_file, to_features_file, focal_length):
    
    def load_features(feature_file):
        with open(feature_file, 'rb') as inp:
            return pickle.load(inp)

    [from_features, to_features]  = [
        load_features(feature_file)
        for feature_file in [from_features_file, to_features_file]
    ]

    [kp_sift1, des_sift1, kp_surf1, des_surf1] = from_features    
    [kp_sift2, des_sift2, kp_surf2, des_surf2] = to_features

    matches = load_features(match_features_file)
    matches.sort(key=lambda x: x[0], reverse=False)
    matches = matches[:int(GOOD_MATCH_PERCENT*len(matches))]

    points1 = np.zeros((len(matches), 2), dtype=np.float32)
    points2 = np.zeros((len(matches), 2), dtype=np.float32)        

    [dist, omg_idx, query_idx, train_idx] = range(4)    
    for i, match in enumerate(matches):        
        points1[i, :] = kp_sift1[match[query_idx]].pt
        points2[i, :] = kp_sift2[match[train_idx]].pt

    E, mask = cv2.findEssentialMat(points1, points2, focal=focal_length, pp=(0., 0.), method=cv2.RANSAC, prob=0.999, threshold=3.0)
    points, R, t, mask = cv2.recoverPose(E, points1, points2)
#    print(R, t)

if '__main__' == __name__:

    parser = argparse.ArgumentParser(description='solve')
    parser.add_argument('--match_features', help='match features', required=True)
    parser.add_argument('--from_features', help='input from features', required=True)
    parser.add_argument('--to_features', help='input to features', required=True)
    parser.add_argument('--focal_length', type=float, help='camera focal length', required=True)
    args = parser.parse_args()
    solve(args.match_features, args.from_features, args.to_features, args.focal_length)
