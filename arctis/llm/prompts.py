class PromptBuilder:
    """
    Universeller Prompt-Builder für Arctis.
    - Enterprise-fähig, aber minimal
    - v1-kompatibel (code_generation bleibt erhalten)
    - v2-ready (build(task_type, ...) als zentrale API)
    """

    @staticmethod
    def build(task_type: str, instruction: str, metadata: dict, old_source: str | None = None) -> str:
        task_type = (task_type or "generate").lower()

        if task_type in ("generate", "create", "add"):
            return PromptBuilder._generate_prompt(instruction)

        if task_type in ("refactor", "rewrite"):
            return PromptBuilder._refactor_prompt(instruction, old_source)

        if task_type in ("bugfix", "fix", "patch"):
            return PromptBuilder._bugfix_prompt(instruction, old_source)

        if task_type in ("test", "tests", "unit_test"):
            return PromptBuilder._test_prompt(instruction, old_source)

        if task_type in ("explain", "analyze", "analysis"):
            return PromptBuilder._explain_prompt(instruction, old_source)

        return PromptBuilder._generate_prompt(instruction)

    @staticmethod
    def code_generation(description: str, metadata: dict) -> str:
        return PromptBuilder._generate_prompt(description)

    @staticmethod
    def _generate_prompt(instruction: str) -> str:
        return (
            "You are Arctis, an architecture-aware code generator.\n"
            "Generate ONLY the Python code that must be appended to the file.\n"
            "Do NOT repeat existing code.\n"
            "Do NOT explain anything.\n"
            "Output ONLY valid Python code.\n\n"
            f"Task:\n{instruction}\n"
        )

    @staticmethod
    def _refactor_prompt(instruction: str, old_source: str | None) -> str:
        return (
            "You are Arctis, an architecture-aware refactoring engine.\n"
            "Rewrite ONLY the necessary parts of the code.\n"
            "Preserve behavior unless explicitly instructed.\n"
            "Output ONLY the full, refactored Python code.\n\n"
            f"Instruction:\n{instruction}\n\n"
            "Existing code:\n"
            "```python\n"
            f"{old_source or ''}\n"
            "```\n"
        )

    @staticmethod
    def _bugfix_prompt(instruction: str, old_source: str | None) -> str:
        return (
            "You are Arctis, an architecture-aware bug fixing engine.\n"
            "Fix ONLY the minimal required parts of the code.\n"
            "Preserve all unrelated behavior.\n"
            "Output ONLY the full, corrected Python code.\n\n"
            f"Bug description:\n{instruction}\n\n"
            "Existing code:\n"
            "```python\n"
            f"{old_source or ''}\n"
            "```\n"
        )

    @staticmethod
    def _test_prompt(instruction: str, old_source: str | None) -> str:
        return (
            "You are Arctis, an architecture-aware test generator.\n"
            "Generate ONLY Python unit tests (pytest style).\n"
            "Do NOT modify the original code.\n"
            "Output ONLY valid Python test code.\n\n"
            f"Behavior:\n{instruction}\n\n"
            "Relevant code:\n"
            "```python\n"
            f"{old_source or ''}\n"
            "```\n"
        )

    @staticmethod
    def _explain_prompt(instruction: str, old_source: str | None) -> str:
        return (
            "You are Arctis, an architecture-aware code explainer.\n"
            "Explain the architecture, structure, and behavior of the code.\n"
            "Output ONLY an explanation in natural language.\n\n"
            f"Instruction:\n{instruction}\n\n"
            "Code:\n"
            "```python\n"
            f"{old_source or ''}\n"
            "```\n"
        )
