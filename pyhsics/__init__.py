"""
Pyhsics: Una librería para cálculos físicos, manejo de unidades, geometría y medidas.

Provee clases para trabajar con unidades, cantidades físicas y operaciones geométricas.
"""
from .printing import setup
from .printing.setup import set_printing_mode
from .linalg import (Scalar, 
                     Vector, Matrix, 
                     LinearSistem)
#                     Symbol, symbols, Term, Expression)
from .units import Unit, UnitAliasManager
from .quantity import ScalarQuantity, VectorQuantity, Quantity, Constants
from .measure import DirectMeasure, CalculatedMeasure
from .plotter import Plotter, MultiPlotter


__all__ = [
    'Scalar',
    'Vector',
    'Matrix',

    'LinearSistem',
    
    'Unit',
    'UnitAliasManager',

    'Quantity',
    'ScalarQuantity',
    'VectorQuantity',
    'Constants',
    
    'DirectMeasure',
    'CalculatedMeasure',
    
    'Plotter',
    'MultiPlotter'
]