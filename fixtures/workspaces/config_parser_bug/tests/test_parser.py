import sys
import unittest
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = WORKSPACE_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from config_tools import parse_bool, parse_port


class ParserTests(unittest.TestCase):
    def test_parses_positive_port(self) -> None:
        self.assertEqual(parse_port("8080"), 8080)

    def test_rejects_non_positive_port(self) -> None:
        with self.assertRaisesRegex(ValueError, "Port must be positive"):
            parse_port("0")

    def test_parses_true_values(self) -> None:
        self.assertTrue(parse_bool("true"))
        self.assertTrue(parse_bool("YES"))
        self.assertTrue(parse_bool("1"))

    def test_parses_false_values(self) -> None:
        self.assertFalse(parse_bool("false"))
        self.assertFalse(parse_bool("NO"))
        self.assertFalse(parse_bool("0"))

    def test_rejects_unknown_bool_value(self) -> None:
        with self.assertRaisesRegex(ValueError, "Invalid boolean value"):
            parse_bool("maybe")


if __name__ == "__main__":
    unittest.main()

