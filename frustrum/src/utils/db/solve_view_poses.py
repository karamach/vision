class SolveViewPoses(Base):

    cols = [
        ('Asset', str),
        ('Category', str),
        ('Session', str),
        ('Site', str),
        ('Version', int),
        ('Snapid', str),
        ('SolveViewIndex', int),
        ('CalibHeight', int),
        ('CalibWidth', int),
        ('CameraAssetId', str),
        ('cx', float),
        ('cy', float),
        ('Distortion', list, float),
        ('fx', float),
        ('fy', float),
        ('Orientation', list, float),
        ('OverlappingViewIds', list, str),
        ('Position', list, float),
        ('Skew', float),        
        ('SourceView', str),
        ('SourceViewAsset', str),
        ('SourceViewAssetVersion', str)
    ]

    def __init__(self, project, instance_id, database_id, table_name, defaults):
        super(SolveViewPoses, self).__init__(project, instance_id, database_id, table_name, defaults)


def get_solve_pose_data(out_file):
    defaults = {
        'Site': 'GUADALUPE_SPILLWAY',
        'Session': '20180815'
    }
    solve_poses = SolveViewPoses('prenav-internal', 'develop', 'demo_assets', 'SolveViewCameras', defaults)
    result = solve_poses.get_select_rows(['SourceView', 'Position', 'Orientation'])
    with open(out_file, 'w') as out:
        for r in result:
            r = [r[0].split(':')[-1]] + [r[1].split(':')[-1]] +  r[2:]
            print(r)
            out.write('%s\n' % '\t'.join([str(v) for v in r]))
                            

def get_view_match_data(site, session):
    defaults = {
        'SolveSession': 'PITTSBURGH_180329'
    }
    view_matches = ViewMatches('prenav-internal', 'develop', 'prenav_assets', 'ViewMatches', defaults)
    result = view_matches.get_select_rows(['ToView', 'View', 'GoodMatch', 'MatchCount'])
    
    with open(out_file, 'w') as out:
        for r in result:
            r = [r[0].split(':')[-1]] + [r[1].split(':')[-1]] +  r[2:]
            print(r)
            out.write('%s\n' % '\t'.join([str(v) for v in r]))

