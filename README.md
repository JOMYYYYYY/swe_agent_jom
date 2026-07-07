# SWE Agent JOM

A learning-oriented SWE agent prototype. The current codebase focuses on building a safe workspace tool runtime before adding an LLM-driven agent loop.

## Current Status

Implemented:

- `src` package layout
- unified tool result shape
- workspace path guards
- exact allowlisted command execution with `shell=False`
- model-callable file, search, and command tool wrappers
- thin trajectory logging

Not implemented yet:

- LLM provider adapters
- agent executor loop
- patch application tools
- sandbox isolation
- benchmark/evaluation runner

## Setup

Create a `.env` file from the example if you want to run the notebook prototypes that call DeepSeek:

```text
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

Install dependencies with your preferred Python workflow. This project currently targets Python 3.13.

## Safety Notes

The command runtime accepts `list[str]` only, runs with `shell=False`, and only executes exact commands listed in `swe_agent_jom.config.settings.ALLOWED_COMMANDS`.

By default, `WORKSPACE_ROOT` is the current working directory. Set `SWE_AGENT_JOM_WORKSPACE_ROOT` to target a different workspace explicitly.
