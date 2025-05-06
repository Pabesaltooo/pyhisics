import math
import unittest

from pyhsics.linalg.vector import Vector
from pyhsics.linalg.scalar import Scalar


def vec_almost_equal(testcase: unittest.TestCase,
                     v: Vector, expected, places: int = 9):
    if isinstance(expected, Vector):
        expected = expected.value
    testcase.assertEqual(len(v), len(expected))
    for a, b in zip(v, expected):
        testcase.assertAlmostEqual(a, b, places=places)


class TestVector(unittest.TestCase):
    # ---------- aritmética ---------------------------------------------
    def test_real_vector_ops(self):
        v1 = Vector([1, 2, 3])
        v2 = Vector([4, 5, 6])
        vec_almost_equal(self, v1 + v2, [5, 7, 9])
        vec_almost_equal(self, v2 - v1, [3, 3, 3])
        vec_almost_equal(self, -v1, [-1, -2, -3])
        vec_almost_equal(self, 2 * v1, [2, 4, 6])
        vec_almost_equal(self, v1 * 2, [2, 4, 6])
        vec_almost_equal(self, v1 / 2, [0.5, 1.0, 1.5])

    def test_complex_vector_ops(self):
        v = Vector([1 + 1j, 2 - 1j])
        vec_almost_equal(self, v * 2, [2 + 2j, 4 - 2j])
        vec_almost_equal(self, v / (1 - 1j),
                         [(1 + 1j) / (1 - 1j), (2 - 1j) / (1 - 1j)])

    # ---------- producto, norma ----------------------------------------
    def test_dot_cross_mag_norm(self):
        i = Vector([1, 0, 0])
        j = Vector([0, 1, 0])
        self.assertEqual(i.dot(j).value, 0)
        self.assertEqual(i.cross(j), Vector([0, 0, 1]))

        v = Vector([3, 4])
        self.assertAlmostEqual(v.magnitude.value, 5.0, places=9)
        self.assertAlmostEqual(v.norm().magnitude.value, 1.0, places=9)

    # ---------- unit helpers -------------------------------------------
    def test_unit_vectors(self):
        n = 4
        units = Vector.unit_vectors(n)
        self.assertEqual(len(units), n)
        for k, e_k in enumerate(units):
            vec_almost_equal(self, e_k, [1 if i == k else 0 for i in range(n)])


if __name__ == "__main__":
    unittest.main()
