import math
import numpy as np

class Inters:

    def __init__(self, view_matches):
        self.reset()
        self.matches = dict([(tuple(sorted([int(v) for v in row[:2]])), row[2:])for row in view_matches])

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

