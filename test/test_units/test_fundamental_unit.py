import unittest
from pyhsics.units.fundamental_unit import FundamentalUnit, UNIT_ORDER

class TestFundamentalUnit(unittest.TestCase):

    def test_enum_values(self):
        """Verifica que los valores de las unidades fundamentales sean los correctos."""
        self.assertEqual(FundamentalUnit.ONE.value, '1')
        self.assertEqual(FundamentalUnit.ANGLE.value, 'rad')
        self.assertEqual(FundamentalUnit.LIGHT.value, 'cd')
        self.assertEqual(FundamentalUnit.MASS.value, 'kg')
        self.assertEqual(FundamentalUnit.TEMPERATURE.value, 'K')
        self.assertEqual(FundamentalUnit.SUBSTANCE_QUANTITY.value, 'mol')
        self.assertEqual(FundamentalUnit.ELECTRIC_CURRENT.value, 'A')
        self.assertEqual(FundamentalUnit.DISTANCE.value, 'm')
        self.assertEqual(FundamentalUnit.TIME.value, 's')

    def test_enum_str(self):
        """Verifica que la representación en cadena de las unidades fundamentales sea correcta."""
        self.assertEqual(str(FundamentalUnit.ONE), '1')
        self.assertEqual(str(FundamentalUnit.ANGLE), 'rad')
        self.assertEqual(str(FundamentalUnit.LIGHT), 'cd')
        self.assertEqual(str(FundamentalUnit.MASS), 'kg')
        self.assertEqual(str(FundamentalUnit.TEMPERATURE), 'K')
        self.assertEqual(str(FundamentalUnit.SUBSTANCE_QUANTITY), 'mol')
        self.assertEqual(str(FundamentalUnit.ELECTRIC_CURRENT), 'A')
        self.assertEqual(str(FundamentalUnit.DISTANCE), 'm')
        self.assertEqual(str(FundamentalUnit.TIME), 's')

    def test_enum_repr(self):
        """Verifica que la representación en consola de las unidades fundamentales sea la correcta."""
        self.assertEqual(repr(FundamentalUnit.ONE), "<ONE>")
        self.assertEqual(repr(FundamentalUnit.ANGLE), "<ANGLE>")
        self.assertEqual(repr(FundamentalUnit.LIGHT), "<LIGHT>")
        self.assertEqual(repr(FundamentalUnit.MASS), "<MASS>")
        self.assertEqual(repr(FundamentalUnit.TEMPERATURE), "<TEMPERATURE>")
        self.assertEqual(repr(FundamentalUnit.SUBSTANCE_QUANTITY), "<SUBSTANCE_QUANTITY>")
        self.assertEqual(repr(FundamentalUnit.ELECTRIC_CURRENT), "<ELECTRIC_CURRENT>")
        self.assertEqual(repr(FundamentalUnit.DISTANCE), "<DISTANCE>")
        self.assertEqual(repr(FundamentalUnit.TIME), "<TIME>")

    def test_unit_order(self):
        """Verifica que el orden de las unidades fundamentales en UNIT_ORDER sea el correcto."""
        expected_order = [
            FundamentalUnit.MASS,
            FundamentalUnit.ANGLE,
            FundamentalUnit.DISTANCE,
            FundamentalUnit.TIME,
            FundamentalUnit.LIGHT,
            FundamentalUnit.TEMPERATURE,
            FundamentalUnit.ELECTRIC_CURRENT,
            FundamentalUnit.SUBSTANCE_QUANTITY,
            FundamentalUnit.ONE,
        ]
        self.assertEqual(UNIT_ORDER, expected_order)

if __name__ == '__main__':
    unittest.main()
