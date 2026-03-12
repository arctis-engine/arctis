# Datei: core/validators/__init__.py

class BaseValidator:
    name: str
    severity: str = "error"

    def run(self, task, spec, code: str) -> dict:
        raise NotImplementedError