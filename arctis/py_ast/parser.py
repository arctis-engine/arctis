import ast
from typing import Any


def parse_code(source: str) -> ast.AST:
    """
    Parse Python source code into an AST.

    Raises SyntaxError if the code is invalid.
    """
    return ast.parse(source)


def safe_parse_code(source: str) -> tuple[ast.AST | None, list[str]]:
    """
    Parse code and return (tree, errors).
    If parsing fails, tree is None and errors contains a message.
    """
    try:
        tree = ast.parse(source)
        return tree, []
    except SyntaxError as exc:
        msg = f"SyntaxError: {exc.msg} at line {exc.lineno}, col {exc.offset}"
        return None, [msg]
