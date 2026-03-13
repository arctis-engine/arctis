from typing import Optional

from arctis.v2.spec_engine import (
    SpecContext,
    RuleEvaluator,
    default_ruleset,
)
from arctis.v2.structure_validator import (
    ASTParser,
    SymbolTableBuilder,
    SymbolDiffer,
    StructureChecks,
)
from arctis.v2.sanitizer import (
    PatchSanitizer,
    Enforcement,
)


class ExpansionIntegrator:
    """
    Integriert generierten Code in das Arctis-System.
    """

    def __init__(self):
        self.spec_evaluator = RuleEvaluator()
        self.ast_parser = ASTParser()
        self.symbol_builder = SymbolTableBuilder()
        self.symbol_differ = SymbolDiffer()
        self.structure_checks = StructureChecks()
        self.patch_sanitizer = PatchSanitizer()
        self.enforcement = Enforcement()

    def integrate(self, blueprint, old_source: str, new_source: str) -> Optional[str]:
        """
        Validiert und integriert neuen Code.
        Gibt finalen Code zurück oder None.
        """

        old_ast = self.ast_parser.parse(old_source)
        new_ast = self.ast_parser.parse(new_source)

        symbols_before = self.symbol_builder.build(old_ast)
        symbols_after = self.symbol_builder.build(new_ast)

        diff = self.symbol_differ.diff(
            symbols_before.functions | symbols_before.classes,
            symbols_after.functions | symbols_after.classes,
        )

        structure_ok, _ = self.structure_checks.validate(diff)

        context = SpecContext(
            file_path=blueprint.target_path,
            patch=None,
            old_source=old_source,
            new_source=new_source,
            symbols_before=symbols_before.functions | symbols_before.classes,
            symbols_after=symbols_after.functions | symbols_after.classes,
            metadata={"patch_mode": "rewrite"},
        )

        spec_result = self.spec_evaluator.evaluate(default_ruleset(), context)
        spec_ok = spec_result.ok

        sanitized = self.patch_sanitizer.sanitize(
            type("Patch", (), {"content": new_source, "mode": "rewrite"})
        )
        if sanitized is None:
            return None

        final = self.enforcement.enforce(
            patch=new_source,
            spec_ok=spec_ok,
            structure_ok=structure_ok,
            sanitized_patch=new_source,
        )

        return final
