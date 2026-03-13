from dataclasses import dataclass


@dataclass
class BaseIR:
    file_path: str
    layer: str
