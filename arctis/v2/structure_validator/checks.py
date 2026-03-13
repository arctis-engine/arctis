from typing import Tuple

from .diff import SymbolDiff


class StructureChecks:
    """
    Führt Strukturprüfungen durch.
    """

    def validate(self, diff: SymbolDiff) -> Tuple[bool, str]:
        if diff.removed:
            return False, f"StructureChecks: removed symbols not allowed: {diff.removed}"

        if diff.changed:
            return False, f"StructureChecks: changed symbols not allowed: {diff.changed}"

        return True, "StructureChecks: structure is valid."
