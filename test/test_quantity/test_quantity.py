import unittest
from pyhsics import Vector, Quantity


class TestQuantity(unittest.TestCase):

    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.q1 = Quantity(5, "m")      # Cantidad escalar
        self.q2 = Quantity(10, "s")     # Cantidad escalar con otra unidad
        self.q3 = Quantity(Vector([1, 2, 3]), "m")  # Cantidad vectorial

    def test_creation(self):
        """Prueba la creación de objetos Quantity"""
        self.assertEqual(self.q1.value, 5)
        self.assertEqual(str(self.q1.units), "m")
        self.assertEqual(str(self.q3.value), "(1, 2, 3)")

    def test_addition(self):
        """Prueba la suma de Quantity"""
        q4 = Quantity(3, "m")
        result = self.q1 + q4
        self.assertEqual(result.value, 8)
        self.assertEqual(str(result.units), "m")

        with self.assertRaises(ValueError):
            _ = self.q1 + self.q2  # No se pueden sumar diferentes unidades

    def test_multiplication(self):
        """Prueba la multiplicación de Quantity"""
        result = self.q1 * self.q2  # 5m * 10s = 50 m·s
        self.assertEqual(result.value, 50)
        self.assertEqual(str(result.units), "m·s")

    def test_division(self):
        """Prueba la división de Quantity"""
        result = self.q1 / self.q2  # 5m / 10s = 0.5 m/s
        self.assertEqual(result.value, 0.5)
        self.assertEqual(str(result.units), "m·s⁻¹")

    def test_power(self):
        """Prueba la exponenciación de Quantity"""
        result = self.q1 ** 2  # (5m)² = 25 m²
        self.assertEqual(result.value, 25)
        self.assertEqual(str(result.units), "m²")

        with self.assertRaises(ValueError):
            _ = self.q1 ** self.q2  # No se puede elevar a una unidad no adimensional

    def test_negation(self):
        """Prueba la negación de Quantity"""
        result = -self.q1
        self.assertEqual(result.value, -5)

    def test_absolute_value(self):
        """Prueba el valor absoluto de Quantity"""
        q_neg = Quantity(-10, "m")
        self.assertEqual(abs(q_neg).value, 10)

    def test_string_representation(self):
        """Prueba la representación en string de Quantity"""
        self.assertEqual(str(self.q1), "5 m")
        self.assertEqual(repr(self.q1), "ScalarQuantity(5 m)")

if __name__ == '__main__':
    unittest.main()
