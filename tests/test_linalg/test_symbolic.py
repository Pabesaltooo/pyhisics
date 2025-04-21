import unittest
from pyhsics.linalg._pruebas.symbolic import *

class TestSymbolicAlgebra(unittest.TestCase):
    def setUp(self):
        # Create some common symbols for testing
        self.x = Symbol('x')
        self.y = Symbol('y')
        self.z = Symbol('z')

    def test_symbol_creation(self):
        """Test basic symbol creation and properties"""
        self.assertEqual(str(self.x), 'x')
        self.assertEqual(self.x._repr_latex_(), '$x$')
        self.assertFalse(self.x.is_zero())
        self.assertFalse(self.x.is_identity())

    def test_basic_operations(self):
        """Test basic arithmetic operations with symbols"""
        # Addition
        expr = self.x + self.y
        self.assertEqual(str(expr), 'x + y')
        
        # Subtraction
        expr = self.x - self.y
        self.assertEqual(str(expr), 'x + -y')
        
        # Multiplication
        expr = self.x * self.y
        self.assertEqual(str(expr), 'x y')
        
        # Division
        expr = self.x / self.y
        self.assertEqual(str(expr), 'x y^-1')

    def test_numeric_operations(self):
        """Test operations with numbers"""
        # Symbol + number
        expr = self.x + 2
        self.assertEqual(str(expr), 'x + 2')
        
        # Number + symbol
        expr = 2 + self.x
        self.assertEqual(str(expr), '2 + x')
        
        # Symbol * number
        expr = self.x * 3
        self.assertEqual(str(expr), '3x')

    def test_power_operations(self):
        """Test power operations"""
        # Integer powers
        expr = self.x ** 2
        self.assertEqual(str(expr), 'x^2')
        
        # Negative powers
        expr = self.x ** (-1)
        self.assertEqual(str(expr), 'x^-1')
        
        # Zero power
        expr = self.x ** 0
        self.assertEqual(str(expr), '1')
        
        # Symbolic powers
        expr = self.x ** self.y
        self.assertTrue(isinstance(expr, Pow))

    def test_expression_simplification(self):
        """Test expression simplification"""
        # Like terms
        expr = (self.x + self.x).simplify()
        self.assertEqual(str(expr), '2x')
        
        # Zero terms
        expr = (self.x - self.x).simplify()
        self.assertEqual(str(expr), '0')
        
        # Multiple variables
        expr = (self.x * self.y + self.x * self.y).simplify()
        self.assertEqual(str(expr), '2x y')

    def test_zero_division(self):
        """Test division by zero"""
        with self.assertRaises(ZeroDivisionError):
            self.x / Expression(0)

    def test_complex_expressions(self):
        """Test more complex expressions"""
        # (x + y)(x - y)
        expr = (self.x + self.y) * (self.x - self.y)
        self.assertEqual(str(expr.simplify()), 'x^2 + -y^2')
        
        # (x + 1)^2
        expr = (Expression([Term(1, {self.x: 1}), Term(1)]) ** 2).simplify()
        self.assertEqual(str(expr), 'x^2 + 2x + 1')

    def test_power_basic(self):
        """Test basic power operations"""
        # Integer powers
        expr = self.x ** 2
        self.assertEqual(str(expr), 'x^2')

        # Power of zero
        expr = self.x ** 0
        self.assertEqual(str(expr), '1')

        # Negative powers
        expr = self.x ** (-1)
        self.assertEqual(str(expr), 'x^-1')

    def test_power_symbolic(self):
        """Test powers with symbolic exponents"""
        expr = self.x ** self.y
        self.assertTrue(isinstance(expr, Pow))
        self.assertEqual(str(expr), '(x)^(y)')

    def test_power_distribution(self):
        """Test power distribution properties"""
        # (x * y)^2 should expand to x^2 * y^2
        expr = (self.x * self.y) ** 2
        simplified = expr.simplify()
        self.assertEqual(str(simplified), 'x^2 y^2')

        # (x + y)^2 should expand to x^2 + 2xy + y^2
        expr = (Expression([Term(1, {self.x: 1}), Term(1, {self.y: 1})]) ** 2).simplify()
        self.assertEqual(str(expr), 'x^2 + 2x y + y^2')

    def test_power_chain(self):
        """Test chained power operations"""
        # (x^2)^3 should simplify to x^6
        expr = (self.x ** 2) ** 3
        simplified = expr.simplify()
        self.assertEqual(str(simplified), 'x^6')

        # x^2 * x^3 should simplify to x^5
        expr = (self.x ** 2 * self.x ** 3).simplify()
        self.assertEqual(str(simplified), 'x^5')

    def test_power_zero_base(self):
        """Test powers with zero base"""
        # 0^positive should be 0
        expr = (Expression([Term(0)]) ** 2).simplify()
        self.assertEqual(str(expr), '0')

        # 0^0 should be 1
        expr = (Expression([Term(0)]) ** 0).simplify()
        self.assertEqual(str(expr), '1')

    def test_complex_expressions(self):
        """Test more complex algebraic expressions"""
        # (x + y)^2 * (x - y)
        expr = ((self.x + self.y) ** 2 * (self.x - self.y)).simplify()
        self.assertEqual(str(expr), 'x^3 + x^2 y + -x y^2 + -y^3')

        # (x^2 + 2xy + y^2) / (x + y)
        numer = self.x**2 + 2*self.x*self.y + self.y**2
        denom = self.x + self.y
        expr = (numer / denom).simplify()
        self.assertEqual(str(expr), 'x + y')

    def test_power_with_coefficients(self):
        """Test powers with coefficients"""
        # (2x)^2 should be 4x^2
        expr = ((2 * self.x) ** 2).simplify()
        self.assertEqual(str(expr), '4x^2')

        # (3x + 2y)^2
        expr = ((3 * self.x + 2 * self.y) ** 2).simplify()
        self.assertEqual(str(expr), '9x^2 + 12x y + 4y^2')

    def test_power_simplification_rules(self):
        """Test power simplification rules"""
        # x^1 should simplify to x
        expr = (self.x ** 1).simplify()
        self.assertEqual(str(expr), 'x')

        # 1^x should simplify to 1
        expr = (Expression([Term(1)]) ** self.x).simplify()
        self.assertEqual(str(expr), '1')

        # x^(a+b) * x^(-b) should simplify to x^a
        a = Symbol('a')
        b = Symbol('b')
        expr = (self.x ** (a + b) * self.x ** (-b)).simplify()
        self.assertEqual(str(expr), 'x^a')

if __name__ == '__main__':
    unittest.main()