# tests/test_vector.py

import unittest
from typing import Any, List

from pyhsics.linalg.structures.vector import Vector
from pyhsics.linalg.structures.scalar import Scalar
from pyhsics.linalg.structures.matrix import Matrix
from pyhsics.linalg.structures.point import Point


class TestVectorBasic(unittest.TestCase):
    def test_init_and_value(self) -> None:
        v = Vector([1, 2, 3])
        self.assertEqual(v.value, [1, 2, 3])
        self.assertEqual(len(v), 3)
        self.assertListEqual(list(v), [1, 2, 3])
        self.assertEqual(v[0], 1)

    def test_str_and_repr_latex(self) -> None:
        v = Vector([1.1, 2.2])
        # should not raise
        _ = str(v)
        _ = v._repr_latex_("v")


class TestVectorArithmetic(unittest.TestCase):
    def test_add_sub_neg(self) -> None:
        v1 = Vector([1, 2])
        v2 = Vector([3, 4])
        self.assertEqual((v1 + v2).value, [4, 6])
        self.assertEqual((v1 - v2).value, [-2, -2])
        self.assertEqual((-v1).value, [-1, -2])

    def test_add_point(self) -> None:
        p = Point([1, 2, 3])
        v = Vector([4, 5, 6])
        res = v + p
        self.assertIsInstance(res, Point)
        self.assertEqual(res.value, [5, 7, 9])

    def test_mul_scalar(self) -> None:
        v = Vector([1, 2, 3])
        s = Scalar(5)
        self.assertEqual((v * s).value, [5, 10, 15])
        self.assertEqual((v * 2).value, [2, 4, 6])
        self.assertEqual((3 * v).value, [3, 6, 9])

    def test_mul_vector_dot(self) -> None:
        v1 = Vector([1, 2, 3])
        v2 = Vector([4, 5, 6])
        dot = v1 * v2
        self.assertIsInstance(dot, Scalar)
        self.assertEqual(dot.value, 1*4 + 2*5 + 3*6)

    def test_div_scalar(self) -> None:
        v = Vector([2, 4, 6])
        self.assertEqual((v / 2).value, [1, 2, 3])
        self.assertEqual((v / Scalar(2)).value, [1, 2, 3])
        with self.assertRaises(TypeError):
            _ = v / Vector([1, 2, 3])

    def test_dot_default_form(self) -> None:
        v1 = Vector([1, 0])
        v2 = Vector([0, 1])
        # should compute v1·v2 = 0
        self.assertEqual(v1.dot(v2).value, 0)

    def test_dot_custom_form(self) -> None:
        # custom bilinear form [[2,0],[0,3]]
        form = Matrix([[2, 0], [0, 3]])
        Vector.set_dot_form(form)
        v1 = Vector([1, 2])
        v2 = Vector([3, 4])
        # v1ᵀ M v2 = [2,4]·[[2,0],[0,3]]·[3,4] = [2,4]·[6,12] = 30
        self.assertEqual(v1.dot(v2).value, 30)

    def test_dot_invalid_dim(self) -> None:
        v1 = Vector([1, 2, 3])
        v2 = Vector([4, 5])
        with self.assertRaises(ValueError):
            _ = v1.dot(v2)

    def test_magnitude_and_norm(self) -> None:
        v = Vector([3, 4])
        mag = v.magnitude
        self.assertIsInstance(mag, Scalar)
        self.assertAlmostEqual(mag.value, 5.0)
        norm = v.norm()
        self.assertIsInstance(norm, Vector)
        self.assertAlmostEqual(norm.value[0], 3/5)
        self.assertAlmostEqual(norm.value[1], 4/5)

    def test_norm_zero_vector(self) -> None:
        with self.assertRaises(ValueError):
            Vector([0, 0, 0]).norm()

    def test_cross(self) -> None:
        v1 = Vector([1, 0, 0])
        v2 = Vector([0, 1, 0])
        cross = v1.cross(v2)
        self.assertIsInstance(cross, Vector)
        self.assertEqual(cross.value, [0, 0, 1])

    def test_cross_invalid_dim(self) -> None:
        with self.assertRaises(ValueError):
            Vector([1, 2]).cross(Vector([3, 4]))


class TestVectorConstructors(unittest.TestCase):
    def test_zeros_ones(self) -> None:
        z = Vector.zeros(4)
        o = Vector.ones(2)
        self.assertEqual(z.value, [0, 0, 0, 0])
        self.assertEqual(o.value, [1, 1])

    def test_unit_vectors(self) -> None:
        u = Vector.unit_vectors(3)
        expected = [[1,0,0], [0,1,0], [0,0,1]]
        self.assertEqual([v.value for v in u], expected)

    def test_unit_vecs_alias(self) -> None:
        u1 = Vector.unit_vectors(2)
        u2 = Vector.unit_vecs(2)
        self.assertEqual([v.value for v in u1], [v.value for v in u2])

    def test_rand_randn(self) -> None:
        r = Vector.rand(5)
        rn = Vector.randn(5)
        self.assertEqual(len(r), 5)
        self.assertEqual(len(rn), 5)
        # values should be floats/ints
        self.assertTrue(all(isinstance(x, (int, float)) for x in r))
        self.assertTrue(all(isinstance(x, (int, float)) for x in rn))


class TestVectorAccessors(unittest.TestCase):
    def test_xyz_properties(self) -> None:
        v = Vector([7, 8, 9])
        self.assertIsInstance(v.x, Scalar)
        self.assertEqual(v.x.value, 7)
        self.assertEqual(v.y.value, 8)
        self.assertEqual(v.z.value, 9)

    def test_z_property_error(self) -> None:
        with self.assertRaises(AttributeError):
            _ = Vector([1, 2]).z

    def test_point_conversion(self) -> None:
        v = Vector([1, 2, 3])
        p = v.point()
        self.assertIsInstance(p, Point)
        self.assertEqual(p.value, [1, 2, 3])


class TestEqualityAndHash(unittest.TestCase):
    def test_equality_colinear(self) -> None:
        v1 = Vector([1, 2, 3])
        v2 = Vector([2, 4, 6])
        # colinear => considered equal
        self.assertTrue(v1 == v2)
        self.assertFalse(v1 != v2)

    def test_equality_non_colinear(self) -> None:
        v1 = Vector([1, 0, 0])
        v2 = Vector([0, 1, 0])
        self.assertFalse(v1 == v2)
        self.assertTrue(v1 != v2)

    def test_hash_consistency(self) -> None:
        v = Vector([3, 0, 4])
        h1 = hash(v)
        h2 = hash(v)
        self.assertEqual(h1, h2)


class TestRounding(unittest.TestCase):
    def test_round(self) -> None:
        v = Vector([1.2345, 6.789])
        vr = round(v, 2)
        self.assertIsInstance(vr, Vector)
        self.assertAlmostEqual(vr.value[0], 1.23)
        self.assertAlmostEqual(vr.value[1], 6.79)


if __name__ == "__main__":
    unittest.main()
