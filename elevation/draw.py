from elevation.data import SpatialData
from elevation.config import Config
import numpy as np

import os

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

class TwoPlot:
    def __init__(self, c: Config, sd: SpatialData):
        os.makedirs(c.out_directory, 0o700, exist_ok=True)
        self.fig, self.axs = plt.subplots(nrows=1, ncols=2, sharey=True, figsize=(20, 10))
        self.fig.tight_layout()
        self.sd = sd
        self.config = c

        use_kilometers = max([sd.width, sd.height]) >= 5000 / sd.scale

        self.units = "km" if use_kilometers else "m"

        scale = (1000 if use_kilometers else 1) * sd.scale
        self.extent=(0.0, sd.width*scale, 0.0, sd.height*scale)

    def plot_original(self):
        ax: Axes = self.axs[0]
        ax.set_title("Original")
        pos = ax.imshow(self.sd.original, extent=self.extent)
        ax.set_ylabel(f"({self.units})")
        ax.set_xlabel(f"({self.units})")
        cb = self.fig.colorbar(pos, ax=ax, orientation='horizontal')
        cb.set_label("Elevation")
        return ax

    def plot_altered_1d(self, clabel: str, **kwargs):
        ax: Axes = self.axs[1]
        ax.set_title("Altered")
        pos = ax.imshow(self.sd.altered, extent=self.extent, **kwargs)
        ax.set_xlabel(f"({self.units})")
        cb = self.fig.colorbar(pos, ax=ax, orientation='horizontal')
        cb.set_label(clabel)
        return ax

    def commit(self):
        self.fig.savefig(self.config.out_directory / "image.png")