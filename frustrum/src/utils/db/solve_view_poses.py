from utils.db.base import Base
from utils.utils import lmap, lfilter

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


def get_solve_pose_data(project, instance, client, site, session):
    defaults = {
        'Site': site,
        'Session': session
    }
    solve_poses = SolveViewPoses(project, instance, client, 'SolveViewCameras', defaults)
    result = solve_poses.get_select_rows(['SourceView', 'Position', 'Orientation'])
    return [r for r in result]
                            


