from __future__ import annotations

import ast
import re
from typing import Dict, Any, Optional, List

from core.validators.base import BaseValidator
from core.models import Issue, Severity, ValidationResult, Task


# ============================================================
#  Strict Naming Rules (Arctic Brain v3)
# ============================================================

SNAKE_CASE = re.compile(r"^[a-z][a-z0-9_]*$")
CAMEL_CASE = re.compile(r"^[a-z][a-zA-Z0-9]*$")
PASCAL_CASE = re.compile(r"^[A-Z][a-zA-Z0-9]*$")


def _is_snake_case(name: str) -> bool:
    return bool(SNAKE_CASE.fullmatch(name))


def _is_camel_case(name: str) -> bool:
    return bool(CAMEL_CASE.fullmatch(name))


def _is_pascal_case(name: str) -> bool:
    return bool(PASCAL_CASE.fullmatch(name))


# ============================================================
#  Naming Validator v3
# ============================================================

class NamingValidator(BaseValidator):
    """
    Deterministic, snippet-aware naming validator for Arctic Brain v3.

    Eigenschaften:
    - niemals blockierend (Severity = WARNING)
    - AST-basiert, keine Regex-Falschalarme
    - respektiert Spec-Regeln
    - deterministische Sortierung
    """

    name = "naming"

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
                # Naming darf niemals blockieren
                issues.append(
                    Issue(
                        code="naming_parse_warning",
                        message="NamingValidator: cannot parse code",
                        severity=Severity.WARNING,
                    )
                )
                return ValidationResult(ok=True, issues=issues, details={})

        # ------------------------------------------------------------
        # 2. Regeln laden
        # ------------------------------------------------------------
        naming_rules = specs.get("naming", {})

        function_case = naming_rules.get("function_case", "snake_case")
        class_case = naming_rules.get("class_case", "PascalCase")
        allow_private = naming_rules.get("allow_private_prefix", True)

        found_functions = []
        found_classes = []

        # ------------------------------------------------------------
        # 3. AST traversieren
        # ------------------------------------------------------------
        for node in ast.walk(ast_tree):

            # ----------------------------------------
            # Function names
            # ----------------------------------------
            if isinstance(node, ast.FunctionDef):
                name = node.name
                found_functions.append(name)

                # private Funktionen erlauben
                if allow_private and name.startswith("_"):
                    continue

                # Naming rules
                if function_case == "snake_case" and not _is_snake_case(name):
                    issues.append(
                        Issue(
                            code="function_naming_violation",
                            message=f"Function name not snake_case: '{name}'",
                            severity=Severity.WARNING,
                            location={"line": node.lineno},
                        )
                    )

                elif function_case == "camelCase" and not _is_camel_case(name):
                    issues.append(
                        Issue(
                            code="function_naming_violation",
                            message=f"Function name not camelCase: '{name}'",
                            severity=Severity.WARNING,
                            location={"line": node.lineno},
                        )
                    )

                elif function_case == "PascalCase" and not _is_pascal_case(name):
                    issues.append(
                        Issue(
                            code="function_naming_violation",
                            message=f"Function name not PascalCase: '{name}'",
                            severity=Severity.WARNING,
                            location={"line": node.lineno},
                        )
                    )

            # ----------------------------------------
            # Class names
            # ----------------------------------------
            elif isinstance(node, ast.ClassDef):
                name = node.name
                found_classes.append(name)

                if class_case == "PascalCase" and not _is_pascal_case(name):
                    issues.append(
                        Issue(
                            code="class_naming_violation",
                            message=f"Class name not PascalCase: '{name}'",
                            severity=Severity.WARNING,
                            location={"line": node.lineno},
                        )
                    )

                elif class_case == "snake_case" and not _is_snake_case(name):
                    issues.append(
                        Issue(
                            code="class_naming_violation",
                            message=f"Class name not snake_case: '{name}'",
                            severity=Severity.WARNING,
                            location={"line": node.lineno},
                        )
                    )

        # ------------------------------------------------------------
        # 4. Ergebnis zurückgeben (v3)
        # ------------------------------------------------------------
        return ValidationResult(
            ok=True,  # NamingValidator blockiert NIE
            issues=sorted(issues, key=lambda i: i.message),
            details={
                "functions": sorted(found_functions),
                "classes": sorted(found_classes),
                "applied_rules": naming_rules,
            },
        )
