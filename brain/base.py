# Datei: brain/base.py

from __future__ import annotations
from typing import Dict, Any

from core.models import Task, Subtask
from core.plugins.registry import Plugin, PluginResult


class BrainPlugin(Plugin):
    """
    Erweiterte Plugin-Basis für Brain-spezifische Logik.
    """

    def create_subtask(
        self,
        parent: Task,
        name: str,
        type: str,
        target_file: str,
        meta: Dict[str, Any] | None = None,
    ) -> Subtask:
        return Subtask(
            parent_task_id=parent.id,
            name=name,
            type=type,
            target_file=target_file,
            meta=meta or {},
        )
