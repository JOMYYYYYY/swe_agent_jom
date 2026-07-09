import sys
import unittest
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = WORKSPACE_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from number_tools import only_even, only_positive


class FilterTests(unittest.TestCase):
    def test_filters_positive_numbers(self) -> None:
        self.assertEqual(only_positive([-2, 0, 3, 5]), [3, 5])

    def test_filters_even_numbers(self) -> None:
        self.assertEqual(only_even([1, 2, 3, 4]), [2, 4])


if __name__ == "__main__":
    unittest.main()
