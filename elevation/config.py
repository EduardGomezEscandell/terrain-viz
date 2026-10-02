from pathlib import Path
from dataclasses import dataclass
import yaml

@dataclass
class Config:
    data_directory: Path
    out_directory: Path

def load(path: str) -> Config:
    with open(path) as f:
        raw = yaml.safe_load(f)
    
    return Config(
        data_directory=Path(raw["data-directory"]),
        out_directory=Path(raw["output-directory"]),
    )