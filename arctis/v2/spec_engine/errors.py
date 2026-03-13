from dataclasses import dataclass
from typing import Optional, Type


class SpecEngineError(Exception):
    """
    Basisklasse für alle Spec-Engine-Fehler.
    """


@dataclass
class RuleViolation:
    """
    Repräsentiert eine einzelne Regelverletzung.
    """
    rule_type: Type
    message: str
    file_path: Optional[str] = None
    rule_name: Optional[str] = None

    def __str__(self) -> str:
        base = f"{self.rule_type.__name__}: {self.message}"
        if self.file_path:
            base += f" (file={self.file_path})"
        if self.rule_name:
            base += f" [ruleset={self.rule_name}]"
        return base
