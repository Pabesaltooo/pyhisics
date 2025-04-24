import unittest

from pyhsics.linalg.matrix import Matrix
from pyhsics.linalg.vector import Vector


def mat_almost_equal(tc: unittest.TestCase,
                     A: Matrix, B: Matrix, places: int = 9):
    tc.assertEqual(A.shape, B.shape)
    for r in range(A.shape[0]):
        for c in range(A.shape[1]):
            tc.assertAlmostEqual(A.value[r][c], B.value[r][c], places=places)


class TestMatrix(unittest.TestCase):
    # ---------- aritmética básica --------------------------------------
    def test_basic_ops_real(self):
        A = Matrix([[1, 2], [3, 4]])
        B = Matrix([[5, 6], [7, 8]])
        mat_almost_equal(self, A + B, Matrix([[6, 8], [10, 12]]))
        mat_almost_equal(self, A * 2, Matrix([[2, 4], [6, 8]]))
        mat_almost_equal(self, 2 * A, Matrix([[2, 4], [6, 8]]))
        mat_almost_equal(self, A / 2, Matrix([[0.5, 1], [1.5, 2]]))

    def test_basic_ops_complex(self):
        A = Matrix([[1 + 1j, 2], [0, 3 - 1j]])
        mat_almost_equal(self, A * (1 - 1j),
                         Matrix([[(1 + 1j) * (1 - 1j), 2 * (1 - 1j)],
                                 [0, (3 - 1j) * (1 - 1j)]]))

    # ---------- multiplicación por vector / matriz ---------------------
    def test_matrix_vector_mul(self):
        M = Matrix([[1, 2, 3], [4, 5, 6]])
        v = Vector([1, 0, 1])
        self.assertEqual(M * v, Vector([4, 10]))

    def test_matrix_matrix_mul(self):
        A = Matrix([[1, 2], [3, 4]])
        B = Matrix([[2, 0], [1, 2]])
        mat_almost_equal(self, A * B, Matrix([[4, 4], [10, 8]]))

    # ---------- determinante, rango, inversa ---------------------------
    def test_det_rank_inv(self):
        M = Matrix([[4, 7], [2, 6]])      # det = 10
        self.assertEqual(M.det().value, 10)
        self.assertEqual(M.rank(), 2)
        Minv = M.inv()
        mat_almost_equal(self, M * Minv, Matrix.eye(2))
        mat_almost_equal(self, Minv * M, Matrix.eye(2))

    # ---------- caché REF / RREF ---------------------------------------
    def test_cached_ref_rref(self):
        M = Matrix([[1, 2], [3, 4]])
        ref1 = M.row_echelon_form()
        ref2 = M.row_echelon_form()
        self.assertIs(ref1, ref2)     # misma instancia (cached_property)

        rref1 = M.reduced_row_echelon_form()
        rref2 = M.reduced_row_echelon_form()
        self.assertIs(rref1, rref2)

    # ---------- propiedades booleanas ----------------------------------
    def test_orthogonal_symmetric(self):
        Q = Matrix([[0, 1], [-1, 0]])      # rotación 90°
        S = Matrix([[2, 1], [1, 2]])
        self.assertTrue(Q.is_orthogonal)
        self.assertTrue(S.is_symmetric)
        self.assertFalse(Q.is_symmetric)
        self.assertFalse(S.is_orthogonal)


if __name__ == "__main__":
    unittest.main()
