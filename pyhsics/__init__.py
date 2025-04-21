"""
Pyhsics: Una librería para cálculos físicos, manejo de unidades, geometría y medidas.

Provee clases para trabajar con unidades, cantidades físicas y operaciones geométricas.
"""
from .linalg import (Point, Scalar, 
                     Vector, Matrix, 
                     LinearSistem, Poly, 
                     Symbol, symbols, Term, Expression)
from .units import Unit, UnitAliasManager
from .quantity import ScalarQuantity, VectorQuantity, Quantity, Constants
from .measure import DirectMeasure, CalculatedMeasure
from .plotter import Plotter, MultiPlotter


__all__ = [
    'Scalar',
    'Point',
    'Vector',
    'Matrix',
    
    'Symbol', 
    'symbols', 
    'Term', 
    'Expression',

    'Poly',
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