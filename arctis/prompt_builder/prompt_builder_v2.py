from arctis.prompt_builder.prompt_builder import PromptBuilder as BasePromptBuilder
from arctis.planner.micro_task import MicroTask
from arctis.context.context_models import RepoContext


class PromptBuilderV2(BasePromptBuilder):
    """
    Erweiterter PromptBuilder:
    - nutzt RepoContext
    - nutzt IR (routes, services, models)
    - nutzt Layer-Informationen
    - bleibt kompatibel zur BasePromptBuilder API
    """

    def __init__(self, ctx: RepoContext):
        self.ctx = ctx

    def build_for_task(self, task: MicroTask) -> str:
        """
        Architektur-aware Prompt-Erzeugung für MicroTasks.
        """
        layer = self.ctx.layers.get(task.file_path, "unknown")

        routes = self.ctx.routes.get(task.file_path, [])
        services = self.ctx.services.get(task.file_path, [])
        models = self.ctx.models.get(task.file_path, [])

        existing_functions = self.ctx.functions.get(task.file_path, [])

        architecture_rules = self._format_rules(self.ctx.rules)

        return f"""
You are Arctis, an architecture-aware code generator for Flask projects.

File: {task.file_path}
Layer: {layer}
Mode: {task.mode}

Instruction:
{task.instruction}

Existing functions:
{existing_functions}

Existing routes:
{[(r.function_name, r.http_method, r.path) for r in routes]}

Existing services:
{[(s.class_name, s.function_name) for s in services]}

Existing models:
{[(m.class_name, m.fields) for m in models]}

Architecture rules:
{architecture_rules}

Constraints:
- Output ONLY valid Python code
- Do NOT modify other files
- Do NOT repeat existing code
- No explanations, no comments, no markdown
"""

    # -------------------------------------------------------------------------
    # Helper
    # -------------------------------------------------------------------------
    def _format_rules(self, rules: dict) -> str:
        return "\n".join([f"- {layer} may import: {allowed}" for layer, allowed in rules.items()])
