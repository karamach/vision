from view.similarity_transform_validation import *

import argparse
import sys

from utils.db.gps import *
from utils.db.solve_view_poses import *
from utils.db.asseted_camera_calibrations import *
from utils.db.solve_sessions import *

from model.camera import Camera

from utils.pose import Pose
from utils.utils import PointCloudUtils

#from utils.sim_transform import *

# --site PITTSBURGH --session 180329 --client prenav_assets
# --site GUADALUPE_SPILLWAY --session 20180815_1
# --site VESONA_DAM --session 20180815_1

def compute_sim_transform(gps_data, solve_pose_data):
    
    gps_views, gps_trans_data = [r[0] for r in gps_data], [r[4:] for r in gps_data]
    solve_views, solve_data = [r[0] for r in solve_pose_data], [r[1:] for r in solve_pose_data]

    def applyMeaninglessTransform(xyz, quat):
        [xyz_t] = Pose.rot([xyz + [1]], Pose.q2ypr(*quat), True)
        return xyz_t[:3]

    solve_data = [applyMeaninglessTransform(pose[0], pose[1])  for pose in solve_data]
    
    transform = compute_transform(gps_views, gps_trans_data, solve_views, solve_data)
    transform = [v for i, v in enumerate(transform)]
    [orientation, origin, scale] = [transform[:3], transform[3:6], transform[6]]
    return [orientation, origin, scale]
                

if '__main__' == __name__:

    parser = argparse.ArgumentParser(description='view intersection visualization')
    parser.add_argument('--project', required=False, default='prenav-internal')
    parser.add_argument('--instance', required=False, default='develop')
    parser.add_argument('--client', required=False, default='demo_assets')
    parser.add_argument('--site', required=True)
    parser.add_argument('--session', required=True)
    parser.add_argument('--ply', required=False)
    args = parser.parse_args()

    # gps data for cameras [[view_id, gimb_p, gimb_y, gimb_r, lat_dec, lon_dec, alt'], ... ]
    gps_data = get_gps_data(args.project, args.instance, args.client, args.site, args.session)

    # solve data for cameras [[view_id, [position(x, y, z)], [orientation(x, y, z, w)]], .. ]
    solve_pose_data = get_solve_pose_data(args.project, args.instance, args.client, args.site, args.session)
        
    # get similarity transform from db
    [orientation, origin, scale] = get_sim_transform(args.project, args.instance, args.client, args.site, args.session)

    # camera intrinsics
    [camera_serial_number] = get_camera_serial_number(args.project, args.instance, args.client, args.site, args.session)
    intrinsics = get_camera_intrinsics(args.project, args.instance, args.client, args.site, args.session, camera_serial_number)    

    # load cameras with gps poses
    view_cameras_gps = Camera.load_cameras_gps(intrinsics, gps_data, 10)

    # load cameras with solve poses
    view_cameras_solve = Camera.load_cameras_solve(intrinsics, solve_pose_data, 2, orientation, origin, scale)

    # common view ids
    view_ids_gps = set(view_cameras_gps.keys())
    view_ids_solve = set(view_cameras_solve.keys())
    view_ids = sorted(list(view_ids_gps.intersection(view_ids_solve)))

    gpsPoints = [c.getOrigin() for c in [view_cameras_gps[view_id] for view_id in view_ids]]
    solvePoints = [c.getOrigin() for c in [view_cameras_solve[view_id] for view_id in view_ids]]    
    (pointCloudPoints, pointCloudColors) = PointCloudUtils.loadPointCloud(args.ply, origin, orientation, scale, 5000) if args.ply else (None, None)
    
    plot_poses(
        gpsPoints, len(gpsPoints)*['red'],
        solvePoints,  len(gpsPoints)*['green'],
        pointCloudPoints, pointCloudColors
    )
    
