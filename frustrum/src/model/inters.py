import math
import numpy as np

from geometry import Geometry as G
from geometry import Pose as P

class Inters:

    def __init__(self, matches_file):
        self.reset()
        self.matches = self.load_matches(matches_file)

    def reset(self):
        self.active_cameras = []
        self.points = []
        self.hull = None
        self.score = 0
        self.state = False
        self.frust_union_volume = 0

    def get_match(self):
        if len(self.active_cameras) != 2:
            return None
        v1, v2 = self.active_cameras[0].view_id, self.active_cameras[1].view_id
        key = tuple(sorted([v1,v2]))
        return self.matches[key] if key in self.matches else None
        
    def load_matches(self, matches_file):
        with open(matches_file, 'r') as f:
            lines = [line.rstrip().split('\t') for line in f.readlines()]
            matches =  dict([(tuple(sorted(row[:2])), row[2:])for row in lines])
            max_m = max([float(v[1]) for v in matches.values() if v[0] == 'True'])
            min_m = min([float(v[1]) for v in matches.values() if v[0] == 'True'])
            print(max_m, min_m)
            for k, v in matches.items():
                matches[k] = [v[0], (float(v[1])-min_m)/(max_m-min_m)]
            return matches
