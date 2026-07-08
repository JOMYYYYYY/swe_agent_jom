import sys
import unittest
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = WORKSPACE_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from demo_math import add, divide, multiply, subtract


class CalculatorTests(unittest.TestCase):
    def test_adds_two_numbers(self) -> None:
        self.assertEqual(add(2, 3), 5)

    def test_subtracts_two_numbers(self) -> None:
        self.assertEqual(subtract(8, 3), 5)

    def test_multiplies_two_numbers(self) -> None:
        self.assertEqual(multiply(4, 3), 12)

    def test_divides_two_numbers(self) -> None:
        self.assertEqual(divide(8, 2), 4)

    def test_divide_by_zero_raises_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "Cannot divide by zero"):
            divide(1, 0)


if __name__ == "__main__":
    unittest.main()

