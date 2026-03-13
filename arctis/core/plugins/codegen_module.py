# Datei: core/plugins/codegen_module.py

from core.plugins.base import Plugin


class CodegenModulePlugin(Plugin):
    """
    v2-kompatibles Plugin für Modul-Codegenerierung.
    Erzeugt einen Subtask pro Datei:
        - patch_mode = "module"
        - validator_profile = "module"
        - context_mode = "module"
    """

    def can_handle(self, task: dict) -> bool:
        return task.get("type") == "codegen.module"

    def execute(self, task: dict, spec: dict, ctx: dict):
        files = task.get("files", {})
        subtasks = []

        for path, description in files.items():
            subtask = self.build_subtask(
                base_task=task,
                target_file=path,
                module=task.get("module"),
                patch_mode="module",            # AST-Patcher ersetzt das ganze Modul
                validator_profile="module",     # Syntax + Naming
                context_mode="module",          # Context Manager liefert Modul-Snippets
            )

            # Beschreibung übernehmen
            subtask["description"] = description

            subtasks.append(subtask)

        return subtasks
