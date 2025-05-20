# tests/test_linear_system.py

import unittest

from pyhsics.linalg.structures import Vector, Matrix
from pyhsics.linalg.solvers.linear_system import vector_to_integer_coords, LinearSystem


class TestVectorToIntegerCoords(unittest.TestCase):
    def test_all_reals(self) -> None:
        vec = [0.5, 2.25, 3.0]
        ints = vector_to_integer_coords(vec)
        # denominators: 2, 4, 1 -> lcm = 4
        # scaled: [0.5*4=2, 2.25*4=9, 3*4=12]
        self.assertEqual(ints, [2, 9, 12])

    def test_with_complex(self) -> None:
        # 1/2 + (3/4)i  and 2.0
        vec = [0.5 + 0.75j, 2.0]
        ints = vector_to_integer_coords(vec)
        # fractions: [1/2+3/4j, 2/1]
        # denominators: 2,1 -> lcm=2
        # first: (1/2)*2=1, (3/4)*2=1.5 -> but ComplexFraction makes exact 3/4 -> numerator=3+?j
        # Actually limit_denominator preserves denom 4 for imag, so denominators [2,4], lcm=4
        # then: (1/2)*4=2, (3/4)*4=3 -> [2,3], second: 2*4=8 -> [8]
        self.assertEqual(ints, [2, 3, 8])

    def test_mixed(self) -> None:
        vec = [1, 1/3, 2+1j]
        ints = vector_to_integer_coords(vec)
        # denominators: 1,3,1 -> lcm=3
        # 1*3=3; (1/3)*3=1; (2+1j)*3=(6+3j) -> [6,3]
        self.assertEqual(ints, [3, 1, 6, 3])


class TestLinearSystemSolve(unittest.TestCase):
    def test_unique_solution(self) -> None:
        A = Matrix.eye(3)
        b = Vector([1, 2, 3])
        sys = LinearSystem(A, b)
        sol = sys.solve()
        self.assertIsInstance(sol, Vector)
        self.assertEqual(sol.value, [1, 2, 3])

    def test_no_solution(self) -> None:
        # inconsistent: x = 1, x = 2
        A = Matrix([[1, 0, 0], [1, 0, 0], [0, 1, 0]])
        b = Vector([1, 2, 0])
        sys = LinearSystem(A, b)
        sol = sys.solve()
        self.assertIsNone(sol)

    def test_infinite_solutions(self) -> None:
        # rank 2 < 3 vars
        A = Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 0]])
        b = Vector([0, 0, 0])
        sys = LinearSystem(A, b)
        sols = sys.solve()
        self.assertIsInstance(sols, list)
        # There should be exactly one free variable direction for free_col=2
        # direction vector integer coords: free_col=2 -> x2=1, pivots zero => [0,0,1]
        expected = {tuple(v.value) for v in sols}
        self.assertIn((0, 0, 1), expected)

    def test_parse_equations_and_repr(self) -> None:
        eqs = ["2*x + 3*y + z = 5", "x - y + 2*z = 4", "z = 1"]
        sys = LinearSystem.parse_equations(eqs)
        # Check shape
        self.assertEqual(sys.shape, (3, 3))
        # Solve should give unique solution [x,y,z] = ?
        sol = sys.solve()
        self.assertIsInstance(sol, Vector)
        # From z=1, second: x - y + 2*1 = 4 -> x - y = 2
        # first: 2x + 3y + 1 = 5 -> 2x + 3y = 4
        # Solve: from x = y + 2, substitute: 2(y+2) + 3y =4 -> 2y+4+3y=4 ->5y=0 -> y=0, x=2
        self.assertEqual(sol.value, [2.0, 0.0, 1.0])

        # Test LaTeX repr for different modes
        sys.repr_mode = "LES"
        tex_les = sys._repr_latex_()
        self.assertIn(r"\begin{aligned}", tex_les)
        self.assertIn("2.0x_{1}", tex_les)

        sys.repr_mode = "AM"
        tex_am = sys._repr_latex_()
        self.assertIn(r"\left(", tex_am)
        self.assertIn("& 5", tex_am)  # augmented last column

        sys.repr_mode = "A"
        tex_ans = sys._repr_latex_()
        self.assertIn("x_{1} = ", tex_ans)
        self.assertIn("= 2.0", tex_ans)


if __name__ == "__main__":
    unittest.main()
