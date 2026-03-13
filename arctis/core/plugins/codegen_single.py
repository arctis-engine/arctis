# Datei: core/plugins/codegen_single.py

from core.plugins.base import Plugin


class CodegenSinglePlugin(Plugin):
    """
    Deterministisches Codegen-Plugin für Tests.
    Überspringt den LLM und schreibt direkt Code.
    """

    def can_handle(self, task):
        return task.get("type") == "codegen.single"

    def execute(self, task, spec, ctx):
        target = task["target_file"]

        code = (
            "def generated_function():\n"
            "    return 'OK'\n"
        )

        # Datei direkt schreiben
        with open(target, "w", encoding="utf-8") as f:
            f.write(code)

        # Orchestrator soll NICHT den LLM aufrufen
        return []
