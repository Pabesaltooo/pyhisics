# tests/test_matrix.py
import unittest

from pyhsics.linalg.structures import Scalar, Vector, Point, Matrix

class TestMatrixInitialization(unittest.TestCase):
    def test_init_and_shape(self) -> None:
        M = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        self.assertEqual(M.shape, (3, 3))
        self.assertEqual(len(M), 3)  # número de filas
        self.assertEqual([row for row in M], [[1, 2, 3], [4, 5, 6], [7, 8, 9]])

    def test_empty_init_error(self) -> None:
        with self.assertRaises(ValueError):
            Matrix([])

    def test_non_rectangular_error(self) -> None:
        with self.assertRaises(ValueError):
            Matrix([[1, 2], [3, 4, 5]])


class TestMatrixBasicProperties(unittest.TestCase):
    def setUp(self) -> None:
        self.M = Matrix([[1, 0, 2], [0, 1, 3], [4, 5, 6]])
        self.I3 = Matrix.eye(3)

    def test_is_zero_and_identity(self) -> None:
        zero = Matrix([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        self.assertTrue(zero.is_zero())
        self.assertFalse(self.M.is_zero())
        self.assertTrue(self.I3.is_identity())
        self.assertFalse(self.M.is_identity())

    def test_hash_and_eq(self) -> None:
        A = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        B = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        self.assertEqual(A, B)
        self.assertEqual(hash(A), hash(B))
        C = Matrix([[9, 8, 7], [6, 5, 4], [3, 2, 1]])
        self.assertNotEqual(A, C)


class TestMatrixArithmetic(unittest.TestCase):
    def setUp(self) -> None:
        self.A = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        self.B = Matrix([[9, 8, 7], [6, 5, 4], [3, 2, 1]])
        self.v = Vector([1, 2, 3])
        self.s = Scalar(2)

    def test_add_and_neg(self) -> None:
        C = self.A + self.B
        self.assertIsInstance(C, Matrix)
        self.assertEqual(C.value, [
            [10, 10, 10],
            [10, 10, 10],
            [10, 10, 10],
        ])
        self.assertEqual((-self.A).value, [[-1, -2, -3], [-4, -5, -6], [-7, -8, -9]])

    def test_add_shape_mismatch(self) -> None:
        with self.assertRaises(ValueError):
            _ = self.A + Matrix([[1, 2], [3, 4]])  # 2x2 no coincide

    def test_mul_scalar(self) -> None:
        C = self.A * 3
        self.assertEqual(C.value, [[3, 6, 9], [12, 15, 18], [21, 24, 27]])
        D = self.A * self.s
        self.assertEqual(D.value, [[2, 4, 6], [8, 10, 12], [14, 16, 18]])
        E = 4 * self.A
        self.assertEqual(E.value, [[4, 8, 12], [16, 20, 24], [28, 32, 36]])

    def test_mul_vector(self) -> None:
        # A * v
        result = self.A * self.v
        self.assertIsInstance(result, Vector)
        # cálculo: [1*1+2*2+3*3, 4*1+5*2+6*3, 7*1+8*2+9*3]
        self.assertEqual(result.value, [14, 32, 50])

    def test_mul_matrix(self) -> None:
        C = self.A * self.B
        self.assertIsInstance(C, Matrix)
        # comparación con producto manual
        expected = Matrix([[1*9+2*6+3*3, 1*8+2*5+3*2, 1*7+2*4+3*1],
                           [4*9+5*6+6*3, 4*8+5*5+6*2, 4*7+5*4+6*1],
                           [7*9+8*6+9*3, 7*8+8*5+9*2, 7*7+8*4+9*1]])
        self.assertEqual(C, expected)

    def test_mul_point(self) -> None:
        p = Point([1, 2, 3])
        result = self.A * p
        self.assertIsInstance(result, Point)
        self.assertEqual(result.value, [14, 32, 50])

    def test_div_scalar(self) -> None:
        C = self.A / 2
        self.assertEqual(C.value, [[0.5, 1, 1.5], [2, 2.5, 3], [3.5, 4, 4.5]])
        with self.assertRaises(TypeError):
            _ = self.A / self.v  # solo escalar

    def test_transpose(self) -> None:
        At = self.A.T
        self.assertEqual(At.value, [[1, 4, 7], [2, 5, 8], [3, 6, 9]])


class TestMatrixRowEchelonAndRank(unittest.TestCase):
    def setUp(self) -> None:
        # una matriz de rango 3
        self.M = Matrix([[2, 4, 1], [6, 9, 5], [3, 7, 8]])

    def test_row_echelon_form(self) -> None:
        ref = self.M.row_echelon_form()
        # comprueba que esté triangular: elementos debajo de diagonal son ceros (aprox)
        for i in range(3):
            for j in range(i):
                self.assertAlmostEqual(ref.value[i][j], 0.0, places=6)

    def test_reduced_row_echelon_form(self) -> None:
        rref = self.M.reduced_row_echelon_form()
        # la forma reducida debe tener 1s en la diagonal
        diag = [rref.value[i][i] for i in range(3)]
        self.assertTrue(all(abs(d - 1.0) < 1e-6 for d in diag))

    def test_rank(self) -> None:
        self.assertEqual(self.M.rank(), 3)
        # hacer dos filas colineales
        M2 = Matrix([[1, 2, 3], [2, 4, 6], [3, 5, 7]])
        self.assertEqual(M2.rank(), 2)


class TestMatrixDeterminantInverseTrace(unittest.TestCase):
    def setUp(self) -> None:
        self.M = Matrix([[4, 7, 2], [3, 6, 1], [2, 5, 9]])
        self.I = Matrix.eye(3)

    def test_det(self) -> None:
        det = self.M.det()
        self.assertIsInstance(det, Scalar)
        # cálculo manual: 4*(6*9-1*5) -7*(3*9-1*2)+2*(3*5-6*2) = 4*49 -7*25 +2*3 = 196-175+6 = 27
        self.assertEqual(det.value, 27)

    def test_trace_and_is_squared(self) -> None:
        self.assertTrue(self.M.is_squared)
        self.assertEqual(self.M.trace.value, 4 + 6 + 9)

    def test_inverse(self) -> None:
        inv = self.M.inv()
        self.assertIsInstance(inv, Matrix)
        # M * M.inv() ≈ I
        prod = self.M * inv
        for i in range(3):
            for j in range(3):
                expected = 1.0 if i == j else 0.0
                self.assertAlmostEqual(prod.value[i][j], expected, places=6)

    def test_inverse_non_invertible(self) -> None:
        singular = Matrix([[1, 2, 3], [2, 4, 6], [3, 6, 9]])
        with self.assertRaises(ValueError):
            singular.inv()


class TestMatrixMiscellaneous(unittest.TestCase):
    def setUp(self) -> None:
        self.M = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

    def test_eye(self) -> None:
        I3 = Matrix.eye(3)
        self.assertTrue(I3.is_identity())

    def test_round(self) -> None:
        M = Matrix([[1.2345, 6.789, 9.1011],
                    [2.3456, 7.8910, 1.1213],
                    [3.4567, 8.9101, 2.1314]])
        Mr = round(M, 2)
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(Mr.value[i][j], round(M.value[i][j], 2))

    def test_is_symmetric_and_orthogonal(self) -> None:
        sym = Matrix([[1, 2, 3], [2, 5, 6], [3, 6, 9]])
        self.assertTrue(sym.is_symmetric)
        self.assertFalse(self.M.is_symmetric)
        # prueba ortogonal con una matriz de rotación 90° en R² embedida en 3×3
        R = Matrix([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
        self.assertTrue(R.is_orthogonal)
        self.assertFalse(self.M.is_orthogonal)

    def test_minor_and_adjoint(self) -> None:
        M = Matrix([[2, 3, 4], [1, 5, 6], [7, 8, 9]])
        minor_0_0 = M.minor(0, 0)
        # elimina fila 0 y columna 0 → [[5,6],[8,9]]
        self.assertEqual(minor_0_0.value, [[5, 6], [8, 9]])
        adj = M.adjoint()
        # adj[0][0] = det(minor_0_0) = 5*9 -6*8 = 45 -48 = -3
        self.assertAlmostEqual(adj.value[0][0], -3)

    def test_from_vecs_and_hvstack_vstack(self) -> None:
        v1 = Vector([1, 2, 3])
        v2 = Vector([4, 5, 6])
        M = Matrix.from_vecs([v1, v2])  # columnas v1, v2 → 3×2
        self.assertEqual(M.shape, (3, 2))
        # hstack: 3×2 con 3×2 → 3×4
        H = M.hstack(M)
        self.assertEqual(H.shape, (3, 4))
        # vstack: 3×2 con 3×2 → 6×2
        V = M.vstack(M)
        self.assertEqual(V.shape, (6, 2))


if __name__ == "__main__":
    unittest.main()
