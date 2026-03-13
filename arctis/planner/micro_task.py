from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class MicroTask:
    file_path: str
    instruction: str
    priority: int = 10
    mode: str = "generate"  # generate | modify | append | create
    metadata: Dict = field(default_factory=dict)
    old_source: Optional[str] = None
