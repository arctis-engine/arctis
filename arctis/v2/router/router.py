from typing import Dict

from .classifier import TaskClassifier
from .routing_table import ROUTING_TABLE


class Router:
    """
    Entscheidet, welche Engine ausgeführt wird.
    """

    def __init__(self):
        self.classifier = TaskClassifier()

    def route(self, task: Dict) -> str:
        task_type = self.classifier.classify(task)

        if task_type not in ROUTING_TABLE:
            raise Exception(f"Router: unknown task type '{task_type}'")

        return ROUTING_TABLE[task_type]
