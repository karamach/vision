from view.frustum import *

import argparse

from utils.db.gps import *
from utils.db.solve_sessions import *
from utils.db.asseted_camera_calibrations import *
from utils.db.view_feature_matches import *

from model.inters import Inters
from model.camera import Camera

# --site GUADALUPE_SPILLWAY --session 20180815
# --site PITTSBURGH --session 180329

if '__main__' == __name__:

    parser = argparse.ArgumentParser(description='view intersection visualization')
    parser.add_argument('--project', required=False, default='prenav-internal')
    parser.add_argument('--instance', required=False, default='develop')
    parser.add_argument('--client', required=False, default='demo_assets')
    parser.add_argument('--site', required=True)
    parser.add_argument('--session', required=True)
    parser.add_argument('--view1', required=False, default=1)
    parser.add_argument('--view2', required=False, default=2)
    parser.add_argument('--fov_dist', required=False, default=20)
    args = parser.parse_args()

    # gps data for cameras
    gps_data = get_gps_data(args.project, args.instance, args.client, args.site, args.session)
    
    # camera intrinsics
    [camera_serial_number] = get_camera_serial_number(args.project, args.instance, args.client, args.site, args.session)
    intrinsics = get_camera_intrinsics(args.project, args.instance, args.client, args.site, args.session, camera_serial_number)

    # view match data
    view_matches = get_view_matches(args.project, args.instance, args.client, args.site, args.session)

    # load cameras
    view_cameras = Camera.load_cameras(intrinsics, gps_data, args.fov_dist)

    # Setup intersection object
    inters = Inters(view_matches)
    inters.active_cameras = [view_cameras[int(args.view1)], view_cameras[int(args.view2)]]
    
    plot_frustrum(list(view_cameras.values()), inters)
    
