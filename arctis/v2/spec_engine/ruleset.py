from typing import List, Tuple

from .context import SpecContext
from .rules import Rule


class RuleSet:
    """
    Ein RuleSet ist eine Sammlung von Regeln, die gemeinsam gelten.
    """

    def __init__(self, rules: List[Rule] | None = None, name: str | None = None):
        self.rules: List[Rule] = rules or []
        self.name = name or "unnamed_ruleset"

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)

    def evaluate(self, context: SpecContext) -> List[Tuple[bool, str, Rule]]:
        results: List[Tuple[bool, str, Rule]] = []
        for rule in self.rules:
            ok, reason = rule.evaluate(context)
            results.append((ok, reason, rule))
        return results

    def __repr__(self) -> str:
        return f"<RuleSet name={self.name!r} rules={len(self.rules)}>"
