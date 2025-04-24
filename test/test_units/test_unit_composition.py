import unittest
from pyhsics.units.fundamental_unit import FundamentalUnit
from pyhsics.units.unit_composition import UnitComposition
from pyhsics.units.basic_typing import UnitDict

class TestUnitComposition(unittest.TestCase):

    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.unit_kg: UnitDict = {FundamentalUnit.MASS: 1}
        self.unit_m: UnitDict = {FundamentalUnit.DISTANCE: 1}
        self.unit_s: UnitDict = {FundamentalUnit.TIME: 1}
        
        self.unit_kg_m: UnitDict = {FundamentalUnit.MASS: 1, FundamentalUnit.DISTANCE: 1}
        self.unit_kg_s: UnitDict = {FundamentalUnit.MASS: 1, FundamentalUnit.TIME: 1}
        self.unit_m_s: UnitDict = {FundamentalUnit.DISTANCE: 1, FundamentalUnit.TIME: 1}
    
    def test_init(self):
        """Prueba la creación de UnitComposition."""
        unit_com = UnitComposition(self.unit_kg)
        self.assertEqual(unit_com.unit_dict, {FundamentalUnit.MASS: 1})

    def test_mul(self):
        """Prueba la multiplicación de composiciones de unidades."""
        unit_com_kg_m = UnitComposition(self.unit_kg_m)
        unit_com_kg_s = UnitComposition(self.unit_kg_s)
        result = unit_com_kg_m * unit_com_kg_s
        self.assertEqual(result.unit_dict, {FundamentalUnit.MASS: 2, FundamentalUnit.DISTANCE: 1, FundamentalUnit.TIME: 1})

    def test_div(self):
        """Prueba la división de composiciones de unidades."""
        unit_com_kg_m = UnitComposition(self.unit_kg_m)
        unit_com_m_s = UnitComposition(self.unit_m_s)
        result = unit_com_kg_m / unit_com_m_s
        self.assertEqual(result.unit_dict, {FundamentalUnit.MASS: 1, FundamentalUnit.TIME: -1})

    def test_pow(self):
        """Prueba la potenciación de composiciones de unidades."""
        unit_com_kg_m = UnitComposition(self.unit_kg_m)
        result = unit_com_kg_m ** 2
        self.assertEqual(result.unit_dict, {FundamentalUnit.MASS: 2, FundamentalUnit.DISTANCE: 2})

    def test_clean(self):
        """Prueba la limpieza de unidades con exponente 0."""
        unit_com_kg_m_s = UnitComposition(self.unit_kg_m)
        unit_com_kg_m_s.unit_dict[FundamentalUnit.DISTANCE] = 0
        cleaned_unit = unit_com_kg_m_s._clean()
        self.assertEqual(cleaned_unit.unit_dict, {FundamentalUnit.MASS: 1})

    def test_eq(self):
        """Prueba la comparación de composiciones de unidades."""
        unit_com_kg_m = UnitComposition(self.unit_kg_m)
        unit_com_kg_m_copy = UnitComposition(self.unit_kg_m)
        unit_com_kg_s = UnitComposition(self.unit_kg_s)
        self.assertTrue(unit_com_kg_m == unit_com_kg_m_copy)
        self.assertFalse(unit_com_kg_m == unit_com_kg_s)

    def test_str(self):
        """Prueba la representación en cadena de las composiciones de unidades."""
        unit_com_kg_m = UnitComposition(self.unit_kg_m)
        self.assertEqual(str(unit_com_kg_m), "kg·m")

    def test_from_str(self):
        """Prueba la creación de UnitComposition a partir de una cadena."""
        unit_com = UnitComposition.from_str("kg*m/s**2")
        self.assertEqual(unit_com.unit_dict, {FundamentalUnit.MASS: 1, FundamentalUnit.DISTANCE: 1, FundamentalUnit.TIME: -2})

if __name__ == '__main__':
    unittest.main()
