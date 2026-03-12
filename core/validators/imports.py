from __future__ import annotations

import ast
from typing import Dict, Any, Optional, List

from core.validators.base import BaseValidator
from core.models import Issue, Severity, ValidationResult, Task


class ImportValidator(BaseValidator):
    """
    Deterministic, AST-based import validator for Arctic Brain v3.

    Features:
    - AST-basiert, keine Regex-Falschalarme
    - erkennt verbotene Module (import + from import)
    - erkennt relative Imports (optional)
    - erkennt dynamische Imports (__import__, importlib.import_module)
    - sortierte, deterministische Ausgabe
    - snippet-safe: feuert nicht bei Code ohne Imports
    """

    name = "imports"

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
                    code="import_syntax_error",
                    message="Cannot parse code for import validation",
                    severity=Severity.FATAL,
                )
                return ValidationResult(ok=False, issues=[issue], details={})

        # ------------------------------------------------------------
        # 2. Regeln laden
        # ------------------------------------------------------------
        import_rules = specs.get("imports", {})

        forbidden = set(import_rules.get("forbidden", []))
        forbid_relative = import_rules.get("forbid_relative", False)
        forbid_dynamic = import_rules.get("forbid_dynamic", True)

        found_imports = []
        found_from_imports = []

        # ------------------------------------------------------------
        # 3. AST traversieren
        # ------------------------------------------------------------
        for node in ast.walk(ast_tree):

            # ----------------------------------------
            # import x, y
            # ----------------------------------------
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    found_imports.append(name)

                    if name in forbidden:
                        issues.append(
                            Issue(
                                code="forbidden_import",
                                message=f"Forbidden import: '{name}'",
                                severity=Severity.ERROR,
                                location={"line": node.lineno},
                            )
                        )

            # ----------------------------------------
            # from x import y
            # ----------------------------------------
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                found_from_imports.append(module)

                # Relative Imports
                if forbid_relative and node.level > 0:
                    issues.append(
                        Issue(
                            code="relative_import_forbidden",
                            message=f"Relative import not allowed: 'from .{module} import ...'",
                            severity=Severity.ERROR,
                            location={"line": node.lineno},
                        )
                    )

                # Verbotene Module
                if module in forbidden:
                    issues.append(
                        Issue(
                            code="forbidden_import",
                            message=f"Forbidden import: '{module}'",
                            severity=Severity.ERROR,
                            location={"line": node.lineno},
                        )
                    )

            # ----------------------------------------
            # Dynamische Imports
            # ----------------------------------------
            elif isinstance(node, ast.Call) and forbid_dynamic:

                # __import__("x")
                if isinstance(node.func, ast.Name) and node.func.id == "__import__":
                    issues.append(
                        Issue(
                            code="dynamic_import_forbidden",
                            message="Dynamic import via __import__() is forbidden",
                            severity=Severity.ERROR,
                            location={"line": node.lineno},
                        )
                    )

                # importlib.import_module("x")
                if (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "import_module"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "importlib"
                ):
                    issues.append(
                        Issue(
                            code="dynamic_import_forbidden",
                            message="Dynamic import via importlib.import_module() is forbidden",
                            severity=Severity.ERROR,
                            location={"line": node.lineno},
                        )
                    )

        # ------------------------------------------------------------
        # 4. Ergebnis zurückgeben (v3)
        # ------------------------------------------------------------
        ok = len([i for i in issues if i.severity in {Severity.ERROR, Severity.FATAL}]) == 0

        return ValidationResult(
            ok=ok,
            issues=issues,
            details={
                "imports": sorted(found_imports),
                "from_imports": sorted(found_from_imports),
                "applied_rules": import_rules,
            },
        )
