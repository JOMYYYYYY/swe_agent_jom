from __future__ import annotations

import os
from pathlib import Path


WORKSPACE_ROOT = Path(
    os.getenv("SWE_AGENT_JOM_WORKSPACE_ROOT", str(Path.cwd()))
).resolve()

COMMAND_TIMEOUT_SECONDS = int(os.getenv("SWE_AGENT_JOM_COMMAND_TIMEOUT", "30"))
MAX_COMMAND_OUTPUT_CHARS = int(
    os.getenv("SWE_AGENT_JOM_MAX_COMMAND_OUTPUT_CHARS", "20000")
)
MAX_READ_FILE_CHARS = int(os.getenv("SWE_AGENT_JOM_MAX_READ_FILE_CHARS", "12000"))
MAX_SEARCH_RESULTS = int(os.getenv("SWE_AGENT_JOM_MAX_SEARCH_RESULTS", "50"))
MAX_LIST_FILES_RESULTS = int(os.getenv("SWE_AGENT_JOM_MAX_LIST_FILES_RESULTS", "200"))

# Exact command allowlist. Keep this intentionally narrow: allowing arbitrary
# extra arguments can turn read-only commands into commands with side effects.
ALLOWED_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("python", "-m", "pytest"),
    ("python", "-m", "unittest"),
    ("python", "-m", "unittest", "discover", "-s", "tests"),
    ("python", "-m", "compileall", "src"),
    ("pytest",),
    ("git", "status"),
    ("git", "status", "--short"),
    ("git", "diff"),
    ("git", "diff", "--stat"),
)

EXCLUDED_DIR_NAMES: frozenset[str] = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
    }
)
