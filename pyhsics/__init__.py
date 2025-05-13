"""
Pyhsics: Una librería para cálculos físicos, manejo de unidades, geometría y medidas.

Provee clases para trabajar con unidades, cantidades físicas y operaciones geométricas.
"""
from .printing import setup
from .printing.setup import set_printing_mode
from .linalg import (Scalar, Point,
                     Vector, Matrix, 
                     LinearSystem, Form)
#                     Symbol, symbols, Term, Expression)
from .units import Unit, UnitAliasManager
from .quantity import ScalarQuantity, VectorQuantity, Quantity, Constants
from .funcs import *
from .measure import DirectMeasure, CalculatedMeasure
from .plotter import Plotter, MultiPlotter


__all__ = [
    'Scalar',
    'Vector',
    'Point',
    'Matrix',

    'LinearSystem',
    'Form',
    
    'Unit',
    'UnitAliasManager',

    'Quantity',
    'ScalarQuantity',
    'VectorQuantity',
    'Constants',
    
    "sin", "cos", "tan", "asin", "acos", "atan",
    "sqrt", "log", "log10", "exp",
    
    'DirectMeasure',
    'CalculatedMeasure',
    
    'Plotter',
    'MultiPlotter'
]