from typing import List

from .rules import (
    AllowedFilesRule,
    PatchModeRule,
    ForbiddenPatternRule,
    AllowedSymbolsRule,
)
from .ruleset import RuleSet


def default_ruleset() -> RuleSet:
    """
    Sehr konservatives Default-Regelset.
    - Kein Full-Rewrite
    - Keine gefährlichen Patterns
    """
    rules = [
        PatchModeRule(allowed_modes=["insert", "append", "replace_line"]),
        ForbiddenPatternRule(
            forbidden_patterns=[
                "eval(",
                "exec(",
                "subprocess.Popen(",
                "os.system(",
            ]
        ),
    ]
    return RuleSet(rules=rules, name="default_ruleset")


def strict_no_rewrite_ruleset(allowed_files: List[str]) -> RuleSet:
    rules = [
        AllowedFilesRule(allowed_paths=allowed_files),
        PatchModeRule(allowed_modes=["insert", "append", "replace_line"]),
        ForbiddenPatternRule(
            forbidden_patterns=[
                "eval(",
                "exec(",
                "os.system(",
                "subprocess.Popen(",
            ]
        ),
    ]
    return RuleSet(rules=rules, name="strict_no_rewrite")


def multi_file_refactor_ruleset(
    allowed_files: List[str],
    allowed_new_symbols: List[str],
) -> RuleSet:
    rules = [
        AllowedFilesRule(allowed_paths=allowed_files),
        PatchModeRule(allowed_modes=["insert", "append", "replace_line"]),
        AllowedSymbolsRule(allowed_new_symbols=allowed_new_symbols),
        ForbiddenPatternRule(
            forbidden_patterns=[
                "eval(",
                "exec(",
                "os.system(",
            ]
        ),
    ]
    return RuleSet(rules=rules, name="multi_file_refactor")
