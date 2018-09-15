from view.similarity_transform_validation import *

import argparse
import sys

from utils.db.gps import *
from utils.db.solve_view_poses import *
from utils.db.asseted_camera_calibrations import *
from utils.db.solve_sessions import *

from model.camera import Camera

from utils.pose import Pose

from utils.sim_transform import *

# --site GUADALUPE_SPILLWAY --session 20180815
# --site PITTSBURGH --session 180329
# --site VESONA_DAM --session 20180815_1


def dump_common(gps_views, gps_data, solve_views, solve_data):
    gps_map = dict([(v, g) for v, g in zip(gps_views, gps_data)])
    solve_map = dict([(v, s) for v, s in zip(solve_views, solve_data)])

    views = set(gps_map.keys()).intersection(solve_map.keys())

    with open('/tmp/gps.txt', 'w') as gps:
        with open('/tmp/solve.txt', 'w') as solve:        
            for v in sorted(list(views)):
                o = ' '.join([str(v)] + [str(val) for val in gps_map[v]])
                gps.write(o + '\n')

            for v in sorted(list(views)):
                o = ' '.join([str(v)] + [str(val) for val in solve_map[v]])
                solve.write(o + '\n')                        


if '__main__' == __name__:

    parser = argparse.ArgumentParser(description='view intersection visualization')
    parser.add_argument('--project', required=False, default='prenav-internal')
    parser.add_argument('--instance', required=False, default='develop')
    parser.add_argument('--client', required=False, default='demo_assets')
    parser.add_argument('--site', required=True)
    parser.add_argument('--session', required=True)
    args = parser.parse_args()

    # gps data for cameras [[view_id, gimb_p, gimb_y, gimb_r, lat_dec, lon_dec, alt'], ... ]
    #gps_data = get_gps_data(args.project, args.instance, args.client, args.site, args.session)
    gps_data = get_gps_data(args.project, args.instance, 'prenav_assets', args.site, args.session)

    # solve data for cameras [[view_id, [position(x, y, z)], [orientation(x, y, z, w)]], .. ]
    solve_pose_data = get_solve_pose_data(args.project, args.instance, args.client, args.site, args.session)
        
    # get similarity transform from db
    #[orientation, origin, scale] = get_sim_transform(args.project, args.instance, args.client, args.site, args.session)

    # compute similarity transform
    gps_views, gps_trans_data = [r[0] for r in gps_data], [r[4:] for r in gps_data]
    solve_views, solve_data = [r[0] for r in solve_pose_data], [r[1:] for r in solve_pose_data]

    def applyMeaninglessTransform(xyz, quat):
        [xyz_t] = Pose.rot([xyz + [1]], Pose.q2ypr(*quat), True)
        return xyz_t[:3]

    solve_data = [applyMeaninglessTransform(pose[0], pose[1])  for pose in solve_data]

    #dump_common(gps_views, gps_trans_data, solve_views, solve_data)
    
    transform = compute_transform(gps_views, gps_trans_data, solve_views, solve_data)
    transform = [v for i, v in enumerate(transform)]
    transform = [-1.43714, 1.50323, 2.82573, -0.38851, 0.406811, 3.61709, 7.24737]
    [orientation, origin, scale] = [transform[:3], transform[3:6], transform[6]]
    print(orientation, origin, scale)
    

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
    
    plot_poses([view_cameras_gps[view_id] for view_id in view_ids], [view_cameras_solve[view_id] for view_id in view_ids])
    
