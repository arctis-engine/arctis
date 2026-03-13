import ast
from typing import Iterable, List

from arctis.ir import RouteIR, ServiceIR, ModelIR


def _get_decorator_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[str]:
    names: List[str] = []
    for dec in node.decorator_list:
        try:
            names.append(ast.unparse(dec))
        except Exception:
            # Fallback: best-effort repr
            names.append(getattr(dec, "id", repr(dec)))
    return names


def _guess_http_method_from_decorators(decorators: Iterable[str]) -> str | None:
    """
    Try to infer HTTP method from Flask-style decorators.
    Examples:
      @bp.route("/users", methods=["GET"])
      @app.get("/users")
    """
    for dec in decorators:
        lower = dec.lower()
        if ".get(" in lower or "methods=['get'" in lower or "methods=[\"get\"" in lower:
            return "GET"
        if ".post(" in lower or "methods=['post'" in lower or "methods=[\"post\"" in lower:
            return "POST"
        if ".put(" in lower or "methods=['put'" in lower or "methods=[\"put\"" in lower:
            return "PUT"
        if ".delete(" in lower or "methods=['delete'" in lower or "methods=[\"delete\"" in lower:
            return "DELETE"
    return None


def _guess_path_from_decorators(decorators: Iterable[str]) -> str | None:
    """
    Very simple heuristic: look for route("...") or .route("...").
    """
    for dec in decorators:
        if "route(" in dec:
            # naive: take first quoted string
            if '"' in dec:
                start = dec.find('"')
                end = dec.find('"', start + 1)
                if start != -1 and end != -1:
                    return dec[start + 1 : end]
            if "'" in dec:
                start = dec.find("'")
                end = dec.find("'", start + 1)
                if start != -1 and end != -1:
                    return dec[start + 1 : end]
    return None


def extract_routes_from_ast(tree: ast.AST, file_path: str) -> list[RouteIR]:
    routes: list[RouteIR] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorators = _get_decorator_names(node)
            if not any("route(" in d or ".get(" in d or ".post(" in d for d in decorators):
                continue

            http_method = _guess_http_method_from_decorators(decorators) or "GET"
            path = _guess_path_from_decorators(decorators) or "/"

            routes.append(
                RouteIR(
                    file_path=file_path,
                    layer="routes",
                    function_name=node.name,
                    http_method=http_method,
                    path=path,
                    decorators=decorators,
                    uses_service=None,
                    returns_type=None,
                )
            )

    return routes


def extract_services_from_ast(tree: ast.AST, file_path: str) -> list[ServiceIR]:
    services: list[ServiceIR] = []

    for node in ast.walk(tree):
        # class-based services
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            for body_item in node.body:
                if isinstance(body_item, ast.FunctionDef):
                    params = [arg.arg for arg in body_item.args.args if arg.arg != "self"]
                    services.append(
                        ServiceIR(
                            file_path=file_path,
                            layer="services",
                            class_name=class_name,
                            function_name=body_item.name,
                            params=params,
                            returns_type=None,
                            uses_model=None,
                        )
                    )
        # module-level service functions
        if isinstance(node, ast.FunctionDef):
            params = [arg.arg for arg in node.args.args]
            services.append(
                ServiceIR(
                    file_path=file_path,
                    layer="services",
                    class_name=None,
                    function_name=node.name,
                    params=params,
                    returns_type=None,
                    uses_model=None,
                )
            )

    return services


def extract_models_from_ast(tree: ast.AST, file_path: str) -> list[ModelIR]:
    models: list[ModelIR] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            fields: list[str] = []
            for body_item in node.body:
                if isinstance(body_item, ast.Assign):
                    for target in body_item.targets:
                        if isinstance(target, ast.Name):
                            fields.append(target.id)
            models.append(
                ModelIR(
                    file_path=file_path,
                    layer="models",
                    class_name=node.name,
                    fields=fields,
                )
            )

    return models
