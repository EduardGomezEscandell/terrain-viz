from os import listdir
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
import numpy as np

@dataclass
class SpatialData:
    longitude_range: tuple[float, float]
    latitude_range: tuple[float, float]
    scale: float
    width: int
    height: int
    original: np.ndarray
    altered: np.ndarray

    def __str__(self) -> str:
        return f"SpatialData(longitude_range={self.longitude_range}, latitude_range={self.latitude_range}, scale={self.scale}, width={self.width}, height={self.height})"

def _locate_by_extension(dir_path: str|Path, extension: str) -> Path:
    extension = extension if extension.startswith(".") else "." + extension

    contents = listdir(dir_path)
    filename = [p for p in contents if p.endswith(extension)]
    if len(filename) > 1:
        raise RuntimeError(f"Data directory contains multiple {extension} files")
    if len(filename) == 0:
        raise RuntimeError(f"Data directory contains no {extension} files")

    return Path(dir_path, filename[0])

def _load_colonfile(path: Path|str) -> dict[str, str]:
    """
    Loads any text file where each line has 'key : value' into a dict
    Empty lines are skipped
    Trailing and leading whitespace is trimmed
    """

    data = dict()
    with open(path) as f:
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            k, v = line.split(":")
            data[k.rstrip()] = v.lstrip()
    return data

def _tif_to_numpy(f: Path) -> np.ndarray:
    im = Image.open(f)
    return np.array(im)

def load(path: Path|str) -> SpatialData:
    metadata_path=_locate_by_extension(path, "txt")
    d = _load_colonfile(metadata_path)

    elevations_path=_locate_by_extension(path, ".tif")
    img = _tif_to_numpy(elevations_path)

    # Src format encodes no data as -9999
    img = np.where(img == -9999, np.nan, img)

    sd = SpatialData(
        latitude_range=(
            float(d["Coordenada sud (metres)"]),
            float(d["Coordenada nord (metres)"]),
        ),
        longitude_range=(
            float(d["Coordenada oest (metres)"]),
            float(d["Coordenada est (metres)"]),
        ),
        width=int(d["Nombre de píxels en X"]),
        height=int(d["Nombre de píxels en Y"]),
        scale=float(d["Tamany de píxel (metres)"]),
        original=img,
        altered=img,
    )

    if sd.height != sd.original.shape[0]:
        raise RuntimeError("Metadata file does not match elevation shape")
    if sd.width != sd.original.shape[1]:
            raise RuntimeError("Metadata file does not match elevation shape")
    return sd