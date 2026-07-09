# String Utils Bug Workspace

This is a small target workspace for SWE agent debugging experiments.

It intentionally contains one bug:

- `text_tools.normalizer.normalize_slug("Hello World")` returns `hello_world`
- The expected result is `hello-world`

## Agent Task

The tests are failing. Inspect the test file, find the implementation bug, and explain the fix.

## Run Tests

From this workspace root:

```bash
python -m unittest discover -s tests
```

