from model.camera import Camera
from model.inters import Inters
from utils.geometry import Geometry

def compute_scores():

    cameras = Camera.load_cameras('../data/gps_fov.txt')
    matches = Inters.load_matches('../data/view_matches.txt')
    max_m = max([float(v[1]) for v in matches.values() if v[0] == 'True'])
    min_m = min([float(v[1]) for v in matches.values() if v[0] == 'True'])

    view_cameras = dict([(c.view_id, c) for c in cameras])
    with open('../data/match_quality.txt', 'w') as out:
        s = '#view1\tview2\tmscore\tiscore\n'
        out.write(s)
        for k, v in matches.items():
            (v1, v2) = k
            match_cnt = float(matches[tuple(sorted([v1,v2]))][1])
            if v1 not in view_cameras or v2 not in view_cameras:
                continue
            c1, c2 = view_cameras[v1], view_cameras[v2]
            c1_f = c1.curr_min_frust + c1.curr_max_frust
            c2_f = c2.curr_min_frust + c2.curr_max_frust
            l1 = abs(c1.frust_range[1] - c2.frust_range[0])
            l2 = abs(c2.frust_range[1] - c1.frust_range[0])            
            vol1 = Geometry.get_frustrum_volume(c1_f, l1)
            vol2 = Geometry.get_frustrum_volume(c2_f, l2)
            pois = Geometry.frustrum_intersect(c1_f, c2_f)        
            iscore = Geometry.frustrum_intersection_score(vol1, vol2, pois)
            mscore = 0 if match_cnt == 0 else (match_cnt-min_m)/(max_m-min_m)
            print(v1, v2, match_cnt, mscore, iscore)
            s = '%s\t%s\t%s\t%s\t%s\n' % (v1, v2, match_cnt, mscore, iscore)
            out.write(s)
            
if '__main__' == __name__:
    compute_scores()
