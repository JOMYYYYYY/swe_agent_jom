import sys
import unittest
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = WORKSPACE_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from text_tools import normalize_slug, normalize_whitespace


class NormalizerTests(unittest.TestCase):
    def test_normalizes_whitespace(self) -> None:
        self.assertEqual(normalize_whitespace(" hello   world "), "hello world")

    def test_normalizes_slug_with_hyphen(self) -> None:
        self.assertEqual(normalize_slug("Hello World"), "hello-world")


if __name__ == "__main__":
    unittest.main()
