from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class SymbolDiff:
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)


class SymbolDiffer:
    """
    Vergleicht zwei Symboltabellen.
    """

    def diff(self, before: Dict[str, Any], after: Dict[str, Any]) -> SymbolDiff:
        before_keys = set(before.keys())
        after_keys = set(after.keys())

        added = sorted(list(after_keys - before_keys))
        removed = sorted(list(before_keys - after_keys))

        changed = []
        for key in before_keys & after_keys:
            if type(before[key]) != type(after[key]):
                changed.append(key)

        return SymbolDiff(added=added, removed=removed, changed=changed)
