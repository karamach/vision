from view.similarity_transform_validation import *

import argparse

from utils.db.gps import *
from utils.db.solve_view_poses import *
from utils.db.asseted_camera_calibrations import *
from utils.db.solve_sessions import *

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
    args = parser.parse_args()

    # gps data for cameras
    gps_data = get_gps_data(args.project, args.instance, args.client, args.site, args.session)

    # solve data for cameras
    solve_pose_data = get_solve_pose_data(args.project, args.instance, args.client, args.site, args.session)
        
    # camera intrinsics
    [camera_serial_number] = get_camera_serial_number(args.project, args.instance, args.client, args.site, args.session)
    intrinsics = get_camera_intrinsics(args.project, args.instance, args.client, args.site, args.session, camera_serial_number)

    # get similarity transform
    [orientation, origin, scale] = get_sim_transform(args.project, args.instance, args.client, args.site, args.session)
    print(orientation, origin, scale)

    # load cameras with gps poses
    view_cameras_gps = Camera.load_cameras_gps(intrinsics, gps_data, 10)

    # load cameras with solve poses
    view_cameras_solve = Camera.load_cameras_solve(intrinsics, solve_pose_data, 2, orientation, origin, scale)

    view_ids_gps = set(view_cameras_gps.keys())
    view_ids_solve = set(view_cameras_solve.keys())
    view_ids = sorted(list(view_ids_gps.intersection(view_ids_solve)))[:5]
    
    #plot_poses([view_cameras_gps[view_id] for view_id in view_ids], [view_cameras_solve[view_id] for view_id in view_ids])
    
