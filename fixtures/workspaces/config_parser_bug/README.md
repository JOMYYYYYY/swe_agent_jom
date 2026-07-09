# Config Parser Bug Workspace

This is a small target workspace for SWE agent debugging experiments.

It intentionally contains one bug:

- `config_tools.parser.parse_bool("false")` returns `True`
- The expected result is `False`

## Agent Task

The tests are failing. Inspect the test file, find the implementation bug, and explain the fix.

## Run Tests

From this workspace root:

```bash
python -m unittest discover -s tests
```

