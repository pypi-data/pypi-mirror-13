'''
Module providing function and classes for  calculating distances and
bearing from ship to sensor as well as the position of the sensor relative to
the ship.
'''
from __future__ import division
import os
from collections import namedtuple
from operator import xor
# from subject import Subject
from numpy import (sign, pi, sqrt, sin, cos, arcsin, arccos,
                   arctan2, nan, finfo, mod, asarray, isfinite,
                   rad2deg, deg2rad, cross, dot)
from numpy.linalg import norm
from datetime import datetime, timedelta
# from utilities.numpy_utils import is_numlike
from nvector import (n_E2lat_lon, lat_lon2n_E, n_EA_E_and_n_EB_E2p_AB_E,
                     unit, n_E2R_EN, great_circle_distance, azimuth,
                     set_north_pole_axis_for_E_frame)

R_Ee = set_north_pole_axis_for_E_frame(axis='z')

__all__ = ['Navigator', 'NmeaFileReader']


class Subject(object):
    pass


def is_numlike(obj):
    'return true if *obj* looks like a number'
    try:
        obj + 1
    except TypeError:
        return False
    else:
        return True

# Calculate machine precision (machine epsilon)
_EPS = finfo(float).eps
# Corresponds to _DMAX in herman.py and chaco_gui.py
_DMAX = 99999999999999999.0

_GPS_AGE_LIMIT = 30  # maximum age in seconds
# Approx. radius of the Earth (in meters) FAI standard
EARTH_RADIUS_M = 6371009.0
EARTH_RADIUS_KM = EARTH_RADIUS_M / 1000
_NUM_AVERAGES = 10.0
_SMOOTHING = 1.0 / _NUM_AVERAGES


def ellipsoidal_parameters(name='WGS84'):
    """
    Name           Major axis, a [m]    Flattening (f)
    WGS84          6378137.00       1/298.257223563
    GRS80/NAD83    6378137.00       1/298.257222101
    WGS66          6378145.            1/298.25
    GRS67/IAU68    6378160.00          1/298.2472
    WGS72          6378135.            1/298.26
    Krasovsky      6378245.            1/298.3
    Clarke66/NAD27 6378206.4           1/294.9786982138

    To convert between geocentric (radius r, geocentric latitude u) and
    geodetic coordinates (geodetic latitude v, height above the ellipsoid h):

    tan(u) = tan(v)*(h*sqrt((a*cos(v))^2+(b*sin(v))^2) +b^2)/
                  (h*sqrt((a*cos(v))^2+(b*sin(v))^2) +a^2)

    r^2 = h^2 + 2*h*sqrt((a*cos(v))^2+(b*sin(v))^2)+
               (a^4-(a^4-b^4)*(sin(v))^2)/(a^2-(a^2-b^2)*(sin(v))^2)

    a and b are the semi-major axes of the ellipsoid, and b=a*(1-f),
    where f is the flattening. Note that geocentric and geodetic longitudes
    are equal.

    Reference:
    ----------
    Coordinate Systems and Map Projections, D. H. Maling (Pergamon 1992)
    (except Clarke66 !)

    """
    e_param = namedtuple('Ellipsoidal_parameters', ['a', 'f'], verbose=True)
    e_parameters = dict(WGS84=e_param(6378137.00, 1./298.257223563),
                        GRS80=e_param(6378137.00, 1./298.257222101),
                        NAD83=e_param(6378137.00, 1./298.257222101),
                        WGS66=e_param(6378145., 1./298.25),
                        GRS67=e_param(6378160.00, 1./298.2472),
                        IAU68=e_param(6378160.00, 1./298.2472),
                        WGS72=e_param(6378135., 1./298.26),
                        KRASOVSKY=e_param(6378245., 1./298.3),
                        CLARKE66=e_param(6378206.4, 1./294.9786982138),
                        NAD27=e_param(6378206.4, 1./294.9786982138))

    return e_parameters[name.upper()]


# rad2deg = lambda rad: rad * (180.0 / pi)
# deg2rad = lambda deg: deg * (pi / 180.0)
deg = rad2deg
rad = deg2rad


def knots2ms(knots):
    return knots * 0.514444


def ms2knots(ms):
    return ms * 1.943844


def distance_rad2distance_nm(distance_rad):
    return 60 * deg(distance_rad)


def distance_nm2distance_rad(distance_nm):
    return rad(distance_nm)/60  # (pi / (180. * 60)) * distance_nm


def distance_km2distance_rad(distance_km):
    return distance_km / EARTH_RADIUS_KM


def distance_m2distance_rad(distance_m):
    return distance_m / EARTH_RADIUS_M


def distance_rad2distance_km(distance_rad):
    return distance_rad * EARTH_RADIUS_KM


def distance_rad2distance_m(distance_rad):
    return distance_rad * EARTH_RADIUS_M


def _acos_safe(x):
    """
    Arguments of arccos() may exceed 1 in magnitude because of
    rounding errors. This function computes arccos(x) in a safe way.
    """
    y = asarray(x)
    return arccos(y.clip(min=-1, max=1))


def _asin_safe(x):
    """
    Arguments of arcsin() may exceed 1 in magnitude because of
    rounding errors. This function computes arcsin(x) in a safe way.
    """
    y = asarray(x)
    return arcsin(y.clip(min=-1, max=1))


# ----- MISC HELPER FUNCTIONS
#
def nmea_split(nmea_str):
    sentence_id = nmea_str[3:6]
    data = nmea_str[7:].split(',')
    return sentence_id, data


def split_hhmm_string(hhmm):
    """
    Split lat or lon 'HHMM.nnnn' string into 'HH', 'MM.nnnn' strings.

    HMM.nnnn or or HHHMM.nnnn
    """
    if hhmm[5] == '.':  # 'HHHMM.nnnn'
        hours, mins = hhmm[0:3], hhmm[3:]
    elif hhmm[3] == '.':  # 'HMM.nnnn string'
        hours, mins = hhmm[0:1], hhmm[1:]
    else:  # 'HHMM.nnnn' string
        hours, mins = hhmm[0:2], hhmm[2:]
    return hours, mins


def lat_or_lon_str2dec_str(data):
    """
    Converts lat or lon HHMM.nnnn string into HH.ddddd decimal string
    """
    hours, mins = split_hhmm_string(data)
    dec = float(mins) / 60.0 * 100.0
    # Cap at 6 digits - currently nn.nnnnnnnn
    dec = dec * 10000.0
    str_dec = "%06d" % dec
    return hours + "." + str_dec


def lat_lon_str2rad(lat, lat_dir, lon, lon_dir):
    """
    Converts lat and lon HHMM.nnnn strings into floats (radians)

    Parameters:
    -----------
    lat : string
        Latitude HHMM.nnnn
    lat_dir : 'N' or 'S'
        Latitudal direction North or South
    lon : string
        Longitude HHMM.nnnn
    lon_dir : 'E' or 'W'
        Longitudal direction East or West

    Returns
    -------
    lat_rad : real scalar
        latitude in radians
    lon_rad : real, scalar
        longitude in radians

    Example
    -------
    >>> lat_lon_str2rad('60.5', 'N', '40.2', 'E')
    (1.0473429894831665, 0.6981898726217007)
    """
    # Convert NMEA lat_dec_str and lon_dec_str to decimals
    lat_dec_str = lat_or_lon_str2dec_str(lat)
    lon_dec_str = lat_or_lon_str2dec_str(lon)
    if lat_dir in ('S', 's'):
        lat_dec_str = '-' + lat_dec_str
    if lon_dir == ('W', 'w'):
        lon_dec_str = '-' + lon_dec_str
    lat_rad = float(lat_dec_str) * pi / 180
    lon_rad = float(lon_dec_str) * pi / 180
    return (lat_rad, lon_rad)


class GeoPath(object):
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2

    def _euclidean_cross_track_distance(self, radius, cos_angle):
        return -cos_angle * radius

    def _great_circle_cross_track_distance(self, radius, cos_angle):
        return (arccos(cos_angle) - pi / 2) * radius

    def nvectors(self):
        return self.point1.nvector(), self.point2.nvector()

    def _normal_to_great_circle(self):
        n_EA1_E, n_EA2_E = self.nvectors()
        return cross(n_EA1_E, n_EA2_E, axis=0)

    def cross_track_distance(self, point, radius=6371e3, method='greatcircle'):
        """
        Return cross track distance from the path to the point.

        Parameters
        ----------
        point: GeoPoint
        radius: real scalar
            radius of sphere in [m]. Default mean Earth radius
        method: string
            defining distance calculated. Options are:
            'greatcircle' or 'euclidian'

        Returns
        -------
        distance: real scalar
            distance in [m]
        """
        c_E = unit(self._normal_to_great_circle())
        n_EB_E = point.nvector()
        cos_angle = dot(c_E.T, n_EB_E)
        if method[0] == 'e':
            return self._euclidean_cross_track_distance(radius, cos_angle)
        return self._great_circle_cross_track_distance(radius, cos_angle)

    def _great_circle_distance(self, radius, n_EA_E, n_EB_E):
        # The great circle distance is given by equation (16) in Gade (2010):
        # Well conditioned for all angles:
        return arctan2(norm(cross(n_EA_E, n_EB_E, axis=0), axis=0),
                       dot(n_EA_E.T, n_EB_E)) * radius

    def track_distance(self, radius=6371e3, method='greatcircle'):
        """
        Return the distance of the path.
        """
        n_EA_E, n_EB_E = self.nvectors()

        if method[0] == "e":  # Euclidean distance:
            return norm(n_EB_E - n_EA_E, axis=0) * radius
        return self._great_circle_distance(radius, n_EA_E, n_EB_E)

    def intersection(self, path):
        """
        Return the intersection between the paths

        Parameters
        ----------
        path: GeoPath object
            path to intersect

        Returns
        -------
        point: GeoPoint
            point of intersection between paths
        """
        n_EA1_E, n_EA2_E = self.nvectors()
        n_EB1_E, n_EB2_E = path.nvectors()

        # Find the intersection between the two paths, n_EC_E:
        n_EC_E_tmp = unit(cross(cross(n_EA1_E, n_EA2_E, axis=0),
                                cross(n_EB1_E, n_EB2_E, axis=0), axis=0))

        # n_EC_E_tmp is one of two solutions, the other is -n_EC_E_tmp. Select
        # the one that is closet to n_EA1_E, by selecting sign from the dot
        # product between n_EC_E_tmp and n_EA1_E:
        n_EC_E = sign(dot(n_EC_E_tmp.T, n_EA1_E)) * n_EC_E_tmp

        lat_EC, long_EC = n_E2lat_lon(n_EC_E)
        return GeoPoint(lat_EC, long_EC)


class GeoPoint(object):

    '''
    Class for calculating on geographical locations

    Attributes
    ----------
    lat : real scalar
        latitude in radians
    lon : real, scalar
        longitude in radians
    '''

    def __init__(self, lat=nan, lon=nan, time=None, valid=None):
        self.lat = lat
        self.lon = lon
        self.time = time
        if valid is None:
            self.check_validity()
        else:
            self.valid = valid

    def check_validity(self):
        lat, lon = self.lat, self.lon
        self.valid = is_numlike(lat) and isfinite(
            lat) and is_numlike(lon) and isfinite(lon)
        return self.valid

    def __repr__(self):
        return 'GeoPoint(lat={}, lon={})'.format(self.lat, self.lon)

    def nvector(self):
        return lat_lon2n_E(self.lat, self.lon)

    def distance_rad_and_bearing_rad_between_points(self, geo_point):
        n_EA_E = self.nvector()
        n_EB_E = geo_point.nvector()

        distance_rad1 = great_circle_distance(n_EA_E, n_EB_E, radius=1)
        bearing_rad1 = azimuth(n_EA_E, n_EB_E, a=EARTH_RADIUS_M, f=0)
        return distance_rad1, bearing_rad1

        lat1, lon1 = self.lat, self.lon
        lat2, lon2 = geo_point.lat, geo_point.lon
        d_lat = lat2 - lat1
        d_lon = lon2 - lon1
        # Use the Haversine formula for computing distance.
        a_0 = (sin(d_lat / 2) * sin(d_lat / 2) +
               cos(lat1) * cos(lat2) * sin(d_lon / 2) * sin(d_lon / 2))
        distance_rad = 2 * _asin_safe(sqrt(a_0))  # Alternative 1
        # Alternative 2
        # distance_rad = 2 * arctan2(sqrt(a_0), sqrt(1.0 - a_0))
        x_1 = sin(lat2) - sin(lat1) * cos(distance_rad)
        y_1 = sin(distance_rad) * cos(lat1)
        if (abs(cos(lat1)) < _EPS):  # Less  than machine precision?
            if (lat1 > 0):
                bearing_rad = pi  # Starting from N pole
            else:
                bearing_rad = 2. * pi  # Starting from S pole
        elif (abs(sin(distance_rad)) < _EPS):  # Less than machine precision?
            bearing_rad = 0.0  # Bearing not defined with zero distance
        elif (sin(d_lon) > 0):
            bearing_rad = _acos_safe(x_1 / y_1)
        else:
            bearing_rad = 2 * pi - _acos_safe(x_1 / y_1)
        return distance_rad, bearing_rad

    def distance_rad_bearing_rad2point(self, distance_rad, bearing_rad):
        '''Returns GeoPoint given radial and distance

        Example
        -------
        >>> point1 = GeoPoint(lat=(33+57./60)*pi/180, lon=(118+24./60)*pi/180)
        >>> point1
        GeoPoint(lat=0.592539281052, lon=2.06646983436)

        >>> point2 = GeoPoint(lat=0.709186, lon=1.287762)
        >>> d, b = point1.distance_rad_and_bearing_rad_between_points(point2)
        >>> point1.distance_rad_bearing_rad2point(d, b)
        GeoPoint(lat=0.709186, lon=1.287762)

        '''
        # Find the destination point B, as n_EB_E ("The direct/first geodetic
        # problem" for a sphere)

        # Step1: Find unit vectors for north and east:
        n_EA_E = self.nvector()
        k_east_E = unit(cross(dot(R_Ee.T, [[1], [0], [0]]), n_EA_E, axis=0))
        k_north_E = cross(n_EA_E, k_east_E, axis=0)

        # Step2: Find the initial direction vector d_E:
        d_E = k_north_E * cos(bearing_rad) + k_east_E * sin(bearing_rad)

        # Step3: Find n_EB_E:
        n_EB_E = n_EA_E * cos(distance_rad) + d_E * sin(distance_rad)

        lat2, lon2 = n_E2lat_lon(n_EB_E)  # convert to lat lon
        #return GeoPoint(lat2, lon2)
        # Old call
        lat1, lon1 = self.lat, self.lon
        theta = 2 * pi - bearing_rad
        lat = _asin_safe(sin(lat1) * cos(distance_rad) +
                         cos(lat1) * sin(distance_rad) * cos(theta))
        dlon = arctan2(sin(theta) * sin(distance_rad) * cos(lat1),
                       cos(distance_rad) - sin(lat1) * sin(lat))
        lon = mod(lon1 - dlon + pi, 2 * pi) - pi
        return GeoPoint(lat, lon)

    def distance_and_bearing_between_points(self, geo_point):
        '''
        Calculates distance [m] and bearing [deg] between point1 and point2

        The bearing (b) between point 1 and point 2 is the angle, measured in
        the clockwise direction, between the north reference ray and ray
        between point 1 and 2.

                      |-->b  p2
                      |     /
                      |    /
                      |   /
                      |  /
                      | /
                      |/
                      p1

        Example
        -------
        >>> from copy import copy
        >>> point1 = GeoPoint(lat=(33+57./60)*pi/180, lon=(118+24./60)*pi/180)
        >>> point1
        GeoPoint(lat=0.592539281052, lon=2.06646983436)

        >>> point2 = GeoPoint(lat=0.709186, lon=1.287762)
        >>> point1.distance_and_bearing_between_points(point2)
        (3972863.6351585817, 294.10788752261243)

        >>> east_point = copy(point1); east_point.lon += 0.00001
        >>> point1.distance_and_bearing_between_points(east_point)
        (52.8491279964299, 89.999840010889983)

        >>> west_point = copy(point1); west_point.lon -= 0.00001
        >>> point1.distance_and_bearing_between_points(west_point)
        (52.8491279964299, 270.00015998910999)

        >>> GeoPoint().distance_and_bearing_between_points(GeoPoint())
        (nan, nan)

        >>> GeoPoint()
        GeoPoint(lat=nan, lon=nan)

        See http://williams.best.vwh.net/avform.htm for more info.
        '''
        d_rad, b_rad = self.distance_rad_and_bearing_rad_between_points(
            geo_point)
        distance_m = distance_rad2distance_m(d_rad)

        return distance_m, rad2deg(b_rad)

    def distance_bearing2point(self, distance, bearing):
        '''Returns GeoPoint given radial and distance

        Parameters
        ----------
        distance : real scalar
            distance in [m]
        bearing : real scalar
            angle in degrees clockwise from North


        Example
        -------
        >>> point1 = GeoPoint(lat=(33+57./60)*pi/180, lon=(118+24./60)*pi/180)
        >>> point1
        GeoPoint(lat=0.592539281052, lon=2.06646983436)

        >>> point2 = GeoPoint(lat=0.709186, lon=1.287762)
        >>> d, b = point1.distance_and_bearing_between_points(point2)
        >>> point1.distance_bearing2point(d, b)
        GeoPoint(lat=0.709186, lon=1.287762)

        '''
        distance_rad = distance_m2distance_rad(distance)
        bearing_rad = deg2rad(bearing)
        return self.distance_rad_bearing_rad2point(distance_rad, bearing_rad)

    def dead_reckoning2point(self, speed, heading, t=1):
        '''
        Extrapolate current position based upon speed, heading and elapsed time

        Parameters
        ----------
        speed : real scalar
            in knots
        heading : real scalar
            in degrees
        t : real scalar
            extrapolation time in seconds

        Returns
        -------
        position : GeoPoint
            end position after travelling

        Example
        -------
        >>> point1 = GeoPoint(lat=0.6, lon=2.0)
        >>> point1.dead_reckoning2point(speed=5, heading=0,t=60)
        GeoPoint(lat=0.600024224295, lon=2.0)

        >>> point1.dead_reckoning2point(speed=25, heading=180, t=60)
        GeoPoint(lat=0.599878878526, lon=2.0)

        >>> point1.dead_reckoning2point(speed=25, heading=90, t=60)
        GeoPoint(lat=0.599999994982, lon=1.99985324579)

        >>> point1.dead_reckoning2point(speed=25, heading=270, t=60)
        GeoPoint(lat=0.599999994982, lon=2.00014675421)
        '''
        heading_rad = deg2rad(heading)
        distance = t * knots2ms(speed)  # Travelled distance in meters
        # point = self.distance_bearing2point(distance, 360-heading)

        distance_rad = distance_m2distance_rad(distance)
        # Compute lat/lon of new extrapolated position
        lat1, lon1 = self.lat, self.lon
        lat = _asin_safe(sin(lat1) * cos(distance_rad) +
                         cos(lat1) * sin(distance_rad) * cos(heading_rad))
        dlon = arctan2(sin(heading_rad) * sin(distance_rad) * cos(lat1),
                       cos(distance_rad) - sin(lat1) * sin(lat))
        lon = (lon1 - dlon + pi) % (2 * pi) - pi
        if self.time:
            newtime = self.time + timedelta(seconds=t)
        else:
            newtime = None
        return GeoPoint(lat, lon, time=newtime)

    def offset2point(self, north, east):
        '''
        Convert north, east positions in m to lat, lon
                assuming local flat earth approximation

        Parameters
        ----------
        north, east : real scalars
            distances in the northerly and easterly direction in [m],
            respectively, relative to the current latitude and longitude.

        Returns
        -------
        position : GeoPoint
            end latitude and longitude

        The approximation fails in the vicinity of either pole and at large
        distances.  The error are of order (distance/R)**2

        Example
        -------
        >>> point1 = GeoPoint(lat=0.6, lon=2.0)
        >>> point1.offset2point(north=500,east=500)
        GeoPoint(lat=0.600078668597, lon=2.00009488152)
        '''
        lat0, lon0 = self.lat, self.lon
        a = 6378137  # equatorial radius of the earth for WGS84
        f = 1. / 298.257223563  # flattening in WGS84
        e2 = f * (2 - f)
        fn = sqrt(1. - e2 * sin(lat0) ** 2)
        R1 = a * (1 - e2) / fn ** 3
        R2 = a / fn
        dlat = north / R1
        dlon = east / (R2 * cos(lat0))
        return GeoPoint(dlat + lat0, dlon + lon0)

    def from_lat_lon_str(self, lat, lat_dir, lon, lon_dir):
        """
        Converts lat and lon HHMM.nnnn strings into floats (radians)

        Parameters:
        -----------
        lat : string
            Latitude HHMM.nnnn
        lat_dir : 'N' or 'S'
            Latitudal direction North or South
        lon : string
            Longitude HHMM.nnnn
        lon_dir : 'E' or 'W'
            Longitudal direction East or West

        """
        self.lat, self.lon = lat_lon_str2rad(lat, lat_dir, lon, lon_dir)


def sensor_position_relative_to_ship_location(distance, bearing, ship_heading):
    ''' Calculate plot-friendly sensor location relative to ship position

    Parameters
    ----------
    distance : real scalar
        between ship and sensor
    bearing  : real scalar
        clockwise angle between sensor, ship and true North in degrees
    heading : real scalar
        of the ship in degrees

    Returns
    -------
    x : real scalar
        distance from center of ship to sensor along the longitudinal axis
        (i.e., the direction of the ship)
    y : real scalar
        distance from center of ship to sensor along the arthwartship axis

    Example
    -------
    >>> sensor_position_relative_to_ship_location(distance=10, bearing=90,
    ...                                            ship_heading=0)
    (6.1232339957367663e-16, 10.0)

    >>> sensor_position_relative_to_ship_location(distance=10, bearing=270,
    ...                                            ship_heading=0)
    (-1.8369701987210296e-15, -10.0)

    '''
    theta = deg2rad(bearing - ship_heading)
    x = distance * cos(theta)
    y = distance * sin(theta)
    return x, y


class LocationParser(object):
    '''
    '''
    def __init__(self, start_time):
        self.start_time = start_time

    def _time_str2time_obj(self, t):
        """
        Generates a datetime.time() object from an NMEA timestamp
        """
        time = self.start_time  # make sure date is
        hour, minute, second, _ms = split_hhmmss(float(t))
        return datetime(time.year, time.month, time.day, hour, minute, second)

    def _gga_to_geo_point(self, data):
        lat, lon = lat_lon_str2rad(*data[1:5])
        t = self._time_str2time_obj(data[0])
        return GeoPoint(lat, lon, time=t, valid=(data[5] != '0'))

    def _gll_to_geo_point(self, data):
        lat, lon = lat_lon_str2rad(*data[:4])
        t = self._time_str2time_obj(data[4])
        return GeoPoint(lat, lon, time=t, valid=(data[5] == 'A'))

    def _rmc_to_geo_point(self, data):
        lat, lon = lat_lon_str2rad(*data[2:6])
        day, month, _yy, _ = split_hhmmss(float(data[8]))
        hour, minute, second, _ms = split_hhmmss(float(data[0]))
        year = self.start_time.year
        t = datetime(year, month, day, hour, minute, second)
        return GeoPoint(lat, lon, time=t, valid=(data[1] == 'A'))

    def _empty_geo_point(self, data):
        return GeoPoint(valid=False)

    def _get_parser(self, sentence_id):
        default = self._empty_geo_point
        parser = dict(GGA=self._gga_to_geo_point,
                      RMC=self._rmc_to_geo_point,
                      GLL=self._gll_to_geo_point).get(sentence_id, default)
        return parser

    def __call__(self, gps_sentence):
        """
        Return GeoPoint location from a NMEA sentence.

        The NMEA location sentences we're interested in are:
        GGA - Global Positioning System Fix Data
        GLL - Geographic Position - Latitude/Longitude
        RMC - Recommended Minimum Specific GNSS Data
        """
        sentence_id, data = nmea_split(gps_sentence)
        make_geo_point = self._get_parser(sentence_id)
        return make_geo_point(data)


class Motion(object):

    def __init__(self, speed_knots=nan, true_heading=nan, valid=False):
        self.speed_knots = speed_knots
        self.true_heading = true_heading
        self.valid = valid


def _parse_vtg_motion(data):
    speed = 0 if not len(data[4]) else float(data[4])
    heading = float(data[0])
    return Motion(speed_knots=speed, true_heading=heading,
                  valid=(data[8] != 'N'))


def _parse_rmc_motion(data):
    speed = 0 if not len(data[6]) else float(data[6])
    heading = float(data[7])
    return Motion(speed_knots=speed, true_heading=heading,
                  valid=(data[1] == 'A'))


def _parse_empty_motion(data):
    return Motion()

_MOTION_PARSER_DICT = dict(VTG=_parse_vtg_motion, RMC=_parse_rmc_motion)


def _parse_motion(sentence_id, data):
    """
        Return current motion from NMEA sentences.
        The NMEA motion sentences we're interested in are:
        VTG - Course Over Ground and Ground Speed
        RMC - Recommended Minimum Specific GNSS Data
        """
    return _MOTION_PARSER_DICT.get(sentence_id, _parse_empty_motion)(data)


# --- Navigator OBJECT ATTACHES ON TOP LEVEL, AND MAY BE OBSERVED BY OBSERVER
class Navigator(Subject):
    """
    Reads ship and sensor positions from file, and calculates distance and
    bearing from ship to sensor as well as the position of the sensor relative
    to the ship.

    Parameters
    ----------
    source : BufferSource

    Attributes
    ----------
    distance : real scalar
        distance from gps to sensor
    bearing : real scalar
        angle formed by North-pole, gps-position and sensor-position
    true_heading : real scalar
        of ship
    speed: real scalar
        of ship in knots
    relative_position :
    """

    def __init__(self, source=None):
        Subject.__init__(self)
        # Read by observer
        self.distance = _DMAX
        self.bearing = 0.0
        self.true_heading = 0.0
        self.speed = 0.0
        self.relative_position = (_DMAX, _DMAX)

        # Misc internal
        self._filter = dict(influence='navigation')
        self._gps_age = 0
        self._ship_location = GeoPoint(valid=False)
        self._ship_motion = Motion()
        self._sensor_location = GeoPoint(valid=False)

        self.sample_time = 1.       # is set with set_sample_time

        if source:
            self.update_source(source)
        else:
            self.source = None

    def update_source(self, source):
        '''
        Updates source and initializes sensor location
        '''
        self.source = source
        if self.source:
            d = self.source.get_sensor_position()

            self._sensor_location = GeoPoint(*lat_lon_str2rad(*d[:4]))
        else:
            self._sensor_location = GeoPoint(valid=False)

    def handle_sample(self):
        """
        Handles the next sentences and processes them
        """
        location = self.source.get_sample(self._filter)
        self._handle_location(location)
        self.notify()

    def _handle_location(self, location):
        location_updated = motion_updated = False
        if location:
            prev_location = self._ship_location
            if not location_updated:
                location_updated = self._set_ship_location(location)
                if location_updated:
                    self._gps_age = 0

        if not location_updated and self._ship_motion.valid:
            self._set_ship_location_from_ship_speed_and_course()

        if not motion_updated and location_updated:
            self._set_ship_motion_from_previous_ship_location(prev_location)

        self._set_sensor_position_relative_to_ship_location()
        self._gps_age += 1

    def set_sample_time(self, sample_time):
        self.sample_time = sample_time

    def _set_distance_and_bearing_from_ship_to_sensor(self):
        """
        Calculates distance and bearing from ship to sensor.
        See http://williams.best.vwh.net/avform.htm for more info.
        """
        ship_loc = self._ship_location
        if ship_loc.valid and self._gps_age <= _GPS_AGE_LIMIT:
            sensor_loc = self._sensor_location
            d, b = ship_loc.distance_and_bearing_between_points(sensor_loc)
            self.distance, self.bearing = d, b
        else:
            self.distance, self.bearing = nan, nan

    def _set_ship_location_from_ship_speed_and_course(self):
        """
        Calculates (extrapolates) ship location from ship speed and course.
        See http://williams.best.vwh.net/avform.htm for more info.
        """

        ship_loc = self._ship_location
        ship_mot = self._ship_motion
        if (ship_loc.valid and ship_mot.valid and
                self._gps_age <= _GPS_AGE_LIMIT):

            speed = ship_mot.speed_knots
            heading = ship_mot.true_heading
            new_ship_loc = ship_loc.dead_reckoning2point(
                speed, heading, t=self.sample_time)

        else:
            new_ship_loc = GeoPoint(valid=False)
        self._set_ship_location(new_ship_loc)

    def _set_ship_motion_from_previous_ship_location(self, prev_location):
        ship_loc = self._ship_location
        if prev_location.valid and ship_loc.valid:
            p = prev_location
            distance, heading = p.distance_and_bearing_between_points(ship_loc)
            t2, t1 = ship_loc.time, prev_location.time
            speed_knts = nan
            if t2 and t1:
                time_diff = (t2 - t1).total_seconds()
                if time_diff < 0:
                    t2 += timedelta(days=1)
                    time_diff = (t2 - t1).total_seconds()

                if time_diff > 0:
                    speed_knts = ms2knots(distance / time_diff)
                    w = _SMOOTHING
                    prev_speed = self._ship_motion.speed_knots
                    if isfinite(prev_speed):
                        speed_knts = (1 - w) * prev_speed + w * speed_knts
                    prev_heading = self._ship_motion.true_heading
                    if isfinite(prev_heading):
                        diff_heading = prev_heading - heading
                        if abs(diff_heading) > 180:
                            heading += sign(diff_heading) * 360

                        heading = ((1 - w) * prev_heading + w * heading) % 360
            self._set_ship_motion(Motion(speed_knots=speed_knts,
                                         true_heading=heading, valid=True))

    def _set_sensor_position_relative_to_ship_location(self):
        ''' Calculate plot-friendly sensor location relative to ship position

        x = longitudinal axis (i.e., the direction of the ship)
        y = arthwartship axis

        Uses:
        self.distance,
        self.bearing and
        self._ship_motion['true_heading']
        '''

        ship_motion = self._ship_motion
        if ship_motion.valid and self._gps_age <= _GPS_AGE_LIMIT:
            bearing = self.bearing
            ship_heading = ship_motion.true_heading
            distance = self.distance
            self.relative_position = sensor_position_relative_to_ship_location(
                distance, bearing, ship_heading)
        else:
            self.relative_position = (nan, nan)

    def _set_ship_location(self, location):
        if location.valid:
            self._ship_location = location
            self._set_distance_and_bearing_from_ship_to_sensor()
        return location.valid

    def _set_ship_motion(self, motion):
        if motion.valid:
            self._ship_motion = motion
            self.speed = motion.speed_knots
            self.true_heading = motion.true_heading
        return motion.valid


class GpsInterpolator(object):
    def __init__(self, file_reader, start_time, fetch_length_sec):
        self.file_reader = file_reader
        self.start_time = start_time
        self.fetch_length_sec = fetch_length_sec
        self.make_geo_point = LocationParser(start_time)

    def get_start_time(self):
        time = self.start_time
        return datetime(time.year, time.month, time.day, time.hour,
                        time.minute, time.second, time.microsecond)

    def interpolate(self, time, last_point, next_point):
        if time < last_point.time or time > next_point.time:
            msg = 'time should be between the time of the GeoPoints'
            raise ValueError(msg)
        if last_point.time == next_point.time:
            return next_point
        get_distance_and_bearing = last_point.distance_and_bearing_between_points  # @IgnorePep8
        distance, bearing = get_distance_and_bearing(next_point)
        sec_to_next_point = (next_point.time - last_point.time).total_seconds()
        sec_to_interpolated_point = (time - last_point.time).total_seconds()

        time_ratio = sec_to_interpolated_point / sec_to_next_point

        distance_to_new_point = distance * time_ratio
        new_point = last_point.distance_bearing2point(distance_to_new_point,
                                                      bearing)
        new_point.time = time
        return new_point

    def generator_last_and_next_geo_points(self):
        dt = timedelta(seconds=self.fetch_length_sec)
        iterator = self.generator_geo_points()

        last_point = iterator.next()
        next_point = iterator.next()
        self.time = self.get_start_time()

        while True:
            while self.time > next_point.time:
                last_point = next_point
                while next_point.time <= last_point.time:
                    next_point = iterator.next()
            if self.time >= last_point.time:
                yield last_point, next_point
            self.time += dt

    def generator_geo_points(self):
        for gps_sentence in self.file_reader.iget_data():
            yield self.make_geo_point(gps_sentence)

    def iget_data(self):
        for points in self.generator_last_and_next_geo_points():
            yield self.interpolate(self.time, *points)


class NmeaFileReader(object):

    '''
    Member variables
    ----------------
    file_path : string
        file name with path
    '''

    def __init__(self, file_path):
        self.file_path = file_path

    def _generator_sentences(self, file_path):
        '''
        Return next occurrence of GGA, GLL or RMC sentence.
        '''
        if os.path.exists(self.file_path):
            with open(file_path) as fid:
                for line in fid.readlines():
                    line = _check_nmea_sentence(line)
                    if line[3:6] in ['GGA', 'GLL', 'RMC']:
                        yield line

    def get_data(self):
        """Return all data from the NMEA file"""
        return [s for s in self._generator_sentences(self.file_path)]

    def iget_data(self):
        """Iterates over data from NMEA file """
        return self._generator_sentences(self.file_path)


# ----- GLOBAL, INTERNAL METHODS
#
def nmea_checksum(nmea_str_n_chksum):
    ''' Generate checksum for nmea message
        Checksum follows *, and is XOR of everything
        from the $ to the *, exclusive.
    '''
    # (Checksum is all the data XORed and turned into hex)
    # hex_csum = "%02x" % reduce(xor, map(ord, data[1:-3]))
    nmea_str, _star, _chksum = nmea_str_n_chksum.partition('*')
    # hex_csum = "%02x" % reduce(xor, [ord(c) for c in nmea_str[1:]])
    hex_csum = "%02x" % reduce(xor, map(ord, nmea_str[1:]))  # Fastest
    return hex_csum.upper()


def _check_nmea_sentence(line):
    """
    Checks the NMEA sentence using start- and stop characters
    and the checksum.
    """

    if line:
        # Discard fragmentary sentences -  start with the last '$'
        # _, dollar, nmea_str_chksum = line.rpartition('$')
        nmea_str_n_chksum = line[line.rfind('$'):]

        # see if string contains the * which starts the checksum and keep
        # string upto * for generating checksum
        nmea_str, star, chksum = nmea_str_n_chksum.partition('*')

        # Make sure it starts with $GP and contains the asterisk near the end
        if star:  # and nmea_str[:3] == '$GP' :

            # Checksum follows *, and is XOR of everything
            # from the $ to the *, exclusive.
            # Generate checksum for messages
            # (Checksum is all the data XORed and turned into hex)
            hex_csum = "%02x" % reduce(xor, map(ord, nmea_str[1:]))  # Fastest
            # hex_csum = "%02x" % reduce(xor, [ord(c) for c in nmea_str[1:])
            if chksum[:2] == hex_csum.upper():
                # Strips the checksum
                return nmea_str
        return ''
    else:
        return line


def split_yymmdd(yymmdd):
    '''Split date yymmdd or yyyymmdd into year, month and day

    Example
    -------
    >>> split_yymmdd(20121001)
    (2012, 10, 1)
    >>> split_yymmdd(121001)
    (12, 10, 1)
    '''
    return split_hhmmss(yymmdd)[:3]


def split_hhmmss(hhmmss):
    '''Split hhmmss number into hours minutes and seconds

    Example
    -------
    >>> split_hhmmss(60233.5)
    (6, 2, 33, 0.5)
    '''
    hh = int(hhmmss // 10000)
    mmss = (hhmmss - hh * 10000)
    mm = int(mmss // 100)
    ss = (mmss - mm * 100)
    return hh, mm, int(ss), ss - int(ss)


def add2timestamp_on_gps_files(hh=0, mm=0, ss=0, subtract=False):
    ''' Add time to timestamp on gps files

    Parameters
    ----------
    hh : integer
        hours to add
    mm : integer
        minutes to add
    ss : real
        seconds to add
    subtract : bool
        If True time is subtracted from timestamp otherwise added.
    '''

    root_path = 'X:\\Files\\2011.05.02\\KV Tor\\Herdla'
    file_names = []
    for folder in os.listdir(root_path):
        if folder.startswith('Run'):
            file_names.append(os.path.join(root_path, folder, 'DC201B.gps'))

    if hh or mm or ss:
        sgn = 'm' if subtract else 'p'
        ext = 'corrected%s%d.gps' % (sgn, hh * 10000 + mm * 100 + ss)
    else:
        ext = '.gps'

    td = timedelta(hours=hh, minutes=mm, seconds=ss)
    utc_index_dict = {'$GPRMC': 1, '$GPGGA': 1, '$GPGNS': 1, '$GPGLL': 5}
    for file_name in file_names:
        if os.path.isfile(file_name):
            f = open(file_name)
            line = '1'
            data = []
            while not line == '':
                raw_data = f.readline()
                # for raw_data in raw_data0.split('SOLO'):
                line = _check_nmea_sentence(raw_data)
                if line:
                    tmp = line.split(',')
                    if tmp[0] in utc_index_dict:
                        utc_ix = utc_index_dict.get(tmp[0], 1)
                        hh0, mm0, ss0, ms0 = split_hhmmss(float(tmp[utc_ix]))

                        if tmp[0] == '$GPRMC':
                            dd, mo, yy, _ = split_hhmmss(float(tmp[9]))
                            tm = datetime(year=yy, month=mo, day=dd, hour=hh0,
                                          minute=mm0, second=ss0)
                            if subtract:
                                tn = tm - td
                            else:
                                tn = tm + td
                            tmp[9] = '%d' % (tn.day * 10000 + tn.month * 100 +
                                             mod(tn.year, 100))
                        else:
                            tm = datetime(1, 1, 1, hour=hh0, minute=mm0,
                                          second=ss0)
                            if subtract:
                                tn = tm - td
                            else:
                                tn = tm + td
                        utc = '%09.2f' % (tn.hour * 10000 + tn.minute * 100 +
                                          tn.second + ms0)
                        tmp[utc_ix] = utc
                    nmea_string = ','.join(tmp)
                    data.append(nmea_string + '*%s' %
                                nmea_checksum(nmea_string))
            f.close()

            path, filename = os.path.split(file_name)

            new_filename = os.path.join(path, filename.split('.')[0] + ext)
            fid2 = open(new_filename, 'w')
            for sentence in data:
                fid2.write(sentence)
                fid2.write('\n')
            fid2.close()


def test_docstrings():
    import doctest
    print('Testing docstrings in %s' % __file__)
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
    print('Docstrings tested')


if __name__ == "__main__":

    test_docstrings()
    # add2timestamp_on_gps_files(ss=29,subtract=True)
    p1 = GeoPoint(rad(50), rad(4))
    p2 = GeoPoint(rad(50 + 1./60), rad(4))
    print(p2.distance_and_bearing_between_points(p1))
    path = GeoPath(p1, p2)
    print(path.track_distance())

