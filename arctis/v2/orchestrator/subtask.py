from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class Subtask:
    """
    Beschreibt eine einzelne Dateioperation innerhalb eines Multi-File-Tasks.
    """
    file_path: str
    instruction: str
    metadata: Dict[str, Any]
