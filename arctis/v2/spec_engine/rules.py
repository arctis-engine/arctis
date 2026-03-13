from abc import ABC, abstractmethod
from typing import Tuple, List, Set, Optional

from .context import SpecContext


class Rule(ABC):
    """
    Basisklasse für alle Regeln.
    """

    @abstractmethod
    def evaluate(self, context: SpecContext) -> Tuple[bool, str]:
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.__class__.__name__


class AllowedFilesRule(Rule):
    def __init__(self, allowed_paths: List[str]):
        self.allowed_paths: Set[str] = set(allowed_paths)

    def evaluate(self, context: SpecContext) -> Tuple[bool, str]:
        if not self.allowed_paths:
            return True, "AllowedFilesRule: no restrictions configured."
        if context.file_path in self.allowed_paths:
            return True, f"AllowedFilesRule: file '{context.file_path}' is allowed."
        return False, f"AllowedFilesRule: file '{context.file_path}' is not allowed."


class PatchModeRule(Rule):
    def __init__(self, allowed_modes: List[str]):
        self.allowed_modes: Set[str] = set(allowed_modes)

    def evaluate(self, context: SpecContext) -> Tuple[bool, str]:
        mode: Optional[str] = context.get_metadata("patch_mode")
        if mode is None:
            return False, "PatchModeRule: no patch_mode provided in context metadata."
        if mode in self.allowed_modes:
            return True, f"PatchModeRule: patch mode '{mode}' is allowed."
        return False, (
            f"PatchModeRule: patch mode '{mode}' is not allowed. "
            f"Allowed: {sorted(self.allowed_modes)}."
        )


class ForbiddenPatternRule(Rule):
    def __init__(self, forbidden_patterns: List[str]):
        self.forbidden_patterns = forbidden_patterns

    def evaluate(self, context: SpecContext) -> Tuple[bool, str]:
        for pattern in self.forbidden_patterns:
            if pattern in context.new_source:
                return False, (
                    f"ForbiddenPatternRule: forbidden pattern '{pattern}' "
                    f"found in new source."
                )
        return True, "ForbiddenPatternRule: no forbidden patterns found."


class AllowedSymbolsRule(Rule):
    def __init__(self, allowed_new_symbols: List[str]):
        self.allowed_new_symbols: Set[str] = set(allowed_new_symbols)

    def evaluate(self, context: SpecContext) -> Tuple[bool, str]:
        if context.symbols_before is None or context.symbols_after is None:
            return False, "AllowedSymbolsRule: no symbol information provided."

        before = set(context.symbols_before.keys())
        after = set(context.symbols_after.keys())
        added = after - before

        if not added:
            return True, "AllowedSymbolsRule: no new symbols added."

        disallowed = [s for s in added if s not in self.allowed_new_symbols]
        if disallowed:
            return False, (
                f"AllowedSymbolsRule: new symbols not allowed: {disallowed}. "
                f"Allowed: {sorted(self.allowed_new_symbols)}."
            )

        return True, (
            f"AllowedSymbolsRule: all new symbols are allowed: {sorted(added)}."
        )
