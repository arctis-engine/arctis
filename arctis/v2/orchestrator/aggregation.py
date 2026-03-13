from typing import List, Any, Optional

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


class PatchAggregator:
    """
    Aggregiert und validiert Patches aus mehreren Dateien.
    """

    def __init__(self):
        self.spec_evaluator = RuleEvaluator()
        self.ast_parser = ASTParser()
        self.symbol_builder = SymbolTableBuilder()
        self.symbol_differ = SymbolDiffer()
        self.structure_checks = StructureChecks()
        self.patch_sanitizer = PatchSanitizer()
        self.enforcement = Enforcement()

    def aggregate(self, patches: List[Any]) -> Optional[List[Any]]:
        """
        Validiert alle Patches gemeinsam.
        Gibt eine Liste finaler Patches zurück oder None.
        """

        final_patches = []

        for patch in patches:
            if patch is None:
                return None

            # 1. AST + Symboltables
            old_ast = self.ast_parser.parse(patch.old_source)
            new_ast = self.ast_parser.parse(patch.new_source)

            symbols_before = self.symbol_builder.build(old_ast)
            symbols_after = self.symbol_builder.build(new_ast)

            diff = self.symbol_differ.diff(
                symbols_before.functions | symbols_before.classes,
                symbols_after.functions | symbols_after.classes,
            )

            structure_ok, _ = self.structure_checks.validate(diff)

            # 2. Spec-Engine
            context = SpecContext(
                file_path=patch.file_path,
                patch=patch,
                old_source=patch.old_source,
                new_source=patch.new_source,
                symbols_before=symbols_before.functions | symbols_before.classes,
                symbols_after=symbols_after.functions | symbols_after.classes,
                metadata={"patch_mode": patch.mode},
            )

            spec_result = self.spec_evaluator.evaluate(default_ruleset(), context)
            spec_ok = spec_result.ok

            # 3. Sanitizer
            sanitized_patch = self.patch_sanitizer.sanitize(patch)

            # 4. Enforcement
            final_patch = self.enforcement.enforce(
                patch=patch,
                spec_ok=spec_ok,
                structure_ok=structure_ok,
                sanitized_patch=sanitized_patch,
            )

            if final_patch is None:
                return None

            final_patches.append(final_patch)

        return final_patches
