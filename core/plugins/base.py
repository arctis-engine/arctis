from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from core.models import Subtask, Task
from core.failures import FailureMode


class Plugin(ABC):
    """
    Base class for all Arctic Brain v3 plugins.

    Responsibilities:
    - decide whether it can handle a Task (v3 Task model)
    - generate one or more Subtasks (v3 Subtask model)
    - define validator profiles
    - define patch modes
    - define context modes

    Guarantees:
    - Plugins NEVER return raw dicts
    - Plugins ALWAYS return Subtask objects
    - Plugins NEVER crash (errors → FailureMode.PLUGIN_RUNTIME_ERROR)
    """

    # ============================================================
    # 1. Plugin Identification
    # ============================================================

    @abstractmethod
    def can_handle(self, task: Task) -> bool:
        """
        Returns True if this plugin can handle the given v3 Task.
        """
        raise NotImplementedError

    # ============================================================
    # 2. Subtask Generation (v3)
    # ============================================================

    @abstractmethod
    def execute(self, task: Task, specs: Dict, ctx: Dict) -> List[Subtask]:
        """
        Returns a list of v3 Subtask objects.

        A Subtask MUST contain:
            - parent_task_id
            - name
            - type
            - target_file
            - meta (optional)

        Plugins MUST NOT return raw dicts.
        """
        raise NotImplementedError

    # ============================================================
    # 3. Validator Profile (v3)
    # ============================================================

    def get_validator_profile(self, task: Task) -> str:
        """
        Returns the validator profile for this task.
        Default: 'syntax_only'
        """
        return task.meta.get("validator_profile", "syntax_only")

    # ============================================================
    # 4. Patch Mode (v3)
    # ============================================================

    def get_patch_mode(self, task: Task) -> str:
        """
        Returns the patch mode for this task.
        Default: 'function'
        Options:
            - function
            - file
            - class_method
            - insert
            - delete
        """
        return task.meta.get("patch_mode", "function")

    # ============================================================
    # 5. Context Mode (v3)
    # ============================================================

    def get_context_mode(self, task: Task) -> str:
        """
        Returns the context mode for this task.
        Default: 'snippets'
        Options:
            - snippets
            - module
            - file
        """
        return task.meta.get("context_mode", "snippets")

    # ============================================================
    # 6. Helper: Build a v3 Subtask
    # ============================================================

    def build_subtask(
        self,
        base_task: Task,
        *,
        name: str,
        type: str,
        target_file: str,
        meta: Optional[Dict] = None,
    ) -> Subtask:
        """
        Helper to create a well-formed v3 Subtask.
        """
        return Subtask(
            parent_task_id=base_task.id,
            name=name,
            type=type,
            target_file=target_file,
            meta=meta or {},
        )

    # ============================================================
    # 7. Safe Execution Wrapper (v3)
    # ============================================================

    def safe_execute(self, task: Task, specs: Dict, ctx: Dict):
        """
        Wraps execute() to ensure plugins never crash.
        Returns:
            - (subtasks, None) on success
            - (None, FailureMode.PLUGIN_RUNTIME_ERROR) on crash
        """
        try:
            subtasks = self.execute(task, specs, ctx)

            # Validate return type
            if not isinstance(subtasks, list) or not all(isinstance(s, Subtask) for s in subtasks):
                return None, FailureMode.PLUGIN_INVALID_SUBTASK

            return subtasks, None

        except Exception:
            return None, FailureMode.PLUGIN_RUNTIME_ERROR
