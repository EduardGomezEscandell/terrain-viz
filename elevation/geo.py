from pyproj import Transformer

# epsg:25831 is the format used by the ICGC
# EPSG is the WGS 84 latitude / longitude we all know and love
__transformer = Transformer.from_crs("epsg:25831", "epsg:4326", always_xy=True)

def epsg25831_to_lonlat(N: float, E: float):
    """
    Takes coordinates from the epsg:25831 format and projects them to longitude and latitude
    """
    return __transformer.transform(N, E)