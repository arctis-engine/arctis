import ast
from typing import Dict, List

from .context_models import RepoContext
from .repo_scanner import RepoScanner
from .layer_detector import detect_layer
from .architecture_rules import DEFAULT_RULES

from arctis.ast import (
    parse_code,
    extract_routes_from_ast,
    extract_services_from_ast,
    extract_models_from_ast,
)


class RepoContextEngine:

    def __init__(self, root: str):
        self.root = root
        self.scanner = RepoScanner()

    def build(self) -> RepoContext:
        files, functions, classes, imports = self.scanner.scan(self.root)

        layers = {f: detect_layer(f) for f in files}

        ctx = RepoContext(
            files=files,
            functions=functions,
            classes=classes,
            imports=imports,
            layers=layers,
            rules=DEFAULT_RULES,
        )

        # IR-Extraktion pro Datei
        ctx.routes = {}
        ctx.services = {}
        ctx.models = {}

        for file_path in files:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

            try:
                tree = parse_code(code)
            except SyntaxError:
                continue

            ctx.routes[file_path] = extract_routes_from_ast(tree, file_path)
            ctx.services[file_path] = extract_services_from_ast(tree, file_path)
            ctx.models[file_path] = extract_models_from_ast(tree, file_path)

        return ctx
