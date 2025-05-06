import unittest
from pyhsics.units.fundamental_unit import FundamentalUnit
from pyhsics.units.prefixed_unit import PrefixedUnit
from pyhsics.units.unit_composition import UnitComposition

class TestPrefixedUnit(unittest.TestCase):

    def setUp(self):
        """Configuración inicial para las pruebas."""
        # Unidades base
        self.unit_kg = UnitComposition({FundamentalUnit.MASS: 1})
        self.unit_m = UnitComposition({FundamentalUnit.DISTANCE: 1})
        self.unit_s = UnitComposition({FundamentalUnit.TIME: 1})
        
        # PrefixedUnit: unidad con prefijo
        self.unit_km = PrefixedUnit(1e3, self.unit_m)  # km = 1000 * m
        self.unit_mm = PrefixedUnit(1e-3, self.unit_m)  # mm = 0.001 * m

    def test_init(self):
        """Prueba la creación de PrefixedUnit."""
        unit_com = PrefixedUnit(1e3, self.unit_kg)
        self.assertEqual(unit_com.prefix, 1e3)
        self.assertEqual(unit_com, self.unit_kg)

    def test_str(self):
        """Prueba la representación en cadena de PrefixedUnit."""
        unit_com = PrefixedUnit(1e3, self.unit_kg)
        self.assertEqual(str(unit_com), "1000.0 kg")

    def test_simplify(self):
        """Prueba la simplificación de PrefixedUnit a UnitComposition."""
        unit_com = PrefixedUnit(1.0, self.unit_kg)
        simplified = unit_com.simplify()
        self.assertIsInstance(simplified, UnitComposition)
        self.assertEqual(simplified, self.unit_kg)

    def test_mul(self):
        """Prueba la multiplicación de dos PrefixedUnit."""
        unit_com_kg = PrefixedUnit(1e3, self.unit_kg)
        unit_com_s = PrefixedUnit(1, self.unit_s)
        result = unit_com_kg * unit_com_s
        self.assertEqual(result.prefix, 1e3)
        self.assertEqual(result.unit_dict, {FundamentalUnit.MASS: 1, FundamentalUnit.TIME: 1})

    def test_div(self):
        """Prueba la división de dos PrefixedUnit."""
        unit_com_kg = PrefixedUnit(1e3, self.unit_kg)
        unit_com_m = PrefixedUnit(1, self.unit_m)
        result = unit_com_kg / unit_com_m
        self.assertEqual(result.prefix, 1e3)
        self.assertEqual(result.unit_dict, {FundamentalUnit.MASS: 1, FundamentalUnit.DISTANCE: -1})

    def test_pow(self):
        """Prueba la potenciación de PrefixedUnit."""
        unit_com_kg = PrefixedUnit(1e3, self.unit_kg)
        result = unit_com_kg ** 2
        self.assertEqual(result.prefix, 1e6)
        self.assertEqual(result.unit_dict, {FundamentalUnit.MASS: 2})

    def test_iter(self):
        """Prueba la iteración de PrefixedUnit."""
        unit_com = PrefixedUnit(1e3, self.unit_kg)
        prefix, units = tuple(unit_com)
        self.assertEqual(prefix, 1e3)
        self.assertEqual(units, self.unit_kg.unit_dict)

if __name__ == '__main__':
    unittest.main()
