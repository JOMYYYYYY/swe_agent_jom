# Project Structure

This project uses a `src` layout. Runtime code lives under `src/swe_agent_jom`, while root-level files are reserved for project configuration, documentation, environment examples, and lock files.

## Recommended Layout

```text
src/swe_agent_jom/
  __init__.py
  main.py

  core/
    __init__.py
    tool_result.py
    messages.py
    types.py
    policy.py
    executor.py

  tools/
    __init__.py
    file_tool.py
    search_tool.py
    command_tool.py
    patch_tool.py
    git_tool.py

  runtime/
    __init__.py
    workspace.py
    command_runner.py
    patch_runner.py
    git_runner.py

  llm/
    __init__.py
    client.py
    openai_client.py
    deepseek_client.py

  prompts/
    system.md
    tool_instructions.md
    swe_agent.md

  memory/
    __init__.py
    trajectory.py
    store.py

  sandbox/
    __init__.py
    local.py
    docker.py

  evaluation/
    __init__.py
    tasks.py
    runner.py
    scorer.py

  config/
    __init__.py
    settings.py
```

## Module Boundaries

### `tools/`

`tools/` contains actions that the LLM is allowed to call directly.

Examples:

- `file_tool.py`: read, list, and inspect files
- `search_tool.py`: search code or filenames
- `command_tool.py`: run approved project commands
- `patch_tool.py`: apply or propose patches
- `git_tool.py`: inspect git status and diffs

A tool should be a thin public interface. It validates input, calls `runtime/`, and returns a unified tool result.

### `runtime/`

`runtime/` contains internal execution infrastructure. These modules are not exposed to the LLM directly.

Examples:

- `workspace.py`: resolve and validate workspace paths
- `command_runner.py`: execute commands with allowlists, timeouts, and output limits
- `patch_runner.py`: apply patches safely
- `git_runner.py`: run git operations safely

The rule is:

```text
tools/ = model-callable actions
runtime/ = internal safe execution primitives
```

For example, `tools/command_tool.py` may call `runtime/command_runner.py`, but the model should never call `command_runner.py` directly.

### `core/`

`core/` contains provider-neutral agent orchestration and shared types.

Examples:

- `tool_result.py`: unified success/error result shape
- `messages.py`: message conversion helpers
- `types.py`: shared protocol and state types
- `policy.py`: decides the next high-level action
- `executor.py`: runs the loop, dispatches tools, records trajectory, and handles limits

Avoid putting provider-specific SDK logic in `core/`.

### `llm/`

`llm/` contains model provider adapters.

`core/` should depend on a small protocol such as `LLMClient`, while concrete implementations live here:

- `openai_client.py`
- `deepseek_client.py`

This keeps OpenAI, DeepSeek, Anthropic, local model, or vLLM details out of the agent core.

### `memory/`

Start thin.

First version:

- `trajectory.py`: records steps, tool calls, observations, patches, test results
- `store.py`: persists trajectories, initially JSONL or SQLite

Do not add long-term memory or retrieval until the main SWE loop is working and there is a clear eval-backed need.

### `prompts/`

Prompt files should be editable outside Python code.

This is useful for:

- system prompt tuning
- tool instructions
- few-shot examples
- A/B prompt experiments

### `sandbox/`

`sandbox/` owns execution isolation.

First version can be local-only, but the boundary should exist because real SWE agents eventually need Docker or another isolation layer for running tests and model-generated commands.

### `evaluation/`

`evaluation/` contains benchmark and scoring code.

This should stay separate from the agent core so recursive self-improvement can be judged by reproducible evals instead of subjective impressions.

## Dependency Direction

Preferred dependency direction:

```text
config -> core types/interfaces
runtime -> config/core result types
tools -> runtime/core result types
llm -> core message/client protocols
core executor -> tools/llm/memory
memory -> core types
sandbox -> runtime/config
evaluation -> public agent/runtime APIs
```

Avoid circular dependencies. In particular:

- `core` should not import concrete tool implementations unless it is the executor/registry layer.
- `runtime` should not import `tools`.
- `tools` should call `runtime`, not duplicate execution logic.
- provider SDK code should stay in `llm/`, not leak into `core/`.

## Phase 1 Minimal Implementation

Before building a full SWE Agent, implement only the pieces needed for reliable workspace tools:

```text
src/swe_agent_jom/
  core/
    tool_result.py

  runtime/
    workspace.py
    command_runner.py

  tools/
    file_tool.py
    search_tool.py
    command_tool.py

  memory/
    trajectory.py

  config/
    settings.py
```

`prototype/4.0_swe_agent_file_tools.ipynb` should import these modules and demonstrate them. The notebook should not become the permanent runtime implementation.

## Design Principle

Build the agent in this order:

1. Safe workspace and command primitives.
2. Thin model-callable tools over those primitives.
3. Trajectory logging.
4. Agent executor loop.
5. Patch and test loop.
6. Evaluation harness.
7. Only then consider recursive self-improvement.
