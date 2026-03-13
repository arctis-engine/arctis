from typing import List, Any

from .subtask import Subtask


class MultiFileExecutor:
    """
    Führt Subtasks über die v1-Pipeline aus.
    """

    def __init__(self, v1_pipeline_callable):
        """
        v1_pipeline_callable: Funktion, die einen Single-File-Patch erzeugt.
        """
        self.v1_pipeline = v1_pipeline_callable

    def execute(self, subtasks: List[Subtask]) -> List[Any]:
        patches = []

        for subtask in subtasks:
            patch = self.v1_pipeline(
                file_path=subtask.file_path,
                instruction=subtask.instruction,
                metadata=subtask.metadata,
            )
            patches.append(patch)

        return patches
