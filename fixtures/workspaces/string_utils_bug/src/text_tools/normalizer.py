def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def normalize_slug(text: str) -> str:
    normalized = normalize_whitespace(text).lower()
    return normalized.replace(" ", "_")

