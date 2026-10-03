import sys
import elevation.config as config
import elevation.data as data
import elevation.draw as draw
import elevation.raytrace as raytrace

import numpy as np
import scipy.ndimage
from PIL import Image

def parse_args() -> config.Config:
    match sys.argv:
        case "-h"|"--help":
            print("Sorry, haven't gotten around to this part yet")
            sys.exit(0)
        case [_, path]:
            return config.load(path)
        case [_]:
            return config.load("config.yaml")
        case [exec, *_]:
            print(f"Wrong usage. Use this command to see valid usage:\n\n    {exec} --help\n", file=sys.stderr)
            sys.exit(2)
        case _:
            raise NotImplementedError("Unreachable")

def flat_nonan(a: np.ndarray):
    v = a.flatten()
    return v[np.logical_not(np.isnan(v))]

def clip_outliers(a: np.ndarray, qmin = 0.01, qmax = None, check_nan = True) -> np.ndarray:
    if check_nan:
        v = flat_nonan(a)
    else:
        v = a
    lo: float = np.quantile(v, qmin)
    hi: float = np.quantile(v, 1-qmin if qmax is None else qmax)
    return np.clip(a, lo, hi)

def __warn_if_remaining_sargs(conf: config.Config):
    if conf.style_args:
        print(f"WARN: unrecognized style args: {[k for k in conf.style_args]}", file=sys.stderr)


def draw_slopes(conf: config.Config, sd: data.SpatialData):
    __warn_if_remaining_sargs(conf)

    sd.altered = scipy.ndimage.gaussian_filter(sd.altered, 10)
    grads = np.gradient(sd.altered)
    sd.altered = 100 * np.sqrt(grads[0]**2 + grads[1]**2) / sd.scale

    # Get rid of outliers
    sd.altered = clip_outliers(sd.altered)

    p = draw.TwoPlot(conf, sd)
    p.plot_original()
    p.plot_altered_1d("Slope %")
    p.commit()


def __vector_at_angle(angle: float):
    "Angle in radians"
    return np.array([np.cos(angle), -np.sin(angle)])

def draw_shading(conf: config.Config, sd: data.SpatialData):
    angle = conf.style_args.pop("angle", 0)
    __warn_if_remaining_sargs(conf)

    grad = np.gradient(sd.altered)
    v = __vector_at_angle(np.pi / 180 * angle)

    sd.altered = grad[0]*v[0] + grad[1]*v[1]
    sd.altered = np.nan_to_num(sd.altered, False, 0.0)

    # Get rid of outliers
    sd.altered = np.clip(180/np.pi * np.arctan2(sd.altered, sd.scale), -90, 90, dtype=data.ElevationFloat)

    p = draw.TwoPlot(conf, sd)
    p.plot_original()
    p.plot_altered_1d(f"Shading, lit from {int(angle)}° from north", cmap='gray')
    p.commit()


def draw_sunshine(conf: config.Config, sd: data.SpatialData):
    sun_azimuth = float(conf.style_args.pop("sun-azimuth", 0.0))
    sun_altitude = float(conf.style_args.pop("sun-altitude", 45.0))
    eye_level = float(conf.style_args.pop("eye-level", 1.7))

    __warn_if_remaining_sargs(conf)

    sd.altered = -9999*np.zeros_like(sd.original)
    raytrace.raytrace(sd.original, sd.altered, sd.scale, sun_azimuth, sun_altitude, eye_level)

    p = draw.TwoPlot(conf, sd)
    p.plot_original()
    p.plot_altered_1d(f"Shadows. Azimouth: {int(sun_azimuth)}°, altitude: {int(sun_altitude)}°, eye level: {eye_level:.2f}", cmap='gray')
    p.commit()


def draw_sunset_animation(conf: config.Config, sd: data.SpatialData):
    sun_azimuth = float(conf.style_args.pop("sun-azimuth", 0.0))
    sun_altitude = float(conf.style_args.pop("sun-altitude", 45.0))
    end_azimuth = float(conf.style_args.pop("sun-azimuth-end"))
    end_altitude = float(conf.style_args.pop("sun-altitude-end"))
    eye_level = float(conf.style_args.pop("eye-level", 1.7))
    frame_count_value = float(conf.style_args.pop("frames"))
    if not frame_count_value.is_integer():
        raise ValueError("frames must be a positive integer")
    frame_count = int(frame_count_value)
    duration_seconds = float(conf.style_args.pop("duration", 4.0))
    __warn_if_remaining_sargs(conf)

    if frame_count <= 0:
        raise ValueError("frames must be a positive integer")

    duration_centiseconds = round(duration_seconds * 100)
    if duration_seconds <= 0 or not np.isclose(duration_seconds * 100, duration_centiseconds, rtol=0, atol=1e-9):
        raise ValueError("duration must be a positive multiple of 0.01 seconds")
    if duration_centiseconds < frame_count:
        raise ValueError("duration must allow at least 0.01 seconds per frame")

    delays_centiseconds = [
        (i + 1) * duration_centiseconds // frame_count
        - i * duration_centiseconds // frame_count
        for i in range(frame_count)
    ]
    azimuths = np.linspace(sun_azimuth, end_azimuth, frame_count)
    altitudes = np.linspace(sun_altitude, end_altitude, frame_count)
    rendered_frames = []

    print(f"Rendering {frame_count} sunset frames...")
    for azimuth, altitude in zip(azimuths, altitudes):
        sd.altered = np.zeros_like(sd.original)
        raytrace.raytrace(sd.original, sd.altered, sd.scale, azimuth, altitude, eye_level)
        frame = np.where(sd.altered > 0.5, 255, 0).astype(np.uint8)
        rendered_frames.append(Image.fromarray(frame))

    output_path = conf.out_directory / "sunset.gif"
    conf.out_directory.mkdir(parents=True, exist_ok=True)
    rendered_frames[0].save(
        output_path,
        save_all=True,
        append_images=rendered_frames[1:],
        duration=[delay * 10 for delay in delays_centiseconds],
        loop=0,
        disposal=2,
        optimize=False,
    )
    print(f"Saved sunset animation to {output_path}")


def main() -> int|None:
    conf = parse_args()
    sd = data.load(conf.data_directory, conf.downsample)

    match conf.style:
        case config.Style.slope:
            return draw_slopes(conf, sd)
        case config.Style.shading:
            return draw_shading(conf, sd)
        case config.Style.sunshine:
            return draw_sunshine(conf, sd)
        case config.Style.sunset_animation:
            return draw_sunset_animation(conf, sd)
