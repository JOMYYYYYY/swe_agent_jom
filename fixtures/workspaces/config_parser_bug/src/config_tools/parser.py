def parse_port(value: str) -> int:
    port = int(value)

    if port <= 0:
        raise ValueError("Port must be positive.")

    return port


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()

    if normalized in {"true", "yes", "1"}:
        return True

    if normalized in {"false", "no", "0"}:
        return True

    raise ValueError(f"Invalid boolean value: {value}")

