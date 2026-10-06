from pathlib import Path
import os

from elevation.data import SpatialData, ElevationBuffer
from elevation.config import Config


import numpy as np
from PIL import Image
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

class GifMaker:
    def __init__(self, frame_count: int, duration_seconds: float, output_dir: Path):
        if duration_seconds <= 0:
            raise ValueError("duration_seconds must be positive")
        if frame_count <= 0:
            raise ValueError("duration_seconds must be positive")

        duration_ms = round(duration_seconds * 1000)
        if not np.isclose(duration_seconds * 1000, duration_ms, rtol=0, atol=1e-9):
            raise ValueError(f"duration ({duration_ms}) must be a positive multiple of 10 ms")
        if duration_ms < frame_count:
            raise ValueError("duration must allow at least 10 ms per frame")

        self.duration_ms = duration_ms
        self.delay_ms = np.diff(np.linspace(0, duration_ms, frame_count+1, dtype=np.int32)).tolist()
        self.frame_count = frame_count
        self.frames: list[Image.Image] = []
        self.output_dir = Path(output_dir)
        self.progress_bar_used = (False, None)

    def append(self, buffer255: ElevationBuffer):
        if len(self.frames) > self.frame_count:
            print("[WARN] appending more frames than planned, GIF will last longer than requested")
        frame = np.rint(buffer255).astype(np.uint8)
        self.frames.append(Image.fromarray(frame))

    def progress_bar(self, bar_width=30, file=None):
        completed_width = bar_width * len(self.frames) // self.frame_count
        progress_bar = "=" * completed_width + " " * (bar_width - completed_width)
        print(
            f"\r[{progress_bar}] {len(self.frames)}/{self.frame_count} frames",
            end="",
            flush=True,
            file=file
        )
        self.progress_bar_used = (True, file)

    def save(self) -> Path:
        if len(self.frames) < self.frame_count:
            print("[WARN] saving GIF with fewer frames than planned, GIF will last less than requested")

        output_path = self.output_dir / "sunset.gif"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.frames[0].save(
            output_path,
            save_all=True,
            append_images=self.frames[1:],
            duration=self.delay_ms,
            loop=0,
            disposal=2,
            optimize=False,
        )
        return output_path

    def close(self):
        self.frames = []
        if self.progress_bar_used[0]:
            print(file=self.progress_bar_used[1])
            self.progress_bar_used = (None, None)
