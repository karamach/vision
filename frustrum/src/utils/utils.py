import math

class GPSUtils(object):

    @staticmethod    
    def dms2dd(pose, direction='N'):
        [degrees, minutes, seconds] = pose
        dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
        dd *= -1 if direction in set(['W', 'S']) else 1
        return dd;

    @staticmethod
    def convert2decimal(pose):
        return [pose[0]] + [GPSUtils.dms2dd(pose[1:4])] + [GPSUtils.dms2dd(pose[4:7])] + pose[7:]

    @staticmethod
    def haversine(la1, lo1, la2, lo2):
        lat1 = math.radians(la1);
        lat2 = math.radians(la2);
        lon1 = math.radians(lo1);
        lon2 = math.radians(lo2);

        dlon = lon2 - lon1;
        dlat = lat2 - lat1;
        a = (math.sin(dlat / 2.) * math.sin(dlat / 2.)) + math.cos(lat1) * math.cos(lat2) * (math.sin(dlon / 2.) * math.sin(dlon / 2.));
        c = 2.0 * math.asin(math.sqrt(a));
        earth_radius = 6378100.0;
        d = earth_radius * c;
        return d

    @staticmethod    
    def convert_latlon_cartesian(lat, lon, alt, clat, clon, calt):
        x = GPSUtils.haversine(clat, lon, clat, clon);
        y = GPSUtils.haversine(lat, clon, clat, clon);
        z = alt - calt;
        x = -x if (lon < clon) else x;
        y = -y if (lat < clat) else y;
        return [x, y, z];    

def lmap(f, d):
    return list(map(f, d))

def lfilter(f, d):
    return list(filter(f, d))

