from elevation.data import SpatialData
from elevation.config import Config
import numpy as np

import os

import matplotlib.colors
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

class TwoPlot:
    def __init__(self, c: Config, sd: SpatialData):
        os.makedirs(c.out_directory, 0o700, exist_ok=True)
        figs: list = [None, None]
        axs: list  = [None, None]

        figs[0], axs[0] = plt.subplots(nrows=1, ncols=2, sharey=True, figsize=(20, 10))
        figs[0].tight_layout()

        aspect_ratio = sd.original.shape[0]/sd.original.shape[1]
        figs[1], axs[1] = plt.subplots(nrows=1, ncols=1, figsize=(10,10*aspect_ratio))

        self.figs: list[Figure] = [f for f in figs if isinstance(f, Figure)]
        self.axes: list[list[Axes]] = [[a] if isinstance(a, Axes) else a for a in axs]

        self.sd = sd
        self.config = c

        use_kilometers = max([sd.width, sd.height]) >= 5000 / sd.scale
        scale = (0.001 if use_kilometers else 1) * sd.scale
        self.units = "km" if use_kilometers else "m"
        self.extent=(0.0, sd.width*scale, 0.0, sd.height*scale)

    def plot_original(self, **kwargs):
        ax = self.axes[0][0]
        ax.set_title("Original")

        class ZeroIsUnder(matplotlib.colors.Normalize):
            "Cheap trick to paint the sea blue"
            def __call__(self, value, clip=None):
                normalized = super().__call__(value, clip)
                return np.ma.where(np.ma.asarray(value) == 0.0, -1.0, normalized)

        cmap = plt.get_cmap(kwargs.get("cmap", "summer")).copy()
        cmap.set_bad("lightgray")  # no data
        cmap.set_under("blue")     # The sea
        pos = ax.imshow(
            self.sd.original,
            extent=self.extent,
            cmap=cmap,
            norm=ZeroIsUnder(),
            interpolation="nearest")

        ax.set_ylabel(f"({self.units})")
        ax.set_xlabel(f"({self.units})")
        cb = self.figs[0].colorbar(pos, ax=ax, orientation='horizontal')
        cb.set_label("Elevation")

    def plot_altered_1d(self, clabel: str, **kwargs):
        for i, _ in enumerate(self.figs):
            axs = self.axes[i]
            fig = self.figs[i]
            ax = axs[-1]
            ax.set_title("Altered")
            pos = ax.imshow(self.sd.altered, extent=self.extent, **kwargs)
            ax.set_xlabel(f"({self.units})")
            cb = fig.colorbar(pos, ax=ax, orientation='horizontal')
            cb.set_label(clabel)

    def commit(self):
        for i, fig in enumerate(self.figs):
            fig.savefig(self.config.out_directory / f"image{i}.png")
            plt.close(fig)