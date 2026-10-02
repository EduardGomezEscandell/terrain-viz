from elevation.data import SpatialData
from elevation.config import Config
import numpy as np

import os

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

def draw(c: Config, sd: SpatialData, ylabel: str):
    os.makedirs(c.out_directory, 0o700, exist_ok=True)

    fig, axs = plt.subplots(nrows=1, ncols=2, sharey=True, figsize=(20, 10))
    fig.tight_layout()

    extent=(0.0, sd.width*sd.scale, 0.0, sd.height*sd.scale)
    units = "m"
    if max(extent) >= 5000:
        extent = (
            extent[0]//1000,extent[1]//1000,extent[2]//1000,extent[3]//1000
        )
        units = "km"
   
    ax: Axes = axs[0]
    ax.set_title("Original")
    pos = ax.imshow(sd.original, extent=extent)
    ax.set_ylabel(f"({units})")
    ax.set_xlabel(f"({units})")
    cb = fig.colorbar(pos, ax=ax, orientation='horizontal')
    cb.set_label("Elevation")

    ax: Axes = axs[1]
    ax.set_title("Altered")
    pos = ax.imshow(sd.altered, extent=extent)
    ax.set_xlabel(f"({units})")
    cb = fig.colorbar(pos, ax=ax, orientation='horizontal')
    cb.set_label(ylabel)

    fig.savefig(c.out_directory / "image.png")