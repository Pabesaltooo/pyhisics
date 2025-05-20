# tests/test_point.py
import unittest

from pyhsics.linalg.structures import Scalar, Vector, Point, Matrix

class TestPointBasic(unittest.TestCase):
    def test_init_and_value(self) -> None:
        p = Point([1, 2, 3])
        self.assertEqual(p.value, [1, 2, 3])
        self.assertEqual(len(p), 3)
        self.assertListEqual(list(p), [1, 2, 3])

    def test_str_and_repr_latex(self) -> None:
        p = Point([4, 5, 6])
        # __str__ should produce the same as Matrix of one row
        mat = Matrix([[4, 5, 6]])
        self.assertEqual(str(p), str(mat))
        # _repr_latex_ should return a LaTeX string
        latex = p._repr_latex_("P")
        self.assertIsInstance(latex, str)
        self.assertIn(r'\begin{pmatrix}', latex)  # basic LaTeX matrix marker


class TestPointArithmetic(unittest.TestCase):
    def setUp(self) -> None:
        self.p1 = Point([1, 2, 3])
        self.p2 = Point([4, 5, 6])
        self.v = Vector([7, 8, 9])
        self.s = Scalar(2)
        self.M = Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    def test_add_point(self) -> None:
        res = self.p1 + self.p2
        self.assertIsInstance(res, Point)
        self.assertEqual(res.value, [5, 7, 9])

    def test_add_vector(self) -> None:
        res = self.p1 + self.v
        self.assertIsInstance(res, Point)
        self.assertEqual(res.value, [8, 10, 12])

    def test_add_invalid(self) -> None:
        with self.assertRaises(NotImplementedError):
            _ = self.p1 + 123  # unsupported type

    def test_neg(self) -> None:
        neg = -self.p1
        self.assertIsInstance(neg, Point)
        self.assertEqual(neg.value, [-1, -2, -3])

    def test_subtract_point_or_vector(self) -> None:
        # p2 - p1 should yield a Vector
        diff = self.p2 - self.p1
        self.assertIsInstance(diff, Vector)
        self.assertEqual(diff.value, [3, 3, 3])
        # p1 - v should also yield Vector: v→-v then add to p1
        diff2 = self.p1 - self.v
        expected = [1 - 7, 2 - 8, 3 - 9]
        self.assertEqual(diff2.value, expected)

    def test_mul_scalar_like(self) -> None:
        # scalar literal
        res1 = self.p1 * 3
        self.assertIsInstance(res1, Point)
        self.assertEqual(res1.value, [3, 6, 9])
        # Scalar object
        res2 = self.p1 * self.s
        self.assertEqual(res2.value, [2, 4, 6])
        # __rmul__
        res3 = 4 * self.p1
        self.assertEqual(res3.value, [4, 8, 12])

    def test_mul_matrix(self) -> None:
        # identity matrix => should be unchanged
        res = self.p1 * self.M
        self.assertIsInstance(res, Point)
        self.assertEqual(res.value, [1, 2, 3])

        # another 3x3 matrix
        A = Matrix([[2,0,0],[0,3,0],[0,0,4]])
        res2 = self.p1 * A
        # each component scaled by diagonal
        self.assertEqual(res2.value, [2, 6, 12])

    def test_mul_invalid(self) -> None:
        with self.assertRaises(TypeError):
            _ = self.p1 * Vector([1, 2])  # wrong dimension
        self.assertEqual((self.p1 * self.M).__class__.__name__, "Point")

    def test_div_scalar(self) -> None:
        res = self.p2 / 2
        self.assertIsInstance(res, Point)
        self.assertEqual(res.value, [2.0, 2.5, 3.0])

    def test_div_invalid(self) -> None:
        with self.assertRaises(TypeError):
            _ = self.p1 / Vector([1, 2, 3])


class TestPointRoundingAndConversion(unittest.TestCase):
    def test_round(self) -> None:
        p = Point([1.2345, 6.789, 2.3456])
        pr = round(p, 2)
        self.assertIsInstance(pr, Point)
        self.assertAlmostEqual(pr.value[0], 1.23)
        self.assertAlmostEqual(pr.value[1], 6.79)
        self.assertAlmostEqual(pr.value[2], 2.35)

    def test_vector_conversion(self) -> None:
        p = Point([9, 8, 7])
        v = p.vector()
        self.assertIsInstance(v, Vector)
        self.assertEqual(v.value, [9, 8, 7])


if __name__ == "__main__":
    unittest.main()
