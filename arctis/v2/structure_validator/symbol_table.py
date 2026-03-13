import ast
from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class SymbolTable:
    classes: Dict[str, Any] = field(default_factory=dict)
    functions: Dict[str, Any] = field(default_factory=dict)
    imports: List[str] = field(default_factory=list)


class SymbolTableBuilder:
    """
    Baut eine SymbolTable aus einem AST-Baum.
    """

    def build(self, tree: ast.AST) -> SymbolTable:
        table = SymbolTable()

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                table.classes[node.name] = node

            elif isinstance(node, ast.FunctionDef):
                table.functions[node.name] = node

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    table.imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    table.imports.append(f"{module}.{alias.name}")

        return table
