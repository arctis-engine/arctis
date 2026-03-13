# arctis/micro_pipeline.py

from dataclasses import dataclass
from typing import Any, Dict


# -----------------------------
# Datentypen
# -----------------------------

@dataclass
class MicroTask:
    file_path: str
    instruction: str
    mode: str  # "generate", "refactor", "bugfix", "test", "explain"
    old_source: str | None = None
    metadata: Dict[str, Any] | None = None


@dataclass
class MicroResult:
    file_path: str
    mode: str
    new_source: str


# -----------------------------
# Micro-Prompts (Iteration 4)
# -----------------------------

class MicroPrompts:
    @staticmethod
    def generate(instruction: str) -> str:
        return (
            "You are Arctis, an architecture-aware Python code generator.\n"
            "Your output will be inserted directly into an existing codebase.\n"
            "Generate a self-contained Python snippet that fits naturally into typical Python project structure.\n"
            "Follow these rules strictly:\n"
            "1. Output ONLY valid Python code.\n"
            "2. Output MUST NOT be empty.\n"
            "3. Output ONLY the code that must be added.\n"
            "4. Do NOT repeat or modify existing code.\n"
            "5. Do NOT include imports unless explicitly required.\n"
            "6. Do NOT include comments unless explicitly required.\n"
            "7. Do NOT include explanations, markdown, or surrounding text.\n"
            "8. Do NOT wrap the code in quotes or backticks.\n"
            "9. The snippet MUST be syntactically complete and self-contained.\n"
            "10. Prefer simple, conventional Python structure (functions, small helpers).\n\n"
            "Instruction:\n"
            f"{instruction}\n\n"
            "Output ONLY the Python code snippet."
        )

    @staticmethod
    def refactor(instruction: str, old_source: str | None) -> str:
        return (
            "You are Arctis, an architecture-aware Python refactoring engine.\n"
            "Rewrite the provided code according to the instruction.\n"
            "Follow these rules strictly:\n"
            "1. Output ONLY the full, refactored Python code.\n"
            "2. Do NOT include explanations, comments, or markdown.\n"
            "3. Preserve behavior unless the instruction requires changes.\n"
            "4. Keep the structure clear, conventional, and minimal.\n"
            "5. The output MUST be valid Python code.\n\n"
            "Instruction:\n"
            f"{instruction}\n\n"
            "Existing code:\n"
            f"{old_source or ''}\n\n"
            "Output ONLY the full refactored Python code."
        )

    @staticmethod
    def bugfix(instruction: str, old_source: str | None) -> str:
        return (
            "You are Arctis, an architecture-aware Python bug fixing engine.\n"
            "Fix the described issue by modifying ONLY the necessary parts of the code.\n"
            "Follow these rules strictly:\n"
            "1. Output ONLY the full corrected Python code.\n"
            "2. Do NOT include explanations, comments, or markdown.\n"
            "3. Preserve all unrelated behavior.\n"
            "4. Keep the fix minimal and conventional.\n"
            "5. The output MUST be valid Python code.\n\n"
            "Bug description:\n"
            f"{instruction}\n\n"
            "Existing code:\n"
            f"{old_source or ''}\n\n"
            "Output ONLY the full corrected Python code."
        )

    @staticmethod
    def test(instruction: str, old_source: str | None) -> str:
        return (
            "You are Arctis, an architecture-aware Python test generator.\n"
            "Generate pytest-style unit tests for the described behavior.\n"
            "Follow these rules strictly:\n"
            "1. Output ONLY valid Python test code.\n"
            "2. Do NOT include explanations, comments, or markdown.\n"
            "3. Do NOT modify the original code.\n"
            "4. Keep the tests simple, direct, and conventional.\n\n"
            "Behavior:\n"
            f"{instruction}\n\n"
            "Relevant code:\n"
            f"{old_source or ''}\n\n"
            "Output ONLY the Python test code."
        )

    @staticmethod
    def explain(instruction: str, old_source: str | None) -> str:
        return (
            "You are Arctis, an architecture-aware code explainer.\n"
            "Explain the structure and behavior of the provided code.\n"
            "Follow these rules strictly:\n"
            "1. Output ONLY a clear natural-language explanation.\n"
            "2. Do NOT output code.\n"
            "3. Do NOT include markdown or formatting.\n"
            "4. Keep the explanation concise and architecture-focused.\n\n"
            "Instruction:\n"
            f"{instruction}\n\n"
            "Code:\n"
            f"{old_source or ''}\n\n"
            "Output ONLY the explanation."
        )


# -----------------------------
# Micro-Monolith Pipeline
# -----------------------------

def _build_prompt(task: MicroTask) -> str:
    mode = (task.mode or "generate").lower()

    if mode in ("generate", "create", "add"):
        return MicroPrompts.generate(task.instruction)

    if mode in ("refactor", "rewrite"):
        return MicroPrompts.refactor(task.instruction, task.old_source)

    if mode in ("bugfix", "fix", "patch"):
        return MicroPrompts.bugfix(task.instruction, task.old_source)

    if mode in ("test", "tests", "unit_test"):
        return MicroPrompts.test(task.instruction, task.old_source)

    if mode in ("explain", "analyze", "analysis"):
        return MicroPrompts.explain(task.instruction, task.old_source)

    return MicroPrompts.generate(task.instruction)


def _call_llm(prompt: str, llm_client) -> str:
    # Erwartet einen bestehenden LLM-Client mit .generate(prompt: str) -> str
    return llm_client.generate(prompt)


def run_micro_pipeline(task: MicroTask, llm_client) -> MicroResult:
    """
    Kleiner, deterministischer Micro-Monolith:
    - baut Prompt
    - ruft LLM
    - gibt neues Source-Snippet oder Vollcode zurück
    """
    prompt = _build_prompt(task)
    output = _call_llm(prompt, llm_client)

    return MicroResult(
        file_path=task.file_path,
        mode=task.mode,
        new_source=output.strip(),
    )
