from dataclasses import dataclass, field
from typing import List

from .base import BaseIR


@dataclass
class ModelIR(BaseIR):
    class_name: str                      # "User"
    fields: List[str] = field(default_factory=list)  # ["id", "name", "email"]
