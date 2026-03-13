import re


class ResponseSanitizer:
    """
    Säubert rohen LLM-Output, bevor er in einen Patch umgewandelt wird.
    """

    def sanitize(self, llm_output: str) -> str:
        if not isinstance(llm_output, str):
            return ""

        cleaned = llm_output.strip()

        forbidden = [
            r"import\s+os",
            r"import\s+subprocess",
            r"eval\(",
            r"exec\(",
            r"open\(.+['\"]w['\"]\)",
        ]
        for pattern in forbidden:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        cleaned = re.sub(r"(?is)^```.*?```$", "", cleaned)
        cleaned = cleaned.replace("```python", "").replace("```", "")
        cleaned = cleaned.strip()

        return cleaned
