from __future__ import annotations

from collections.abc import Sequence

from swe_agent_jom.core.tool_result import ToolResult, error_result
from swe_agent_jom.runtime.command_runner import run_command


def run_project_command(args: Sequence[str], cwd: str = ".") -> ToolResult:
    if isinstance(args, str):
        return error_result(
            "InvalidCommandArgsError",
            "Command args must be a list of strings, not one shell string.",
            details={"args": args},
        )

    return run_command(args, cwd=cwd)
