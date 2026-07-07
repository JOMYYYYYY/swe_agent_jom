from __future__ import annotations

from pathlib import Path

from swe_agent_jom.config.settings import WORKSPACE_ROOT


class WorkspacePathError(ValueError):
    """Raised when a path escapes the configured workspace."""


def workspace_root() -> Path:
    return WORKSPACE_ROOT


def resolve_workspace_path(path: str | Path = ".") -> Path:
    candidate = Path(path)

    if not candidate.is_absolute():
        candidate = WORKSPACE_ROOT / candidate

    resolved = candidate.resolve(strict=False)

    if not _is_relative_to(resolved, WORKSPACE_ROOT):
        raise WorkspacePathError(
            f"Path escapes workspace: {path}. Workspace root is {WORKSPACE_ROOT}."
        )

    return resolved


def relative_to_workspace(path: str | Path) -> str:
    resolved = resolve_workspace_path(path)
    return resolved.relative_to(WORKSPACE_ROOT).as_posix()


def ensure_file(path: str | Path) -> Path:
    resolved = resolve_workspace_path(path)

    if not resolved.exists():
        raise FileNotFoundError(f"File does not exist: {relative_to_workspace(resolved)}")

    if not resolved.is_file():
        raise IsADirectoryError(f"Expected a file: {relative_to_workspace(resolved)}")

    return resolved


def ensure_directory(path: str | Path = ".") -> Path:
    resolved = resolve_workspace_path(path)

    if not resolved.exists():
        raise FileNotFoundError(
            f"Directory does not exist: {relative_to_workspace(resolved)}"
        )

    if not resolved.is_dir():
        raise NotADirectoryError(
            f"Expected a directory: {relative_to_workspace(resolved)}"
        )

    return resolved


def is_excluded_path(path: Path, excluded_dir_names: frozenset[str]) -> bool:
    try:
        relative_parts = path.resolve(strict=False).relative_to(WORKSPACE_ROOT).parts
    except ValueError:
        return True

    return any(part in excluded_dir_names for part in relative_parts)


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False

    return True
