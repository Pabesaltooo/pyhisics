# tests/test_algebraic_core.py

import unittest
from pyhsics.linalg.core import algebraic_core as ac

class TestValidationHelpers(unittest.TestCase):
    def test_validate_same_len_valid(self) -> None:
        # No debería lanzar
        ac._validate_same_len([1, 2, 3], [4, 5, 6])

    def test_validate_same_len_invalid(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            ac._validate_same_len([1, 2], [3])
        self.assertIn("Dimensiones incompatibles", str(ctx.exception))

    def test_validate_same_dim_valid(self) -> None:
        a = [[1, 2], [3, 4]]
        b = [[5, 6], [7, 8]]
        ac._validate_same_dim(a, b)

    def test_validate_same_dim_invalid(self) -> None:
        a = [[1, 2], [3, 4]]
        b = [[5, 6, 7]]
        with self.assertRaises(ValueError):
            ac._validate_same_dim(a, b)


class TestAlgebraicOps(unittest.TestCase):
    def test_add_scalar_like(self) -> None:
        self.assertEqual(ac.AlgebraicOps.add_scalar_like(2, 3), 5)

    def test_add_vector_like(self) -> None:
        v1 = [1, 2, 3]
        v2 = [4, 5, 6]
        self.assertEqual(ac.AlgebraicOps.add_vector_like(v1, v2), [5, 7, 9])

    def test_add_vector_like_invalid(self) -> None:
        with self.assertRaises(ValueError):
            ac.AlgebraicOps.add_vector_like([1, 2], [3])

    def test_add_matrix_like(self) -> None:
        m1 = [[1, 2], [3, 4]]
        m2 = [[5, 6], [7, 8]]
        self.assertEqual(ac.AlgebraicOps.add_matrix_like(m1, m2), [[6, 8], [10, 12]])

    def test_mul_scalar_like(self) -> None:
        self.assertEqual(ac.AlgebraicOps.mul_scalar_like(3, 4), 12)

    def test_mul_vector_scalar_like(self) -> None:
        self.assertEqual(ac.AlgebraicOps.mul_vector_scalar_like([1, 2], 3), [3, 6])

    def test_mul_matrix_scalar_like(self) -> None:
        M = [[1, 2], [3, 4]]
        self.assertEqual(ac.AlgebraicOps.mul_matrix_scalar_like(M, 2), [[2, 4], [6, 8]])

    def test_st_dot(self) -> None:
        self.assertEqual(ac.AlgebraicOps.st_dot([1, 2, 3], [4, 5, 6]), 32)

    def test_st_dot_invalid(self) -> None:
        with self.assertRaises(ValueError):
            ac.AlgebraicOps.st_dot([1, 2], [3])

    def test_mul_mat_vec_like(self) -> None:
        M = [[1, 0], [0, 1]]
        v = [5, 7]
        self.assertEqual(ac.AlgebraicOps.mul_mat_vec_like(M, v), [5, 7])

    def test_mul_mat_vec_like_invalid(self) -> None:
        M = [[1, 2, 3]]
        v = [4, 5]
        with self.assertRaises(ValueError):
            ac.AlgebraicOps.mul_mat_vec_like(M, v)

    def test_mul_mat_mat_like(self) -> None:
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        self.assertEqual(ac.AlgebraicOps.mul_mat_mat_like(A, B), [[19, 22], [43, 50]])

    def test_mul_mat_mat_like_invalid(self) -> None:
        A = [[1, 2]]
        B = [[3, 4, 5]]
        with self.assertRaises(ValueError):
            ac.AlgebraicOps.mul_mat_mat_like(A, B)

    def test_div_scalar_like(self) -> None:
        self.assertAlmostEqual(ac.AlgebraicOps.div_scalar_like(7, 2), 3.5)

    def test_div_vector_scalar_like(self) -> None:
        self.assertEqual(ac.AlgebraicOps.div_vector_scalar_like([2, 4], 2), [1, 2])

    def test_div_matrix_scalar_like(self) -> None:
        M = [[2, 4], [6, 8]]
        self.assertEqual(ac.AlgebraicOps.div_matrix_scalar_like(M, 2), [[1, 2], [3, 4]])


class TestT2AlgebraicAndRounding(unittest.TestCase):
    def test_T2Algebraic_scalar(self) -> None:
        s = ac.T2Algebraic(10)
        self.assertEqual(s.value, 10)
        self.assertEqual(type(s).__name__, "Scalar")

    def test_T2Algebraic_vector(self) -> None:
        v = ac.T2Algebraic([1, 2, 3])
        self.assertEqual(v.value, [1, 2, 3])
        self.assertEqual(type(v).__name__, "Vector")

    def test_T2Algebraic_matrix(self) -> None:
        M = ac.T2Algebraic([[1, 2], [3, 4]])
        self.assertEqual(M.value, [[1, 2], [3, 4]])
        self.assertEqual(type(M).__name__, "Matrix")

    def test_T2Algebraic_invalid(self) -> None:
        with self.assertRaises(TypeError):
            ac.T2Algebraic("not supported")  # tipo no válido

    def test_round_T_Scalar_real(self) -> None:
        self.assertEqual(ac.round_T_Scalar(3.14159, 3), 3.142)

    def test_round_T_Scalar_complex(self) -> None:
        z = 1.2345 + 6.789j
        rounded = ac.round_T_Scalar(z, 2)
        self.assertEqual(rounded.real, round(1.2345, 2))
        self.assertEqual(rounded.imag, round(6.789, 2))


if __name__ == "__main__":
    unittest.main()
