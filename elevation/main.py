import sys
import elevation.config as config
import elevation.data as data
import elevation.draw as draw
import elevation.raytrace as raytrace

import numpy as np
import scipy.ndimage

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
    sd.altered = np.clip(180/np.pi * np.arctan2(sd.altered, sd.scale), -90, 90)

    p = draw.TwoPlot(conf, sd)
    p.plot_original()
    p.plot_altered_1d(f"Shading, lit from {int(angle)}° from north", cmap='gray')
    p.commit()


def draw_sunshine(conf: config.Config, sd: data.SpatialData):
    sun_azimuth = float(conf.style_args.pop("sun-azimuth", 0.0))
    sun_altitude = float(conf.style_args.pop("sun-altitude", 0.0))
    __warn_if_remaining_sargs(conf)

    raytrace.raytrace(sd.altered, sd.scale, sun_altitude, sun_azimuth)

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
