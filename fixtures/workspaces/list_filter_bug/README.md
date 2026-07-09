# List Filter Bug Workspace

This is a small target workspace for SWE agent debugging experiments.

It intentionally contains one bug:

- `number_tools.filters.only_even([1, 2, 3, 4])` returns odd numbers
- The expected result is `[2, 4]`

## Agent Task

The tests are failing. Inspect the test file, find the implementation bug, and explain the fix.

## Run Tests

From this workspace root:

```bash
python -m unittest discover -s tests
```

