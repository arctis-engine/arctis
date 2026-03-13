from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class ExpansionBlueprint:
    """
    Beschreibt eine geplante Erweiterung von Arctis.
    """
    target_path: str
    description: str
    metadata: Dict[str, Any]
