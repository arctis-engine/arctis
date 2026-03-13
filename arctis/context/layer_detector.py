def detect_layer(path: str) -> str:
    p = path.lower()

    if "route" in p or "controller" in p:
        return "routes"

    if "service" in p:
        return "services"

    if "model" in p:
        return "models"

    if "test" in p:
        return "tests"

    return "unknown"
