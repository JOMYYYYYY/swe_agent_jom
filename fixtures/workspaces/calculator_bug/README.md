# Calculator Bug Workspace

This is a small target workspace for SWE agent experiments.

It intentionally contains one bug:

- `demo_math.calculator.add(2, 3)` returns `-1`
- The expected result is `5`

## Agent Task

The tests are failing. Inspect the test file, find the implementation bug, and explain the fix.

## Run Tests

From this workspace root:

```bash
python -m unittest discover -s tests
```
