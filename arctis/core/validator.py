from __future__ import annotations

import ast
from typing import List, Dict, Any

from core.models import (
    Issue,
    Severity,
    ValidationResult,
    Task,
)
from core.validators.base import BaseValidator
from core.validators.syntax import SyntaxValidator
from core.validators.imports import ImportValidator
from core.validators.naming import NamingValidator
from core.validators.structure import StructureValidator


# ============================================================
#  Validator-Profile pro Task-Typ (v3)
# ============================================================

VALIDATOR_PROFILES = {
    "codegen.single_function": [SyntaxValidator, NamingValidator],
    "codegen.file": [SyntaxValidator, ImportValidator, NamingValidator, StructureValidator],
    "patch.refactor": [SyntaxValidator, StructureValidator],
    "patch.fix_bug": [SyntaxValidator, ImportValidator],
    "analysis.review": [SyntaxValidator, StructureValidator],
}

DEFAULT_VALIDATORS = [SyntaxValidator]


# ============================================================
#  LLM-Output-Normalisierung (v3)
# ============================================================

def normalize_llm_code_output(raw: str) -> str:
    """
    Entfernt Backticks, trimmt Whitespace und sorgt für deterministische
    Code-Normalisierung. Kein Markdown-Parsing.
    """
    if not raw:
        return ""

    cleaned = raw.replace("```", "").strip()
    return cleaned


# ============================================================
#  Validator-Lader (v3)
# ============================================================

def load_validators_for_task(task_type: str) -> List[BaseValidator]:
    classes = VALIDATOR_PROFILES.get(task_type, DEFAULT_VALIDATORS)
    return [cls() for cls in classes]


# ============================================================
#  Haupt-Validierungsfunktion (v3)
# ============================================================

def validate_code(task: Task, specs: Dict[str, Any], code: str) -> ValidationResult:
    """
    Führt alle relevanten Validatoren aus und aggregiert Issues.
    - AST wird einmalig geparst und an alle Validatoren weitergegeben.
    - Jeder Validator liefert Issue-Objekte.
    - Severity-Level bestimmen, ob der Code blockiert.
    """

    # --------------------------------------------------------
    # 1. LLM-Output normalisieren
    # --------------------------------------------------------
    code = normalize_llm_code_output(code)

    # --------------------------------------------------------
    # 2. AST einmalig parsen
    # --------------------------------------------------------
    try:
        parsed_ast = ast.parse(code)
    except SyntaxError as e:
        issue = Issue(
            code="syntax_error",
            message=f"SyntaxError: {e}",
            severity=Severity.FATAL,
            location={"line": e.lineno, "col": e.offset},
        )
        return ValidationResult(ok=False, issues=[issue], details={"ast": None})

    # --------------------------------------------------------
    # 3. Validatoren laden
    # --------------------------------------------------------
    validators = load_validators_for_task(task.type)

    all_issues: List[Issue] = []
    per_validator: Dict[str, Any] = {}

    # --------------------------------------------------------
    # 4. Validatoren ausführen
    # --------------------------------------------------------
    for validator in validators:
        try:
            result = validator.run(
                task=task,
                specs=specs,
                code=code,
                ast_tree=parsed_ast,
            )
        except Exception as e:
            # Harte Fehler im Validator → FATAL Issue
            fatal_issue = Issue(
                code="validator_crash",
                message=f"Validator '{validator.name}' crashed: {e}",
                severity=Severity.FATAL,
            )
            return ValidationResult(
                ok=False,
                issues=[fatal_issue],
                details={"validator": validator.name},
            )

        # ValidatorResult → Issues extrahieren
        per_validator[validator.name] = {
            "issues": result.issues,
            "ok": result.ok,
        }

        all_issues.extend(result.issues)

    # --------------------------------------------------------
    # 5. Blocking-Logik (ERROR + FATAL blockieren)
    # --------------------------------------------------------
    blocking = [i for i in all_issues if i.severity in {Severity.ERROR, Severity.FATAL}]
    ok = len(blocking) == 0

    # --------------------------------------------------------
    # 6. Ergebnis zurückgeben
    # --------------------------------------------------------
    return ValidationResult(
        ok=ok,
        issues=all_issues,
        details={
            "per_validator": per_validator,
            "blocking": blocking,
        },
    )


# ============================================================
#  Fehlerformatierung (v3)
# ============================================================

def format_validation_errors(validation: ValidationResult) -> str:
    """
    Gibt eine menschenlesbare Fehlerliste zurück.
    """
    lines = []
    for issue in validation.issues:
        loc = ""
        if issue.location:
            loc = f" (line {issue.location.get('line')}, col {issue.location.get('col')})"
        lines.append(f"[{issue.severity}] {issue.code}: {issue.message}{loc}")
    return "\n".join(lines)
