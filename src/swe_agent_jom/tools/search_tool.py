from __future__ import annotations

from pathlib import Path

from swe_agent_jom.config.settings import EXCLUDED_DIR_NAMES, MAX_SEARCH_RESULTS
from swe_agent_jom.core.tool_result import ToolResult, error_result, success_result
from swe_agent_jom.runtime.workspace import (
    ensure_directory,
    is_excluded_path,
    relative_to_workspace,
    resolve_workspace_path,
)


def search_code(
    query: str,
    path: str = ".",
    pattern: str = "*",
    *,
    case_sensitive: bool = False,
    max_results: int = MAX_SEARCH_RESULTS,
    max_file_bytes: int = 1_000_000,
) -> ToolResult:
    original_query = query
    comparable_query = query if case_sensitive else query.lower()

    if not original_query:
        return error_result(
            "EmptyQueryError",
            "Search query cannot be empty.",
        )

    try:
        start = resolve_workspace_path(path)
    except Exception as error:
        return error_result(
            type(error).__name__,
            str(error),
            details={"path": path},
        )

    if not start.exists():
        return error_result(
            "FileNotFoundError",
            f"Search path does not exist: {path}",
            details={"path": path},
        )

    files = [start] if start.is_file() else _iter_files(path, pattern)
    matches: list[dict[str, object]] = []

    for file_path in files:
        if len(matches) >= max_results:
            break

        if is_excluded_path(file_path, EXCLUDED_DIR_NAMES):
            continue

        if not file_path.is_file():
            continue

        try:
            if file_path.stat().st_size > max_file_bytes:
                continue

            content = file_path.read_bytes()
        except OSError:
            continue

        if b"\x00" in content:
            continue

        text = content.decode("utf-8", errors="replace")

        for line_number, line in enumerate(text.splitlines(), start=1):
            comparable_line = line if case_sensitive else line.lower()
            if comparable_query in comparable_line:
                matches.append(
                    {
                        "path": relative_to_workspace(file_path),
                        "line_number": line_number,
                        "line": line,
                    }
                )

                if len(matches) >= max_results:
                    break

    return success_result(
        {
            "query": original_query,
            "path": relative_to_workspace(start),
            "pattern": pattern,
            "case_sensitive": case_sensitive,
            "count": len(matches),
            "max_results": max_results,
            "truncated": len(matches) >= max_results,
            "matches": matches,
        }
    )


def _iter_files(path: str, pattern: str) -> list[Path]:
    base = ensure_directory(path)
    return sorted(candidate for candidate in base.rglob(pattern) if candidate.is_file())
