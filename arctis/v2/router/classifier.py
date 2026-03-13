from typing import Dict


class TaskClassifier:
    """
    Klassifiziert Tasks in:
    - single_file
    - multi_file
    - self_expand
    """

    def classify(self, task: Dict) -> str:
        # Self-Expansion hat Vorrang
        if task.get("type") == "self_expand":
            return "self_expand"

        files = task.get("files", [])

        if not files:
            raise Exception("TaskClassifier: task contains no files.")

        if len(files) == 1:
            return "single_file"

        return "multi_file"
