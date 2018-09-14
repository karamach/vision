from utils.db.base import Base

class SolveSessions(Base):

    table_name = 'SolveSessions'
    
    cols = [
        ('Asset', str),
        ('Category', str),
        ('Session', str),
        ('Site', str),
        ('Version', int),
        ('CameraModel', str),
        ('CameraSerial', str),
        ('CameraVersion', int),
        ('DenseOutputAsset', int),
        ('DenseOutputAssetVersion', int),
        ('DenseOutputFile', str),
        ('Flights', list, int),
        ('OccupancyMapAsset', str),
        ('OccupancyMapAssetVersion', int),
        ('OccupancyMapFile', str),
        ('Orientation', list, float),
        ('Origin', list, float),
        ('RotationOrder', str),
        ('Scale', float),
    ]

    def __init__(self, project, instance_id, database_id, defaults):
        super(SolveSessions, self).__init__(project, instance_id, database_id, SolveSessions.table_name, defaults)
        
def get_camera_serial_number(project, instance, client, site, session):
    defaults = {
        'Site': site,
        'Session': session
    }
    ss = SolveSessions(project, instance, client, defaults)
    result = ss.get_select_rows([
        'CameraSerial'
    ])
    return [r for r in result][0]

def get_sim_transform(project, instance, client, site, session):
    defaults = {
        'Site': site,
        'Session': session
    }
    ss = SolveSessions(project, instance, client, defaults)
    result = ss.get_select_rows([
        'Orientation', 'Origin', 'Scale'
    ])
    return [r for r in result][0]

