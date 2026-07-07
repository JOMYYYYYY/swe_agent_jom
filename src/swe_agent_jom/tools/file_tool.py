from __future__ import annotations

from pathlib import Path

from swe_agent_jom.config.settings import (
    EXCLUDED_DIR_NAMES,
    MAX_LIST_FILES_RESULTS,
    MAX_READ_FILE_CHARS,
)
from swe_agent_jom.core.tool_result import ToolResult, error_result, success_result
from swe_agent_jom.runtime.workspace import (
    ensure_directory,
    ensure_file,
    is_excluded_path,
    relative_to_workspace,
    resolve_workspace_path,
)


def list_files(
    path: str = ".",
    pattern: str = "*",
    *,
    max_results: int = MAX_LIST_FILES_RESULTS,
) -> ToolResult:
    try:
        base = ensure_directory(path)
    except Exception as error:
        return error_result(
            type(error).__name__,
            str(error),
            details={"path": path},
        )

    entries: list[dict[str, object]] = []

    try:
        for candidate in sorted(base.rglob(pattern)):
            if is_excluded_path(candidate, EXCLUDED_DIR_NAMES):
                continue

            entries.append(
                {
                    "path": relative_to_workspace(candidate),
                    "type": "directory" if candidate.is_dir() else "file",
                    "size_bytes": candidate.stat().st_size if candidate.is_file() else None,
                }
            )

            if len(entries) >= max_results:
                break
    except Exception as error:
        return error_result(
            type(error).__name__,
            str(error),
            details={"path": path, "pattern": pattern},
        )

    return success_result(
        {
            "path": relative_to_workspace(base) or ".",
            "pattern": pattern,
            "count": len(entries),
            "max_results": max_results,
            "truncated": len(entries) >= max_results,
            "entries": entries,
        }
    )


def read_file(path: str, *, max_chars: int = MAX_READ_FILE_CHARS) -> ToolResult:
    try:
        file_path = ensure_file(path)
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as error:
        return error_result(
            type(error).__name__,
            str(error),
            details={"path": path},
        )

    truncated = len(content) > max_chars

    return success_result(
        {
            "path": relative_to_workspace(file_path),
            "size_bytes": file_path.stat().st_size,
            "content": content[:max_chars],
            "truncated": truncated,
            "max_chars": max_chars,
        }
    )


def get_file_info(path: str) -> ToolResult:
    try:
        resolved = resolve_workspace_path(path)
    except Exception as error:
        return error_result(
            type(error).__name__,
            str(error),
            details={"path": path},
        )

    exists = resolved.exists()
    data: dict[str, object] = {
        "path": relative_to_workspace(resolved),
        "exists": exists,
    }

    if exists:
        data.update(
            {
                "type": _path_type(resolved),
                "size_bytes": resolved.stat().st_size if resolved.is_file() else None,
            }
        )

    return success_result(data)


def _path_type(path: Path) -> str:
    if path.is_file():
        return "file"
    if path.is_dir():
        return "directory"
    return "other"
