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
    """List files/directories under a workspace path.

    列出 workspace 内某个目录下匹配 pattern 的路径。这个函数是给未来
    agent/LLM 使用的 file listing tool：它不直接信任输入路径，而是先通过
    ensure_directory 做 workspace safety check，再返回统一的 ToolResult。

    存在原因：agent 需要先观察项目结构，但不能扫描无限多文件，也不应该进入
    .git/.venv/node_modules 等噪音目录，所以这里同时做 exclusion 和 max_results
    限制。
    """
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
            # Skip dependency/cache/build internals; they are usually noisy for agents.
            if is_excluded_path(candidate, EXCLUDED_DIR_NAMES):
                continue

            entries.append(
                {
                    "path": relative_to_workspace(candidate),
                    "type": "directory" if candidate.is_dir() else "file",
                    "size_bytes": candidate.stat().st_size if candidate.is_file() else None,
                }
            )

            # Keep tool output bounded so it stays usable for model context.
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
    """Read a text file from inside the workspace.

    读取 workspace 内的一个文件内容。这个函数先用 ensure_file 确认 path 没有
    逃出 workspace、目标存在、并且确实是 file，然后用 UTF-8 读取文本内容。

    存在原因：agent 需要查看源码和配置文件，但一次性返回太多内容会浪费上下文，
    所以通过 max_chars 截断，并在返回值里标记 truncated。
    """
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
    """Return basic metadata for a workspace path.

    获取一个 workspace 路径的基础信息：是否存在、是 file/directory/other，
    如果是文件则返回 size_bytes。这个函数不会读取文件内容，只做轻量 inspection。

    存在原因：agent 在决定下一步之前，经常需要先确认某个路径是否存在、类型是什么，
    但不一定需要 read_file 的完整内容。
    """
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
    """Classify a Path for get_file_info output.

    把 pathlib 的 is_file/is_dir 判断转换成稳定字符串，方便 ToolResult 以简单
    JSON-like 结构返回给 agent。
    """
    if path.is_file():
        return "file"
    if path.is_dir():
        return "directory"
    return "other"
