from typing import List, Dict, Any

from .subtask import Subtask


class MultiFilePlanner:
    """
    Plant Multi-File-Tasks und erzeugt Subtasks.
    """

    def plan(self, task: Dict[str, Any]) -> List[Subtask]:
        """
        Erwartet:
        {
            "files": ["a.py", "b.py"],
            "instructions": {
                "a.py": "...",
                "b.py": "..."
            },
            "metadata": {...}
        }
        """
        files = task.get("files", [])
        instructions = task.get("instructions", {})
        metadata = task.get("metadata", {})

        subtasks = []

        for file_path in files:
            instruction = instructions.get(file_path)
            if not instruction:
                raise Exception(f"Planner: missing instruction for file '{file_path}'")

            subtasks.append(
                Subtask(
                    file_path=file_path,
                    instruction=instruction,
                    metadata=metadata,
                )
            )

        return subtasks
