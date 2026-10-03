from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import sys

import yaml

class Style(Enum):
    slope = 'slope'
    shading = 'shading'
    sunshine = 'sunshine'

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
    style_args: dict

def load(path: str) -> Config:
    with open(path) as f:
        raw = {k: v for k,v in yaml.safe_load(f).items() if v is not None}

    conf = Config(
        data_directory=Path(raw.pop("data-directory")),
        out_directory=Path(raw.pop("output-directory")),
        downsample=int(raw.pop('downsample', 1)),
        style=Style.parse(raw.pop('style')),
        style_args=dict(raw.pop('style-args', {})),
    )

    if len(raw) != 0:
        print(f"WARN: unrecognized args: {[k for k in conf.style_args]}", file=sys.stderr)

    return conf