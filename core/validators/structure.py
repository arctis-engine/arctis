from __future__ import annotations

import ast
from typing import Dict, Any, Optional, List

from core.validators.base import BaseValidator
from core.models import Issue, Severity, ValidationResult, Task


class StructureValidator(BaseValidator):
    """
    Deterministic, snippet-aware structure validator for Arctic Brain v3.

    Features:
    - AST-basiert, keine Regex-Falschalarme
    - snippet-aware: ein einzelnes Top-Level-Element → niemals Fehler
    - respektiert spec-Regeln (max classes, max functions, forbid_multiple_classes)
    - deterministische, sortierte Ausgabe
    """

    name = "structure"

    def run(
        self,
        task: Task,
        specs: Dict[str, Any],
        code: str,
        ast_tree: Any,
        file_meta: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:

        issues: List[Issue] = []

        # ------------------------------------------------------------
        # 1. AST nutzen (vom Orchestrator geliefert)
        # ------------------------------------------------------------
        if ast_tree is None:
            try:
                ast_tree = ast.parse(code)
            except SyntaxError:
                issue = Issue(
                    code="structure_parse_error",
                    message="StructureValidator: cannot parse code",
                    severity=Severity.FATAL,
                )
                return ValidationResult(ok=False, issues=[issue], details={})

        # ------------------------------------------------------------
        # 2. Top-Level-Elemente extrahieren
        # ------------------------------------------------------------
        top_level = list(ast.iter_child_nodes(ast_tree))
        classes = [n for n in top_level if isinstance(n, ast.ClassDef)]
        functions = [n for n in top_level if isinstance(n, ast.FunctionDef)]

        # ------------------------------------------------------------
        # 3. Regeln laden
        # ------------------------------------------------------------
        structure_rules = specs.get("structure", {})

        max_classes = structure_rules.get("max_top_level_classes")
        max_functions = structure_rules.get("max_top_level_functions")
        forbid_multiple_classes = structure_rules.get("forbid_multiple_classes", False)

        # ------------------------------------------------------------
        # 4. Snippet-Awareness
        # ------------------------------------------------------------
        # Ein einzelnes Top-Level-Element → kein Modul → niemals Fehler
        if len(classes) == 0 and len(functions) <= 1:
            return ValidationResult(
                ok=True,
                issues=[],
                details={
                    "classes": [],
                    "functions": [f.name for f in functions],
                    "class_count": 0,
                    "function_count": len(functions),
                    "snippet_mode": True,
                    "applied_rules": structure_rules,
                },
            )

        # ------------------------------------------------------------
        # 5. Modul-Modus: Regeln anwenden
        # ------------------------------------------------------------

        # Regel: max_top_level_classes
        if isinstance(max_classes, int) and len(classes) > max_classes:
            issues.append(
                Issue(
                    code="too_many_classes",
                    message=f"Too many top-level classes: found {len(classes)}, allowed {max_classes}",
                    severity=Severity.ERROR,
                )
            )

        # Regel: forbid_multiple_classes
        if forbid_multiple_classes and len(classes) > 1:
            issues.append(
                Issue(
                    code="multiple_classes_forbidden",
                    message=f"Multiple top-level classes found: {[c.name for c in classes]}",
                    severity=Severity.ERROR,
                )
            )

        # Regel: max_top_level_functions
        if isinstance(max_functions, int) and len(functions) > max_functions:
            issues.append(
                Issue(
                    code="too_many_functions",
                    message=f"Too many top-level functions: found {len(functions)}, allowed {max_functions}",
                    severity=Severity.ERROR,
                )
            )

        # ------------------------------------------------------------
        # 6. Ergebnis zurückgeben (v3)
        # ------------------------------------------------------------
        blocking = [i for i in issues if i.severity in {Severity.ERROR, Severity.FATAL}]
        ok = len(blocking) == 0

        return ValidationResult(
            ok=ok,
            issues=sorted(issues, key=lambda i: i.message),
            details={
                "classes": sorted([c.name for c in classes]),
                "functions": sorted([f.name for f in functions]),
                "class_count": len(classes),
                "function_count": len(functions),
                "snippet_mode": False,
                "applied_rules": structure_rules,
            },
        )
