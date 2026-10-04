import datetime as dt
import numpy as np

__DEG_TO_RAD = np.pi/180

def __year_angle(time_utc: dt.datetime) -> float:
    "Angle (in radians) the earth has advanced through its orbit since spring equinox"
    d = (time_utc - dt.datetime(time_utc.year, 1, 1, tzinfo=dt.UTC)).total_seconds() / 3600 / 24
    return 360*__DEG_TO_RAD * (d - 81)/365

def __hour_angle(local_solar_time: dt.datetime) -> float:
    "Angle (in radians) the earth has rotated since noon"
    noon = local_solar_time.replace(hour=12, minute=0, second=0, microsecond=0)
    hours = (local_solar_time - noon).total_seconds() / 3600
    return 360*__DEG_TO_RAD * hours/24

def __equation_of_time(time_utc: dt.datetime) -> float:
    B = __year_angle(time_utc)
    return 9.87 * np.sin(2*B) - 7.53*np.cos(B) - 1.5*np.sin(B)

def __elevation(d: float, phi: float, hour_angle: float) -> float:
    """
    Sun elevation (angle above horizon) based pn the declination d, latitude phi, and hour angle"
    All angles in radians
    """
    return np.arcsin(
        np.sin(d)*np.sin(phi)
        + np.cos(d)*np.cos(phi)*np.cos(hour_angle)
    )

def __azimouth(d: float, phi: float, hour_angle: float, elevation: float) -> float:
    """
    Sun azimouth (angle from north) based pn the declination d, latitude phi,
    hour angle, and sun elevation.

    All angles in radians
    """
    return np.arccos(
        (
            np.sin(d)*np.cos(phi)
            - np.cos(d)*np.sin(phi)*np.cos(hour_angle)
        )
        / np.cos(elevation)
    )

def sun_position(latitude_deg: float, longitude_deg: float, time: dt.datetime) -> tuple[float, float]:
    """
    Returns the position of the sun in the sky as an (elevation, azimouth) tuple in radians
    """

    time_utc = time.astimezone(dt.UTC)
    time_correction_factor = 4 * longitude_deg + __equation_of_time(time_utc) # 4 minutes per degree of rotation
    local_solar_time = time_utc + dt.timedelta(minutes=time_correction_factor)
    hour_angle =  __hour_angle(local_solar_time)
    declination = 23.45*__DEG_TO_RAD * np.sin(__year_angle(time_utc))
    latitude = latitude_deg*__DEG_TO_RAD
    elevation = __elevation(declination, latitude, hour_angle)
    azimouth = __azimouth(declination, latitude, hour_angle, elevation)
    return (elevation, azimouth)