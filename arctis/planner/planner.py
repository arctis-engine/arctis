from typing import List
from .micro_task import MicroTask
from arctis.context.context_models import RepoContext


class TaskPlanner:

    def __init__(self, ctx: RepoContext):
        self.ctx = ctx

    def plan(self, instruction: str) -> List[MicroTask]:
        """
        High-level instruction → list of MicroTasks.
        Flask-aware, architecture-aware.
        """

        instruction_lower = instruction.lower()
        tasks: List[MicroTask] = []

        # --- 1. Neue Route hinzufügen ---------------------------------------
        if "route" in instruction_lower or "endpoint" in instruction_lower:
            tasks += self._plan_route_tasks(instruction)

        # --- 2. Service hinzufügen ------------------------------------------
        if "service" in instruction_lower:
            tasks += self._plan_service_tasks(instruction)

        # --- 3. Model hinzufügen --------------------------------------------
        if "model" in instruction_lower:
            tasks += self._plan_model_tasks(instruction)

        # Sort by priority
        return sorted(tasks, key=lambda t: t.priority)

    # -------------------------------------------------------------------------
    # Route Tasks
    # -------------------------------------------------------------------------
    def _plan_route_tasks(self, instruction: str) -> List[MicroTask]:
        tasks: List[MicroTask] = []

        # 1. Route-Datei finden
        route_files = [f for f, layer in self.ctx.layers.items() if layer == "routes"]
        file_path = route_files[0] if route_files else "routes.py"

        # 2. Route generieren
        tasks.append(
            MicroTask(
                file_path=file_path,
                instruction=f"generate flask route: {instruction}",
                priority=1,
                mode="append",
            )
        )

        # 3. Service erzeugen, falls nötig
        if not self._has_service_for_instruction(instruction):
            service_file = self._default_service_file()
            tasks.append(
                MicroTask(
                    file_path=service_file,
                    instruction=f"generate service for route: {instruction}",
                    priority=2,
                    mode="append",
                )
            )

        # 4. Test erzeugen
        test_file = self._default_test_file()
        tasks.append(
            MicroTask(
                file_path=test_file,
                instruction=f"generate test for route: {instruction}",
                priority=5,
                mode="append",
            )
        )

        return tasks

    # -------------------------------------------------------------------------
    # Service Tasks
    # -------------------------------------------------------------------------
    def _plan_service_tasks(self, instruction: str) -> List[MicroTask]:
        service_file = self._default_service_file()

        return [
            MicroTask(
                file_path=service_file,
                instruction=f"generate service: {instruction}",
                priority=1,
                mode="append",
            )
        ]

    # -------------------------------------------------------------------------
    # Model Tasks
    # -------------------------------------------------------------------------
    def _plan_model_tasks(self, instruction: str) -> List[MicroTask]:
        model_file = self._default_model_file()

        return [
            MicroTask(
                file_path=model_file,
                instruction=f"generate model: {instruction}",
                priority=1,
                mode="append",
            )
        ]

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    def _default_service_file(self) -> str:
        service_files = [f for f, l in self.ctx.layers.items() if l == "services"]
        return service_files[0] if service_files else "services.py"

    def _default_model_file(self) -> str:
        model_files = [f for f, l in self.ctx.layers.items() if l == "models"]
        return model_files[0] if model_files else "models.py"

    def _default_test_file(self) -> str:
        test_files = [f for f, l in self.ctx.layers.items() if l == "tests"]
        return test_files[0] if test_files else "tests/test_routes.py"

    def _has_service_for_instruction(self, instruction: str) -> bool:
        """
        Very simple heuristic:
        If instruction mentions a service name that already exists.
        """
        for file, services in self.ctx.services.items():
            for s in services:
                if s.class_name and s.class_name.lower() in instruction.lower():
                    return True
                if s.function_name.lower() in instruction.lower():
                    return True
        return False
