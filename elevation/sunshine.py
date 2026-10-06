import datetime as dt
import elevation.astronomy as astro
import elevation.config as config
import elevation.draw as draw
import elevation.raytrace as raytrace
import elevation.data as data
from elevation.draw import GifMaker

import numpy as np
from PIL import Image

def __parse_subsampling_level(conf: config.Config) -> int:
    value = float(conf.style_args.pop("subsampling-level", 0))
    if not value.is_integer() or not 0 <= value <= 2:
        raise ValueError("subsampling-level must be 0, 1, or 2")
    return int(value)

def __parse_sun_position(conf: config.Config, suffix: str = ""):
    has_timestamp =  f"timestamp{suffix}" in conf.style_args
    has_sun_angle = f"sun-azimuth{suffix}" in conf.style_args or f"sun-altitude{suffix}" in conf.style_args

    if has_timestamp == int(has_sun_angle):
        raise RuntimeError(f"Incompatible arguments: specify one, and only one of these two options: (a) 'timestamp{suffix}', or (b) 'sun-azimuth{suffix}' and 'sun-altitude{suffix}'")

    if has_timestamp:
        ts = conf.style_args["timestamp"]
        return {"format": "timestamp", "timestamp": dt.datetime.fromisoformat(ts)}

    if has_sun_angle:
        sun_azimuth = float(conf.style_args.pop(f"sun-azimuth{suffix}", 0.0))
        sun_altitude = float(conf.style_args.pop(f"sun-altitude{suffix}", 45.0))
        return {"format": "angles", "azimuth": sun_azimuth, "altitude": sun_altitude}

    raise NotImplemented("Unreachable")

def draw_static(conf: config.Config, sd: data.SpatialData):
    sun_data = __parse_sun_position(conf)
    eye_level = float(conf.style_args.pop("eye-level", 1.7))
    subsampling_level = __parse_subsampling_level(conf)

    conf.warn_if_remaining_style_args()

    sd.altered = -9999*np.zeros_like(sd.original)

    title = ""
    if sun_data["format"] == "angles":
        az = sun_data["azimuth"]
        alt = sun_data["altitude"]
        raytrace.raytrace_fixedsource(sd.original, sd.altered, sd.scale, az, alt, eye_level, subsampling_level)
        title = f"Shadows. Azimuth: {int(sun_data["azimuth"])}°, altitude: {int(sun_data["altitude"])}°, eye level: {eye_level:.2f}"
    else:
        raise NotImplemented("TODO")

    p = draw.TwoPlot(conf, sd)
    p.plot_original()
    p.plot_altered_1d(title, cmap='gray')
    p.commit()


def draw_animation(conf: config.Config, sd: data.SpatialData):
    start_sundata = __parse_sun_position(conf, "-start")
    end_sundata = __parse_sun_position(conf, "-end")
    if start_sundata["format"] != end_sundata["format"]:
        raise ValueError("Both start and end sun data must be in the same format (either explicit positions or a timestamp)")

    eye_level = float(conf.style_args.pop("eye-level", 1.7))
    subsampling_level = __parse_subsampling_level(conf)

    frame_count = int(conf.style_args.pop("frames"))
    duration = float(conf.style_args.pop("duration", 4.0))

    conf.warn_if_remaining_style_args()

    gif = GifMaker(frame_count=frame_count, duration_seconds=duration, output_dir=conf.out_directory)

    data_is_angles = start_sundata["format"] == "angles"
    
    azimuths, altitudes, timestamps = [], [], []
    if data_is_angles:
        azimuths = np.linspace(start_sundata["azimuth"], end_sundata["azimuth"], frame_count)
        altitudes = np.linspace(start_sundata["altitude"], end_sundata["altitude"], frame_count)
    else:
        ts_begin: dt.datetime = start_sundata["timestamp"]
        ts_end: dt.datetime = end_sundata["timestamp"]
        epoch = dt.datetime(1970, 1, 1, tzinfo=dt.UTC)
        timestamps = np.linspace((ts_begin-epoch).total_seconds(), (ts_end-epoch).total_seconds(), frame_count)

    print(f"Rendering...")

    for i in range(frame_count):
        sd.altered = np.zeros_like(sd.original)

        if data_is_angles:
            az = azimuths[i]
            alt = altitudes[i]
            raytrace.raytrace_fixedsource(sd.original, sd.altered, sd.scale, az, alt, eye_level, subsampling_level)
        else:
            ts = timestamps[i]
            raise NotImplemented("TODO")

        gif.append(255 * sd.altered) # The data is in range 0-1, GifMaker wants 0-255
        gif.progress_bar(30)

    path = gif.save()
    print(f"Saved sunset animation to {path}")

    gif.close()
