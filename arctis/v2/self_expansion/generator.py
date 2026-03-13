from arctis.llm.prompts import PromptBuilder
from arctis.v2.sanitizer import ResponseSanitizer

class ExpansionGenerator:
    def __init__(self, llm_callable):
        self.llm = llm_callable
        self.response_sanitizer = ResponseSanitizer()

    def generate(self, blueprint) -> str:
        prompt = PromptBuilder.code_generation(
            blueprint.description,
            blueprint.metadata
        )
        raw = self.llm(prompt)
        return self.response_sanitizer.sanitize(raw)
