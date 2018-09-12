from utils.db.base import Base

class AssetedCameraCalibrations(Base):

    table_name = 'AssetedCameraCalibrations'

    cols = [
        ('Model', str),
        ('Asset', str),
        ('SerialNumber', str),
        ('Version', int),
        ('Baseline', float),
        ('Blackpoint', list, float),
        ('ConvergenceDistance', float),
        ('Crop', bool),
        ('CropResolutionHeight', int),
        ('CropResolutionWidth', int),        
        ('cx', float),
        ('cy', float),        
        ('Distortion', list, float),
        ('Exposure', float),
        ('FocalDistance', float),
        ('Fstop', float),
        ('fx', float),
        ('fy', float),
        ('Gamma', list, float),
        ('Make', str),
        ('PixelPitch', float),
        ('q', list, float),
        ('ResolutionHeight', int),
        ('ResolutionWidth', int),
        ('Stereo', bool),
        ('t', list, float),
        ('Whitepoint', list, float)
    ]

    def __init__(self, project, instance_id, database_id, defaults):
        super(AssetedCameraCalibrations, self).__init__(project, instance_id, database_id, AssetedCameraCalibrations.table_name, defaults)
        
def get_camera_intrinsics(project, instance, client, site, session, serial_number):
    defaults = {
        'SerialNumber': serial_number
    }
    acc = AssetedCameraCalibrations(project, instance, client, defaults)
    result = acc.get_select_rows([
        'fx', 'fy', 'ResolutionHeight', 'ResolutionWidth'
    ])
    return [r for r in result][0]
    
