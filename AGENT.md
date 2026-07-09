# Agent Instructions

- Follow existing project conventions. Make minimal, targeted changes.
- Do not modify unrelated files or introduce new dependencies unless necessary.
- Run relevant tests/lint/build commands before finishing when possible.
- Explain any assumptions or skipped checks.
- After modifying code, provide a suggested commit message in Conventional Commits format.
- For every Python function the agent writes, include concise inline comments inside the function body to explain the key implementation steps. Do not rely only on the function docstring for explanation.
- Write every Python function with explicit, Pylance-friendly type annotations. Avoid implicit Any, unsafe None usage, and ambiguous return types; resolve type issues in the code rather than suppressing warnings.
