import ast
from typing import Any


class ASTParser:
    """
    Parst Python-Quelltext in einen AST-Baum.
    """

    def parse(self, source: str) -> Any:
        try:
            return ast.parse(source)
        except SyntaxError as e:
            raise Exception(f"ASTParser: Syntax error in source: {e}") from e
