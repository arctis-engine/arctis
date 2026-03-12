from __future__ import annotations

import ast
from typing import Optional, Dict, Any

from core.validators.base import BaseValidator
from core.models import Issue, Severity, ValidationResult, Task


class SyntaxValidator(BaseValidator):
    """
    Deterministic, AST-based syntax validator for Arctic Brain v3.

    Eigenschaften:
    - nutzt v3 Issue-Objekte
    - nutzt Severity-Enums
    - AST-aware (AST wird vom Orchestrator geliefert)
    - niemals Dicts, niemals Strings als Issues
    - deterministische Fehlermeldungen
    """

    name = "syntax"

    def run(
        self,
        task: Task,
        specs: Dict[str, Any],
        code: str,
        ast_tree: Any,
        file_meta: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """
        SyntaxValidator v3:
        - nutzt den bereits geparsten AST (ast_tree)
        - falls der Orchestrator keinen AST liefern konnte, wird hier erneut geparst
        """

        # ------------------------------------------------------------
        # 1. Wenn der Orchestrator bereits einen AST geliefert hat → OK
        # ------------------------------------------------------------
        if ast_tree is not None:
            return ValidationResult(ok=True, issues=[], details={"source": "preparsed"})

        # ------------------------------------------------------------
        # 2. Falls kein AST geliefert wurde → selbst parsen
        # ------------------------------------------------------------
        try:
            parsed = ast.parse(code)
            return ValidationResult(
                ok=True,
                issues=[],
                details={"source": "self_parsed"},
            )

        except SyntaxError as e:
            # --------------------------------------------------------
            # 3. Issue-Objekt erzeugen (v3)
            # --------------------------------------------------------
            issue = Issue(
                code="syntax_error",
                message=f"SyntaxError: {e.msg or 'invalid syntax'}",
                severity=Severity.FATAL,
                location={
                    "line": e.lineno or None,
                    "col": e.offset or None,
                },
            )

            return ValidationResult(
                ok=False,
                issues=[issue],
                details={
                    "line": e.lineno,
                    "offset": e.offset,
                    "text": (e.text or "").rstrip(),
                },
            )
