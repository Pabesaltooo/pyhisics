# tests/test_scalar.py

import unittest

from pyhsics.linalg.structures import Scalar, Vector, Matrix



class TestScalarBasic(unittest.TestCase):
    def test_init_and_value(self) -> None:
        s = Scalar(5)
        self.assertEqual(s.value, 5)
        self.assertIsInstance(s.value, int)

    def test_str_and_repr_latex(self) -> None:
        s = Scalar(3.14)
        # str should not raise
        _ = str(s)
        # latex repr should not raise
        _ = s._repr_latex_("x")

    def test_is_zero_and_is_identity(self) -> None:
        self.assertTrue(Scalar(0).is_zero())
        self.assertFalse(Scalar(1e-12).is_zero())
        self.assertTrue(Scalar(1).is_identity())
        self.assertFalse(Scalar(2).is_identity())


class TestScalarArithmetic(unittest.TestCase):
    def test_add_and_sub(self) -> None:
        a = Scalar(2)
        b = Scalar(3)
        self.assertEqual((a + b).value, 5)
        self.assertEqual((a - b).value, -1)

    def test_neg(self) -> None:
        s = Scalar(7)
        self.assertEqual((-s).value, -7)

    def test_mul_scalar(self) -> None:
        a = Scalar(4)
        b = Scalar(5)
        self.assertEqual((a * b).value, 20)
        # native int
        self.assertEqual((a * 2).value, 8)
        self.assertEqual((2 * a).value, 8)

    def test_mul_vector(self) -> None:
        v = Vector([1, 2, 3])
        s = Scalar(10)
        result = s * v
        self.assertIsInstance(result, Vector)
        self.assertEqual(result.value, [10, 20, 30])

    def test_mul_matrix(self) -> None:
        M = Matrix([[1, 2], [3, 4]])
        s = Scalar(3)
        result = s * M
        self.assertIsInstance(result, Matrix)
        self.assertEqual(result.value, [[3, 6], [9, 12]])

    def test_mul_invalid(self) -> None:
        s = Scalar(2)
        with self.assertRaises(TypeError):
            _ = s * "not a scalar or sequence"  # should return NotImplemented or raise

    def test_div_and_rdiv(self) -> None:
        a = Scalar(10)
        b = Scalar(2)
        self.assertEqual((a / b).value, 5)
        # native scalar
        self.assertEqual((a / 2).value, 5)
        self.assertEqual((20 / a).value, 2)

    def test_div_by_zero(self) -> None:
        with self.assertRaises(ZeroDivisionError):
            _ = Scalar(0).inv()

        with self.assertRaises(ZeroDivisionError):
            _ = Scalar(1) / Scalar(0)

    def test_div_type_error(self) -> None:
        s = Scalar(5)
        with self.assertRaises(TypeError):
            _ = s / Vector([1, 2, 3])

    def test_inv(self) -> None:
        self.assertEqual(Scalar(4).inv().value, 0.25)


class TestScalarPower(unittest.TestCase):
    def test_pow_with_int(self) -> None:
        s = Scalar(2)
        self.assertEqual((s ** 3).value, 8)

    def test_pow_with_scalar(self) -> None:
        s = Scalar(5)
        e = Scalar(2)
        self.assertEqual((s ** e).value, 25)

    def test_pow_invalid(self) -> None:
        with self.assertRaises(TypeError):
            _ = Scalar(2) ** [1, 2]  # invalid exponent type


class TestScalarCoercions(unittest.TestCase):
    def test_float_and_int(self) -> None:
        s_real = Scalar(3.7)
        self.assertIsInstance(float(s_real), float)
        self.assertEqual(int(s_real), 3)

        s_complex = Scalar(2 + 5j)
        self.assertIsInstance(float(s_complex), float)
        self.assertEqual(int(s_complex), 2)

    def test_round(self) -> None:
        s = Scalar(3.14159)
        rounded = round(s, 3)
        self.assertIsInstance(rounded, Scalar)
        self.assertAlmostEqual(rounded.value, 3.142)

    def test_abs(self) -> None:
        s = Scalar(-7)
        a = abs(s)
        self.assertIsInstance(a, Scalar)
        self.assertEqual(a.value, 7)


class TestScalarComparisons(unittest.TestCase):
    def test_equality_and_order(self) -> None:
        a = Scalar(2)
        b = Scalar(3)
        self.assertTrue(a == 2)
        self.assertTrue(2 == a)
        self.assertFalse(a == b)
        self.assertTrue(a < b)
        self.assertTrue(b > a)
        self.assertTrue(a <= Scalar(2))
        self.assertTrue(b >= Scalar(3))

    def test_comparison_with_non_algebraic(self) -> None:
        a = Scalar(5)
        # Should wrap native into Scalar via T2Algebraic internally
        self.assertTrue(a == 5)
        self.assertTrue(a != 4)


if __name__ == "__main__":
    unittest.main()
