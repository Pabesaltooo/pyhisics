from typing import Any
import unittest
import ast

from pyhsics.linalg.structures.scalar import Scalar
from pyhsics.linalg.structures.vector import Vector
from pyhsics.quantity.quantities import quantities, parse_scalar, parse_vector
from pyhsics.quantity.core_quantity import Quantity
from pyhsics.quantity.scalar_quantity import ScalarQuantity
from pyhsics.quantity.vector_quantity import VectorQuantity
from pyhsics.units.unit import Unit  # Asegúrate de que Unit esté disponible en este módulo


class TestParseScalar(unittest.TestCase):
    def test_parse_scalar_valid(self):
        """Comprobar que parse_scalar convierte cadenas válidas a float."""
        self.assertAlmostEqual(parse_scalar(ScalarQuantity, "3.14"), 3.14)
        self.assertAlmostEqual(parse_scalar(Quantity, "0"), 0.0)
        self.assertAlmostEqual(parse_scalar(ScalarQuantity, "-2.5e1"), -25.0)

    def test_parse_scalar_invalid(self):
        """parse_scalar debe lanzar ValueError si la cadena no es un número."""
        with self.assertRaises(ValueError) as ctx:
            parse_scalar(ScalarQuantity, "abc")
        self.assertIn("Valor escalar inválido", str(ctx.exception))

        # Si se usa cls=VectorQuantity, aunque la cadena sea numérica, debe saltar error
        with self.assertRaises(ValueError) as ctx2:
            parse_scalar(VectorQuantity, "5")
        self.assertIn("No se puede crear VectorQuantity a partir de un valor escalar", str(ctx2.exception))


class TestParseVector(unittest.TestCase):
    def test_parse_vector_valid(self):
        """Comprobar que parse_vector convierte correctamente listas y tuplas a lista de floats."""
        # Lista de enteros
        vec = parse_vector(Quantity, "[1, 2, 3]")
        self.assertIsInstance(vec, list)
        self.assertEqual(vec, [1.0, 2.0, 3.0])

        # Lista mixta de ints/floats
        vec2 = parse_vector(VectorQuantity, "[0.5, -1, 4.2]")
        self.assertEqual(vec2, [0.5, -1.0, 4.2])

        # Tupla de valores
        vec3 = parse_vector(Quantity, "(7, 0)")
        self.assertEqual(vec3, [7.0, 0.0])

    def test_parse_vector_invalid_syntax(self):
        """parse_vector debe lanzar ValueError ante sintaxis inválida o contenido no numérico."""
        with self.assertRaises(ValueError) as ctx:
            parse_vector(Quantity, "[1, a, 3]")
        self.assertIn("Valor vectorial inválido", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx2:
            parse_vector(Quantity, "not_a_list")
        self.assertIn("Valor vectorial inválido", str(ctx2.exception))

        # Si se usa cls=ScalarQuantity con vector, lanza ValueError
        with self.assertRaises(ValueError) as ctx3:
            parse_vector(ScalarQuantity, "[1,2,3]")
        self.assertIn("No se puede crear ScalarQuantity a partir de un valor vectorial", str(ctx3.exception))


class TestQuantitiesBasic(unittest.TestCase):
    def test_single_scalar_with_unit(self):
        """Con la implementación actual, default cls es ScalarQuantity."""
        iterable = quantities("10 kg")
        results = list(iterable)
        self.assertEqual(len(results), 1)
        q = results[0]
        self.assertIsInstance(q, ScalarQuantity)
        self.assertAlmostEqual(q.value, 10.0)
        self.assertEqual(q.units, Unit("kg"))

    def test_single_scalar_no_unit(self):
        """Verificar que si no se proporciona unidad, se crea ScalarQuantity adimensional."""
        iterable = quantities("7.5")
        results = list(iterable)
        self.assertEqual(len(results), 1)
        q = results[0]
        self.assertIsInstance(q, ScalarQuantity)
        self.assertAlmostEqual(q.value, 7.5)
        # Comparamos contra el Unit vacío (adimensional)
        self.assertEqual(q.units, Unit('1'))

    def test_single_vector_default_cls_error(self):
        """Con default cls=ScalarQuantity, pasar un vector debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            list(quantities("[1,2,3] m/s"))
        self.assertIn("No se puede crear ScalarQuantity a partir de un valor vectorial", str(ctx.exception))


class TestQuantitiesWithQuantityCls(unittest.TestCase):
    def test_multiple_scalars_and_vectors_mixed(self):
        """Usar cls=Quantity: debe asignar subclase correcta a cada elemento."""
        iterable = quantities("5, [2,4] km, 3.0 m", cls=Quantity[Any])
        results = list(iterable)
        self.assertEqual(len(results), 3)

        # Primer elemento: escalar sin unidad
        q1 = results[0]
        self.assertIsInstance(q1, ScalarQuantity)
        self.assertAlmostEqual(q1.value, 5.0)
        self.assertEqual(q1.units, Unit('1'))

        # Segundo elemento: vector con unidad
        q2 = results[1]
        self.assertIsInstance(q2, VectorQuantity)
        self.assertEqual(q2.value, Vector([2000, 4000]))
        self.assertEqual(q2.units, Unit("m"))

        # Tercer elemento: escalar con unidad
        q3 = results[2]
        self.assertIsInstance(q3, ScalarQuantity)
        self.assertAlmostEqual(q3.value, 3.0)
        self.assertEqual(q3.units, Unit("m"))

    def test_multiple_with_forced_scalarquantity(self):
        """Forzar cls=ScalarQuantity en múltiples escalares y reprobar vectores."""
        # Todos escalares
        iterable = quantities("1, 2.2 kg, 3.5", cls=ScalarQuantity)
        results = list(iterable)
        self.assertTrue(all(isinstance(x, ScalarQuantity) for x in results))
        self.assertAlmostEqual(results[0].value, 1.0)
        self.assertEqual(results[0].units, Unit('1'))
        self.assertAlmostEqual(results[1].value, 2.2)
        self.assertEqual(results[1].units, Unit("kg"))
        self.assertAlmostEqual(results[2].value, 3.5)
        self.assertEqual(results[2].units, Unit('1'))

        # Si uno de ellos es vector, salta ValueError al encontrarlo
        with self.assertRaises(ValueError) as ctx:
            list(quantities("1, [0,1] m", cls=ScalarQuantity))
        self.assertIn("No se puede crear ScalarQuantity a partir de un valor vectorial", str(ctx.exception))

    def test_multiple_with_forced_vectorquantity(self):
        """Forzar cls=VectorQuantity en múltiples vectores y reprobar escalares."""
        # Todos vectores
        iterable = quantities("[1,2] m, [3,4] kg", cls=VectorQuantity)
        results = list(iterable)
        self.assertTrue(all(isinstance(x, VectorQuantity) for x in results))
        self.assertEqual(results[0].value, Vector([1.0, 2.0]))
        self.assertEqual(results[0].units, Unit("m"))
        self.assertEqual(results[1].value, Vector([3.0, 4.0]))
        self.assertEqual(results[1].units, Unit("kg"))

        # Si hay un escalar, salta ValueError al encontrarlo
        with self.assertRaises(ValueError) as ctx:
            list(quantities("5 m, [1,2] s", cls=VectorQuantity))
        self.assertIn("No se puede crear VectorQuantity a partir de un valor escalar", str(ctx.exception))


class TestQuantitiesWhitespaceAndEdgeCases(unittest.TestCase):
    def test_whitespace_and_empty_tokens(self):
        """Elementos vacíos o con espacios deben ser ignorados."""
        iterable = quantities(" ,  8 m , , 9 , ")
        results = list(iterable)
        self.assertEqual(len(results), 2)

        # Primer elemento: escalar con unidad
        q1 = results[0]
        self.assertIsInstance(q1, ScalarQuantity)
        self.assertAlmostEqual(q1.value, 8.0)
        self.assertEqual(q1.units, Unit("m"))

        # Segundo elemento: escalar sin unidad
        q2 = results[1]
        self.assertIsInstance(q2, ScalarQuantity)
        self.assertAlmostEqual(q2.value, 9.0)
        self.assertEqual(q2.units, Unit('1'))

    def test_zero_and_negative_values(self):
        """Comprobar correctamente valores 0 y negativos en escalares y vectores."""
        iterable = quantities("0 kg, -5, [0,-1,2] m", cls=Quantity[Any])
        results = list(iterable)

        # 0 con unidad
        self.assertIsInstance(results[0], ScalarQuantity)
        self.assertAlmostEqual(results[0].value, 0.0)
        self.assertEqual(results[0].units, Unit("kg"))

        # -5 sin unidad
        self.assertIsInstance(results[1], ScalarQuantity)
        self.assertAlmostEqual(results[1].value, -5.0)
        self.assertEqual(results[1].units, Unit("1"))

        # Vector con ceros y negativos
        self.assertIsInstance(results[2], VectorQuantity)
        self.assertEqual(results[2].value, Vector([0.0, -1.0, 2.0]))
        self.assertEqual(results[2].units, Unit("m"))

    def test_large_and_scientific_notation(self):
        """Comprobar notación científica y valores grandes."""
        iterable = quantities("1e3 km, [1e2,2e2,3e2] m", cls=Quantity[Any])
        results = list(iterable)

        # Primer elemento: escalar con unidad
        self.assertIsInstance(results[0], ScalarQuantity)
        self.assertAlmostEqual(results[0].value, Scalar(1e6))
        self.assertEqual(results[0].units, Unit("m"))

        # Segundo elemento: vector
        self.assertIsInstance(results[1], VectorQuantity)
        self.assertEqual(results[1].value, Vector([1e2, 2e2, 3e2]))
        self.assertEqual(results[1].units, Unit("m"))

    def test_only_commas_returns_empty_iterator(self):
        """Si la cadena solo tiene comas y espacios, debe devolver iterator vacío."""
        iterable = quantities(" , , ")
        results = list(iterable)
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
