from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence

from swe_agent_jom.config.settings import (
    ALLOWED_COMMANDS,
    COMMAND_TIMEOUT_SECONDS,
    MAX_COMMAND_OUTPUT_CHARS,
)
from swe_agent_jom.core.tool_result import ToolResult, error_result, success_result
from swe_agent_jom.runtime.workspace import resolve_workspace_path


def run_command(
    args: Sequence[str],
    *,
    cwd: str = ".",
    timeout_seconds: int = COMMAND_TIMEOUT_SECONDS,
    max_output_chars: int = MAX_COMMAND_OUTPUT_CHARS,
) -> ToolResult:
    if not args:
        return error_result(
            "EmptyCommandError",
            "Command args cannot be empty.",
        )

    if not all(isinstance(arg, str) and arg for arg in args):
        return error_result(
            "InvalidCommandArgsError",
            "Command args must be a non-empty list of non-empty strings.",
            details={"args": list(args)},
        )

    command = tuple(args)

    if not is_allowed_command(command):
        return error_result(
            "CommandNotAllowedError",
            "Command is not in the exact command allowlist.",
            details={
                "args": list(command),
                "allowed_commands": [list(allowed) for allowed in ALLOWED_COMMANDS],
            },
        )

    try:
        resolved_cwd = resolve_workspace_path(cwd)
    except Exception as error:
        return error_result(
            "InvalidWorkingDirectoryError",
            str(error),
            details={"cwd": cwd},
        )

    run_args = list(command)
    if run_args[0] == "python":
        run_args[0] = sys.executable

    try:
        completed = subprocess.run(
            run_args,
            cwd=resolved_cwd,
            capture_output=True,
            text=True,
            shell=False,
            timeout=timeout_seconds,
        )
    except FileNotFoundError as error:
        return error_result(
            "CommandExecutableNotFoundError",
            str(error),
            details={"args": list(command)},
        )
    except subprocess.TimeoutExpired as error:
        return error_result(
            "CommandTimeoutError",
            f"Command timed out after {timeout_seconds} seconds.",
            details={
                "args": list(command),
                "stdout": _truncate(_output_to_text(error.stdout), max_output_chars),
                "stderr": _truncate(_output_to_text(error.stderr), max_output_chars),
            },
        )

    return success_result(
        {
            "args": list(command),
            "cwd": str(resolved_cwd),
            "exit_code": completed.returncode,
            "stdout": _truncate(completed.stdout, max_output_chars),
            "stderr": _truncate(completed.stderr, max_output_chars),
            "stdout_truncated": len(completed.stdout) > max_output_chars,
            "stderr_truncated": len(completed.stderr) > max_output_chars,
        }
    )


def is_allowed_command(args: Sequence[str]) -> bool:
    return tuple(args) in ALLOWED_COMMANDS


def _output_to_text(output: str | bytes | bytearray | memoryview | None) -> str:
    if output is None:
        return ""

    if isinstance(output, str):
        return output

    return bytes(output).decode("utf-8", errors="replace")


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text

    return text[:max_chars] + f"\n... <truncated {len(text) - max_chars} chars>"
