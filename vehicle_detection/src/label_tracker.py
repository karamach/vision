import numpy as np
import math

class LabelTracker(object):

    def __init__(self, params):
        self.params = params
        self.labels = []

    @staticmethod
    def add_heat(heat_map, bbox_list):
        for box in bbox_list:
            heat_map[box[0][1]:box[1][1], box[0][0]:box[1][0]] += 1
        return heat_map

    def compute_cumulative(self, heat_map, cum_beg, cum_end, cont_beg, cont_end):
        cum_output = np.zeros_like(heat_map).astype(np.float)
        for heat_map in self.labels[cum_beg: cum_end]:
            cum_output = cum_output + heat_map

        cont_output = np.zeros_like(heat_map).astype(np.float)
        for heat_map in self.labels[cont_beg: cont_end]:
            cont_output = np.multiply(cont_output, heat_map)

        cum_output[cum_output <= math.ceil(self.params['threshold'] * np.max(cum_output))] = 0
        return cum_output

    def track_label(self, img, bbox_list):
        heat_map = np.zeros_like(img[:, :, 0]).astype(np.float)
        LabelTracker.add_heat(heat_map, bbox_list)
        self.labels.append(heat_map)
        output = self.compute_cumulative(heat_map, -1*min(self.params['num_frames'], len(self.labels)),
                                         len(self.labels), -1*min(self.params['num_cont_frames'], len(self.labels)),
                                         len(self.labels))
        return output
