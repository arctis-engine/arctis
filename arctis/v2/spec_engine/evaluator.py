from dataclasses import dataclass
from typing import List

from .context import SpecContext
from .errors import RuleViolation
from .rules import Rule
from .ruleset import RuleSet


@dataclass(frozen=True)
class EvaluationResult:
    """
    Ergebnis der Auswertung eines RuleSets.
    """
    ok: bool
    violations: List[RuleViolation]

    def raise_if_failed(self) -> None:
        if not self.ok and self.violations:
            messages = "; ".join(str(v) for v in self.violations)
            raise Exception(f"SpecEngine rule violations: {messages}")


class RuleEvaluator:
    """
    Führt ein RuleSet gegen einen Kontext aus und entscheidet final.
    """

    def evaluate(self, ruleset: RuleSet, context: SpecContext) -> EvaluationResult:
        raw_results = ruleset.evaluate(context)
        violations: List[RuleViolation] = []

        for ok, reason, rule in raw_results:
            if not ok:
                violations.append(
                    RuleViolation(
                        rule_type=type(rule),
                        message=reason,
                        file_path=context.file_path,
                        rule_name=ruleset.name,
                    )
                )

        return EvaluationResult(ok=(len(violations) == 0), violations=violations)
