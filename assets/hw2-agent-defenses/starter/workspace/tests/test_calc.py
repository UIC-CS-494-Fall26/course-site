import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
from calc import add, mul, sub  # noqa: E402


class CalcTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

    def test_sub(self):
        self.assertEqual(sub(5, 3), 2)

    def test_mul(self):
        self.assertEqual(mul(4, 3), 12)


if __name__ == "__main__":
    unittest.main()
