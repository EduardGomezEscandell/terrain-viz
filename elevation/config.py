from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import yaml

from typing import Literal

class Style(Enum):
    slope = 'slope'
    northface = 'obaga'

    @classmethod
    def parse(cls, s: str):
        for v in cls:
            if v.value == s:
                return v
        raise ValueError(f"Style {s} not reconized")


@dataclass
class Config:
    data_directory: Path
    out_directory: Path
    style: Style
    downsample: int

def load(path: str) -> Config:
    with open(path) as f:
        raw = yaml.safe_load(f)

    return Config(
        data_directory=Path(raw["data-directory"]),
        out_directory=Path(raw["output-directory"]),
        style=Style.parse(raw['style']),
        downsample=int(raw.get('downsample', 1)),
    )