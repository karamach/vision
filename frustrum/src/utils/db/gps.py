from utils.db.base import Base
from utils.utils import lmap, lfilter, GPSUtils

class GPS(Base):

    cols = [
        ('Asset', str),
        ('Category', str),
        ('Session', str),
        ('Site', str),
        ('Version', int),
        ('View', str),
        ('AbsoluteAltitude', float),
        ('FlightPitch', float),        
        ('FlightRoll', float),
        ('FlightYaw', float),
        ('GimbalPitch', float),
        ('GimbalReverse', int),
        ('GimbalRoll', float),
        ('GimbalYaw', float),
        ('GPSAltitude', float),
        ('GPSAltitudeRef', int),
        ('GPSLatitude', list, float),
        ('GPSLatitudeRef', str),
        ('GPSLongitude', list, float),
        ('GPSLongitudeRef', str),        
        ('RelativeAltitude', float),                
    ]

    def __init__(self, project, instance_id, database_id, table_name, defaults):
        super(GPS, self).__init__(project, instance_id, database_id, table_name, defaults)

def insert_gps_data():

    def process_json(folder):

        def read_file(f):
            with open(f, 'r') as f_handle:
                lines = [line.rstrip() for line in  f_handle.readlines()]
                d = json.loads(''.join(lines))
                d['Asset'] = d['View'] = os.path.basename(f).split('.')[1]
                return d

        files = [os.path.join(folder, f) for f in os.listdir(folder)]
        return [read_file(f) for f in files]

    defaults = {
        'Session': '180329',
        'Site': 'PITTSBURGH',
        
    }
    data = process_json('/home/karamach/tmp/sfm/prenav-datasets/karamach/PITTSBURGH/180329/JSON/PHANTOM/001/')
    gps = GPS('prenav-internal', 'develop', 'prenav_assets', 'GPS', defaults)
    gps.insert_rows(data)

def get_gps_data(project, instance, client, site, session):
    defaults = {
        'Site': site,
        'Session': session
    }
    gps = GPS(project, instance, client, 'GPS', defaults)
    result = gps.get_select_rows([
        'View', 'GPSLatitude', 'GPSLatitudeRef', 'GPSLongitude', 'GPSLongitudeRef', 'RelativeAltitude', 'GimbalYaw', 'GimbalPitch', 'GimbalRoll' 
    ])

    result = lfilter(lambda r: r is not None and r[1] is not None and r[2] is not None and len(r[1]) != 0 and len(r[3]) != 0, result)
    result = lmap(lambda r: [r[0]] + [GPSUtils.dms2dd(r[1], r[2])] + [GPSUtils.dms2dd(r[3], r[4])] + r[5:], result)
    return result
    
