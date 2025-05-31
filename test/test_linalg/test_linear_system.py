# tests/test_linear_system.py

import unittest
import re

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



class TestLinearSystemPrinter(unittest.TestCase):
    def setUp(self):
        # Un sistema sencillo para tests genéricos
        self.A = Matrix([[1, 2], [3, 4]])
        self.b = Vector([5, 6])
        self.sys = LinearSystem(self.A, self.b)

    def test_repr_latex_default_and_name(self):
        # Modo ANSW por defecto
        self.sys.set_repr_mode('ANSW')
        tex = self.sys.latex()
        # Debe contener el entorno cases
        self.assertIn(r"\begin{cases}", tex)
        self.assertIn(r"\end{cases}", tex)


    def test_invalid_mode_raises(self):
        with self.assertRaises(ValueError):
            self.sys.set_repr_mode('NO-MODE') # type: ignore
            self.sys.latex()

    def test_as_augmented_matrix(self):
        A = Matrix([[1, 0], [0, 1]])
        b = Vector([7, 8])
        sys = LinearSystem(A, b)
        sys.set_repr_mode('AUG-MAT')
        tex = sys.latex()
        # columnas "cc|c"
        self.assertIn(r"{cc|c}", tex)
        # filas correctamente formadas
        self.assertIn("1 & 0 & 7", tex)
        self.assertIn("0 & 1 & 8", tex)
        # delimitadores de array
        self.assertIn(r"\left(", tex)
        self.assertIn(r"\end{array}\right)", tex)

    def test_as_matrix_system(self):
        A = Matrix([[2, 3]])
        b = Vector([4])
        sys = LinearSystem(A, b)
        sys.set_repr_mode('MAT-SYS')
        tex = sys.latex()
        # Debe usar pmatrix y el igual
        self.assertIn(r"\begin{pmatrix}", tex)
        self.assertIn(r"\end{pmatrix}", tex)
        self.assertIn("=", tex)
        # Debe aparecer coeficientes y constante
        self.assertIn("2", tex)
        self.assertIn("3", tex)
        self.assertIn("4", tex)

    def test_as_linear_equations(self):
        eqs = ["x + 2*y = 3", "y = 4"]
        sys = LinearSystem.parse_equations(eqs)
        sys.set_repr_mode("LES")
        tex = sys.latex()
        # Entorno aligned
        self.assertTrue(tex.startswith(r"\begin{aligned}"))
        self.assertTrue(tex.endswith(r"\end{aligned}"))
        # x₁ y x₂, términos y ecuaciones
        self.assertTrue(re.search(r"x_\{1\}", tex))
        self.assertTrue(re.search(r"x_\{2\}", tex))
        # 2·y debe salir como 2x_{2}
        self.assertIsNotNone(re.search(r"2x_\{2\}", tex))
        # comprobar igualdad y constantes
        self.assertIn("= & 3", tex)
        self.assertIn("= & 4", tex)


    def test_as_solutions_unique_and_empty(self):
        # Única solución
        eqs1 = ["x = 2", "y = 3"]
        sys1 = LinearSystem.parse_equations(eqs1)
        sys1.set_repr_mode("ANSW")
        sol_tex = sys1.latex()
        self.assertTrue(sol_tex.startswith(r"\begin{cases}"))
        self.assertTrue(sol_tex.endswith(r"\end{cases}"))
        self.assertIn("x_{1} = 2", sol_tex)
        self.assertIn("x_{2} = 3", sol_tex)

        # Sin solución: sistema incompatible
        eqs2 = ["x = 1", "x = 2"]
        sys2 = LinearSystem.parse_equations(eqs2)
        sol2 = sys2.solve()
        # solve() devuelve None
        self.assertIsNone(sol2)
        # _as_solutions debe producir vacío
        empty_tex = sys2.latex()
        self.assertEqual(empty_tex, r"\emptyset")

    def test_parametric_solution(self):
        # Sistema con infinitas soluciones: x + y = 0
        eqs = ["x + y = 0"]
        sys = LinearSystem.parse_equations(eqs)
        sys.set_repr_mode('PARAM')
        tex = sys.latex()
        # Debe contener \mathbb{R}^{2} y \displaystyle
        self.assertIn(r"\mathbb{R}^{2}", tex)
        self.assertIn(r"\displaystyle", tex)

if __name__ == "__main__":
    unittest.main()
