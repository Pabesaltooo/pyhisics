import math
import unittest

from pyhsics.linalg.scalar import Scalar, ScalarLike


class TestScalar(unittest.TestCase):
    def assertScalarAlmostEqual(self, a: Scalar, b: ScalarLike, places: int = 9):
        if not isinstance(b, Scalar):
            b = Scalar(b)
        self.assertAlmostEqual(a.value, b.value, places=places)

    # ---------- básicos -------------------------------------------------
    def test_real_arithmetic(self):
        s1, s2 = Scalar(2), Scalar(3.5)
        self.assertScalarAlmostEqual(s1 + s2, 5.5)
        self.assertScalarAlmostEqual(s2 - s1, 1.5)
        self.assertScalarAlmostEqual(s1 * s2, 7.0)
        self.assertScalarAlmostEqual(s2 / s1, 1.75)
        self.assertScalarAlmostEqual(-s1, -2)
        self.assertScalarAlmostEqual(s1 ** 3, 8)

    def test_complex_arithmetic(self):
        a, b = Scalar(2 + 3j), Scalar(1 - 1j)
        self.assertScalarAlmostEqual(a + b, 3 + 2j)
        self.assertScalarAlmostEqual(a * b, (2 + 3j) * (1 - 1j))
        self.assertScalarAlmostEqual(a / 2, 1 + 1.5j)

    def test_identity_zero(self):
        self.assertTrue(Scalar(0).is_zero())
        self.assertTrue(Scalar(1).is_identity())
        self.assertFalse(Scalar(2).is_zero())
        self.assertNotEqual(Scalar(2), Scalar(3))

    def test_round_abs(self):
        s = Scalar(math.pi)
        self.assertEqual(round(s, 2).value, 3.14)
        self.assertEqual(abs(Scalar(-5)).value, 5)


if __name__ == "__main__":
    unittest.main()
