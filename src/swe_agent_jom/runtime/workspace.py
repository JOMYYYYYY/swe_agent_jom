from __future__ import annotations

from pathlib import Path

from swe_agent_jom.config.settings import WORKSPACE_ROOT


class WorkspacePathError(ValueError):
    """Raised when a path escapes the configured workspace."""


def workspace_root() -> Path:
    """Return the configured workspace root.

    返回当前 agent 被允许操作的根目录。存在这个函数，是为了让其他模块
    不直接依赖配置变量本身，而是通过 runtime 层拿到 workspace boundary。
    """
    return WORKSPACE_ROOT


def resolve_workspace_path(path: str | Path = ".") -> Path:
    """Resolve a user-provided path and keep it inside WORKSPACE_ROOT.

    把外部传入的 path 转成规范化后的 absolute Path，并检查它没有逃出
    workspace。这个函数是 file/search/command tools 的核心 safety gate：
    所有不可信路径都应该先经过这里，再用于读文件、列目录或作为 cwd。
    """
    candidate = Path(path)

    if not candidate.is_absolute():
        candidate = WORKSPACE_ROOT / candidate

    # Normalize ".", "..", and symlinks where possible. strict=False allows paths
    # that do not exist yet, which is useful for future write/create-file tools.
    resolved = candidate.resolve(strict=False)

    if not _is_relative_to(resolved, WORKSPACE_ROOT):
        raise WorkspacePathError(
            f"Path escapes workspace: {path}. Workspace root is {WORKSPACE_ROOT}."
        )

    return resolved


def relative_to_workspace(path: str | Path) -> str:
    """Return a workspace-relative POSIX path after safety validation.

    把安全路径转换成相对于 workspace 的字符串，例如 README.md 或 src/main.py。
    存在这个函数，是为了工具返回结果时不要暴露过长的本机绝对路径，同时仍然
    保证传入路径没有逃出 workspace。
    """
    resolved = resolve_workspace_path(path)
    return resolved.relative_to(WORKSPACE_ROOT).as_posix()


def ensure_file(path: str | Path) -> Path:
    """Resolve path and require it to be an existing file.

    用于 read_file/get file content 这类工具：先做 workspace safety check，
    再确认目标真的存在且是 file。这样调用方不用重复写相同的校验逻辑。
    """
    resolved = resolve_workspace_path(path)

    if not resolved.exists():
        raise FileNotFoundError(f"File does not exist: {relative_to_workspace(resolved)}")

    if not resolved.is_file():
        raise IsADirectoryError(f"Expected a file: {relative_to_workspace(resolved)}")

    return resolved


def ensure_directory(path: str | Path = ".") -> Path:
    """Resolve path and require it to be an existing directory.

    用于 list/search/cwd 这类需要 directory 的场景：先保证路径没有越界，
    再确认它存在且是目录。存在这个函数，是为了统一目录校验和错误类型。
    """
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
    """Return True if a path should be skipped by workspace tools.

    判断路径是否位于 .git/.venv/node_modules 等排除目录中。存在这个函数，
    是为了让 list/search tools 避开依赖、缓存、构建产物和 Git 内部数据，
    减少噪音、提升速度，也降低 agent 读到无关内容的概率。
    """
    try:
        relative_parts = path.resolve(strict=False).relative_to(WORKSPACE_ROOT).parts
    except ValueError:
        # If it cannot be made relative to WORKSPACE_ROOT, treat it as excluded.
        return True

    return any(part in excluded_dir_names for part in relative_parts)


def _is_relative_to(path: Path, parent: Path) -> bool:
    """Compatibility helper for checking whether path is under parent.

    检查 path 是否在 parent 目录下面。单独封装这个 helper，是为了让
    resolve_workspace_path 的安全判断更直观，并把 ValueError handling
    集中在一个地方。
    """
    try:
        path.relative_to(parent)
    except ValueError:
        return False

    return True
