import unittest
from pyhsics.units.unit import Unit
from pyhsics.units.prefixed_unit import PrefixedUnit
from pyhsics.units.fundamental_unit import FundamentalUnit


class TestUnit(unittest.TestCase):

    def setUp(self):
        """Configuración inicial para las pruebas."""
        # Crear una unidad de ejemplo
        self.unit_kg_m_s = "kg * m / s**2"
        self.unit_kg_m = "kg * m"
        self.unit_newton = "N = kg * m / s**2"
        
        # Inicializar unidades
        self.unit1 = Unit(self.unit_kg_m_s)
        self.unit2 = Unit(self.unit_kg_m)
        self.unit3 = Unit(self.unit_newton)

    def test_init(self):
        """Prueba la creación de una unidad a partir de una fórmula."""
        self.assertEqual(self.unit1.formula, "kg * m / s**2")
        self.assertEqual(self.unit1.composition.unit_dict, {FundamentalUnit.MASS: 1, FundamentalUnit.DISTANCE: 1, FundamentalUnit.TIME: -2})
        self.assertEqual(self.unit1.prefix, 1.0)
        self.assertEqual(self.unit1.alias, None)
        
    def test_alias_creation(self):
        """Verifica que se pueda asociar un alias a una unidad."""
        self.assertEqual(self.unit3.alias, "N")

    def test_from_prefixed_unit(self):
        """Prueba la creación de una unidad a partir de un PrefixedUnit."""
        prefixed_unit = PrefixedUnit(1e3, {FundamentalUnit.MASS: 1, FundamentalUnit.DISTANCE: 1})
        unit_from_prefixed = Unit.from_prefixed_unit(prefixed_unit)
        self.assertEqual(unit_from_prefixed.prefix, 1e3)
        self.assertEqual(unit_from_prefixed.formula, "kg·m")
        self.assertEqual(unit_from_prefixed.composition.unit_dict, {FundamentalUnit.MASS: 1, FundamentalUnit.DISTANCE: 1})

    def test_multiplication(self):
        """Prueba la multiplicación de unidades."""
        result = self.unit1 * self.unit2
        self.assertEqual(result.formula, "kg²·m²·s⁻²")
        self.assertEqual(result.prefix, 1.0)

    def test_division(self):
        """Prueba la división de unidades."""
        result = self.unit1 / self.unit2
        self.assertEqual(result.formula, "s⁻²")
        self.assertEqual(result.prefix, 1.0)

    def test_power(self):
        """Prueba la potenciación de una unidad."""
        result = self.unit1 ** 2
        self.assertEqual(result.formula, "kg²·m²·s⁻⁴")
        self.assertEqual(result.prefix, 1.0)

    def test_eq(self):
        """Verifica que dos unidades sean iguales."""
        unit1 = Unit(self.unit_kg_m_s)
        unit2 = Unit(self.unit_kg_m_s)
        self.assertTrue(unit1 == unit2)

    def test_ne(self):
        """Verifica que dos unidades sean diferentes."""
        unit1 = Unit(self.unit_kg_m_s)
        unit2 = Unit(self.unit_kg_m)
        self.assertTrue(unit1 != unit2)


if __name__ == '__main__':
    unittest.main()
