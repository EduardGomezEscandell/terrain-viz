import sys
import elevation.config as config
import elevation.data as data
import elevation.draw as draw

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

def truncate(a: np.ndarray, qmin = 0.01, qmax = None, check_nan = True) -> np.ndarray:
    if check_nan:
        v = flat_nonan(a)
    else:
        v = a
    lo: float = np.quantile(v, qmin)
    hi: float = np.quantile(v, 1-qmin if qmax is None else qmax)
    return np.clip(a, lo, hi)

def draw_slopes(conf: config.Config, sd: data.SpatialData):
    sd.altered = scipy.ndimage.gaussian_filter(sd.altered, 10)
    grads = np.gradient(sd.altered)
    sd.altered = np.nan_to_num(100 * np.sqrt(grads[0]**2 + grads[1]**2) / sd.scale, False, 0.0)

    # Get rid of outliers
    sd.altered = np.clip(sd.altered, -100, 100)

    p = draw.TwoPlot(conf, sd)
    p.plot_original()
    p.plot_altered_1d("Slope %")
    p.commit()


def draw_northface(conf: config.Config, sd: data.SpatialData):
    sd.altered = scipy.ndimage.gaussian_filter(sd.altered, 10)
    grads = np.gradient(sd.altered)
    sd.altered = 100/sd.scale * np.nan_to_num(grads[0], False, 0.0)

    # Get rid of outliers
    sd.altered = truncate(sd.altered, 0.0, 0.5)

    p = draw.TwoPlot(conf, sd)
    p.plot_original()
    p.plot_altered_1d("Slope %")
    p.commit()


def main() -> int|None:
    conf = parse_args()
    sd = data.load(conf.data_directory, conf.downsample)

    match conf.style:
        case config.Style.slope:
            return draw_slopes(conf, sd)
        case config.Style.northface:
            return draw_northface(conf, sd)



