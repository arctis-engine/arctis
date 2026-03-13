from dataclasses import dataclass, field
from typing import List, Optional

from .base import BaseIR


@dataclass
class FunctionIR(BaseIR):
    name: str
    params: List[str] = field(default_factory=list)
    returns_type: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    body: str = ""
    docstring: Optional[str] = None
    async_def: bool = False
