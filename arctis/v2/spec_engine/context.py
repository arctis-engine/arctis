from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class SpecContext:
    """
    Kontext für die Spec-Engine.
    Wird von v1/v2 befüllt und an alle Rules übergeben.
    """
    file_path: str
    patch: Any
    old_source: str
    new_source: str
    symbols_before: Optional[Dict[str, Any]] = None
    symbols_after: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_metadata(self, key: str, default=None):
        return self.metadata.get(key, default)
