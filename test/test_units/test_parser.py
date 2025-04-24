import unittest
from pyhsics.units.parser import UnitParser, UnitParseError, alias_resolver
from pyhsics.units.fundamental_unit import FundamentalUnit
from pyhsics.units.prefixed_unit import PrefixedUnit


class TestUnitParser(unittest.TestCase):
    
    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.mapping = {unit.value: unit for unit in FundamentalUnit}
        self.alias_resolver = alias_resolver  # Resolver de alias

    def test_valid_expression(self):
        """Prueba expresiones válidas con prefijos y operaciones."""
        text = "kg * m/s**2"
        parser = UnitParser(text, self.mapping, self.alias_resolver)
        result = parser.parse()
        self.assertIsInstance(result, PrefixedUnit)
        
    def test_valid_complex_expression(self):
        """Prueba expresiones complejas con varios operadores."""
        text = "C**2 * s**4 * kg **-1 * m ** -3"
        parser = UnitParser(text, self.mapping, self.alias_resolver)
        result = parser.parse()
        self.assertIsInstance(result, PrefixedUnit)

    def test_invalid_expression(self):
        """Prueba una expresión inválida que debería lanzar un error."""
        text = "kg * / m"
        parser = UnitParser(text, self.mapping, self.alias_resolver)
        with self.assertRaises(UnitParseError):
            parser.parse()

    def test_invalid_token(self):
        """Prueba un token inesperado en la expresión."""
        text = "kg * @@"
        parser = UnitParser(text, self.mapping, self.alias_resolver)
        with self.assertRaises(UnitParseError):
            parser.parse()

    def test_prefixed_unit(self):
        """Prueba la resolución de unidades con prefijos."""
        text = "km * s"
        parser = UnitParser(text, self.mapping, self.alias_resolver)
        result = parser.parse()
        self.assertEqual(result.prefix, 1e3)  # Verifica que km se haya resuelto correctamente como prefijo

    def test_custom_unit(self):
        """Prueba la resolución de unidades personalizadas."""
        text = "atm"
        parser = UnitParser(text, self.mapping, self.alias_resolver)
        result = parser.parse()
        self.assertIsInstance(result, PrefixedUnit)  # Esperamos un PrefixedUnit para atm

    def test_number_only(self):
        """Prueba la interpretación de números sin unidades."""
        text = "1000"
        parser = UnitParser(text, self.mapping, self.alias_resolver)
        result = parser.parse()
        self.assertEqual(result.prefix, 1000)  # Verifica que solo el número se interpreta correctamente

if __name__ == '__main__':
    unittest.main()
