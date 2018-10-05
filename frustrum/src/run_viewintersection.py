from control.inters_control import IntersControl
from view.viewintersection_view import plot_frustrum
    
import argparse
import sys

from utils.db.gps import *
from utils.db.solve_sessions import *
from utils.db.asseted_camera_calibrations import *
from utils.db.view_feature_matches import *

from model.inters import Inters
from model.camera import Camera

# --site GUADALUPE_SPILLWAY --session 20180815
# --site PITTSBURGH --session 180329
# --site VESONA_DAM --session 20180815_1

if '__main__' == __name__:

    parser = argparse.ArgumentParser(description='view intersection visualization')
    parser.add_argument('--project', required=False, default='prenav-internal')
    parser.add_argument('--instance', required=False, default='develop')
    parser.add_argument('--client', required=False, default='demo_assets')
    parser.add_argument('--site', required=True)
    parser.add_argument('--session', required=True)
    parser.add_argument('--viewFrom', required=False, type=int)    
    parser.add_argument('--viewTo', required=False, type=int)    
    parser.add_argument('--fov_dist', required=False, default=20)
    parser.add_argument('--ui', required=False, default=False)
    
    args = parser.parse_args()

    # gps data for cameras
    gps_data = get_gps_data(args.project, args.instance, args.client, args.site, args.session)

    # camera intrinsics
    [camera_serial_number] = get_camera_serial_number(args.project, args.instance, args.client, args.site, args.session)
    intrinsics = get_camera_intrinsics(args.project, args.instance, args.client, args.site, args.session, camera_serial_number)

    # view match data
    view_matches = get_view_matches(args.project, args.instance, args.client, args.site, args.session)

    # load cameras
    active_views = [args.viewFrom, args.viewTo] if args.viewFrom and args.viewTo else [1, 2]
    if args.ui:
        view_cameras = Camera.load_cameras_gps(intrinsics, gps_data, args.fov_dist, active_views)
        inters = Inters(view_matches)
        inters.active_cameras = [view_cameras[idx] for idx in active_views]
        plot_frustrum(list(view_cameras.values()), inters)        
    else:
        viewid_gps = dict([(int(r[0]), r) for r in gps_data])
        for v1 in range(active_views[0], active_views[0] + len(gps_data)):
            for v2 in range(active_views[1], active_views[1] + len(gps_data)):
                v1_data = viewid_gps[v1%len(gps_data)]
                v2_data = viewid_gps[v2%len(gps_data)]
                view_cameras = Camera.load_cameras_gps(intrinsics, [v1_data, v2_data], args.fov_dist, active_views)
                inters = Inters(view_matches)
                inters.active_cameras = [view_cameras[idx] for idx in [v1%len(gps_data), v2%len(gps_data)]]
                plot_frustrum(list(view_cameras.values()), inters)        
                
                #ctrl = IntersControl(view_cameras, inters, True)
                #ctrl.update()
                #print('view1=%06d view2=%06d inters_score=%02d' %
                #      (ctrl.inters.active_cameras[0].view_id, ctrl.inters.active_cameras[1].view_id, ctrl.inters.score))
                #print('----------------------------------------')
    
