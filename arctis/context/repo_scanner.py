import os
import ast


class RepoScanner:

    def scan(self, root: str):
        files, functions, classes, imports = [], {}, {}, {}

        for dirpath, _, filenames in os.walk(root):
            for name in filenames:
                if not name.endswith(".py"):
                    continue

                path = os.path.join(dirpath, name)
                files.append(path)

                with open(path, "r", encoding="utf-8") as f:
                    code = f.read()

                tree = ast.parse(code)

                functions[path] = []
                classes[path] = []
                imports[path] = []

                for node in ast.walk(tree):

                    if isinstance(node, ast.FunctionDef):
                        functions[path].append(node.name)

                    if isinstance(node, ast.ClassDef):
                        classes[path].append(node.name)

                    if isinstance(node, ast.Import):
                        imports[path] += [n.name for n in node.names]

                    if isinstance(node, ast.ImportFrom) and node.module:
                        imports[path].append(node.module)

        return files, functions, classes, imports
