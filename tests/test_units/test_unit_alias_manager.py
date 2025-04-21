import unittest
from pyhsics.units.fundamental_unit import FundamentalUnit
from pyhsics.units.unit_composition import UnitComposition
from pyhsics.units.alias_manager import UnitAliasManager


class TestUnitAliasManager(unittest.TestCase):
    
    def setUp(self):
        """Configuración inicial para las pruebas."""
        # Definir algunas composiciones y alias
        self.unit_kg_m_s = UnitComposition({FundamentalUnit.MASS: 1, FundamentalUnit.DISTANCE: 1, FundamentalUnit.TIME: -2})
        self.unit_newton = "kg*m/s**2"  # Alias para newton
        self.unit_kg = {FundamentalUnit.MASS: 1}
        
        # Resetear los alias antes de cada prueba
        UnitAliasManager.reset(True)

    def test_add_alias(self):
        """Prueba la adición de un alias para una composición de unidades."""
        UnitAliasManager.add_alias(self.unit_newton, "N")
        alias = UnitAliasManager.get_alias(frozenset(self.unit_kg_m_s.unit_dict.items()))
        self.assertEqual(alias, "N")

    def test_add_multiple_aliases(self):
        """Prueba la adición de múltiples alias para una composición de unidades."""
        UnitAliasManager.add_aliases(self.unit_newton, ["Newton", "newton", "N"])
        alias = UnitAliasManager.get_alias(frozenset(self.unit_kg_m_s.unit_dict.items()))
        self.assertEqual(alias, "N")
    
    def test_get_units_dict(self):
        """Prueba que se recupere correctamente el diccionario de unidades de un alias."""
        UnitAliasManager.add_alias(self.unit_newton, "N")
        units_dict = UnitAliasManager.get_units_dict("N")
        self.assertEqual(units_dict, dict(self.unit_kg_m_s.unit_dict))

    def test_get_units_dict_non_existent(self):
        """Prueba que se lance una excepción cuando se intenta recuperar un alias no existente."""
        with self.assertRaises(KeyError):
            UnitAliasManager.get_units_dict("unknown")

    def test_reset(self):
        """Prueba que el reset de alias borre los alias previamente registrados."""
        UnitAliasManager.add_alias(self.unit_newton, "N")
        UnitAliasManager.reset(True)
        with self.assertRaises(KeyError):
            UnitAliasManager.get_units_dict("N")
    
    def test_repr(self):
        """Prueba la representación en cadena de los alias registrados."""
        UnitAliasManager.add_alias(self.unit_newton, "N")
        repr_str = repr(UnitAliasManager())
        self.assertIn("N ->", repr_str)

if __name__ == '__main__':
    unittest.main()
