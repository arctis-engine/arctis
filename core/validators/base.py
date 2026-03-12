from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from core.models import Issue, Severity, ValidationResult, Task


class ValidatorContext:
    """
    Gemeinsamer Kontext für alle Validatoren in v3.
    Wird vom Orchestrator bereitgestellt.
    """

    def __init__(
        self,
        task: Task,
        specs: Dict[str, Any],
        code: str,
        ast_tree: Any,
        file_meta: Optional[Dict[str, Any]] = None,
    ):
        self.task = task
        self.specs = specs
        self.code = code
        self.ast = ast_tree
        self.file_meta = file_meta or {}


class BaseValidator(ABC):
    """
    Abstrakte Basis für alle Validatoren in Arctic Brain v3.

    Jeder Validator MUSS:
    - einen Namen haben
    - eine run()-Methode implementieren
    - Issue-Objekte zurückgeben
    - niemals crashen (Fehler → Issue mit Severity.FATAL)
    """

    name: str = "base"

    @abstractmethod
    def run(
        self,
        task: Task,
        specs: Dict[str, Any],
        code: str,
        ast_tree: Any,
        file_meta: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """
        Muss ein ValidationResult zurückgeben.
        """
        raise NotImplementedError

    # ------------------------------------------------------------
    # Helper: Issue erzeugen
    # ------------------------------------------------------------

    def issue(
        self,
        code: str,
        message: str,
        severity: Severity = Severity.ERROR,
        location: Optional[Dict[str, Any]] = None,
    ) -> Issue:
        return Issue(
            code=code,
            message=message,
            severity=severity,
            location=location,
        )

    # ------------------------------------------------------------
    # Helper: Erfolgreiches Ergebnis
    # ------------------------------------------------------------

    def ok(self) -> ValidationResult:
        return ValidationResult(ok=True, issues=[], details={})

    # ------------------------------------------------------------
    # Helper: Fehlerergebnis
    # ------------------------------------------------------------

    def fail(self, issues: List[Issue]) -> ValidationResult:
        return ValidationResult(ok=False, issues=issues, details={})
