"""
Pyhsics: Una librería para cálculos físicos, manejo de unidades, geometría y medidas.

Provee clases para trabajar con unidades, cantidades físicas y operaciones geométricas.
"""
from typing import Iterable, List, Sequence

from pyhsics.linalg.core.algebraic_core import ScalarLike
from .printing import setup
from .printing.setup import set_printing_mode
from .linalg import (Scalar, Point, Matrix, 
                     Vector, LinearSystem, BilinealForm)
from .units import Unit, UnitAliasManager
from .quantity import ScalarQuantity, VectorQuantity, Quantity, Constants
from .funcs import *
from .measure import DirectMeasure, CalculatedMeasure
from .plotter import Plotter, MultiPlotter

def eye(size: int) -> Matrix:
    """
    Returns an identity matrix of the given size.
    """
    return Matrix.eye(size)

def points(*args: Sequence[ScalarLike]) -> List[Point]:
    """
    return [Point(arg) for arg in args]
    """
    return [Point(arg) for arg in args]

def vectors(*args: Sequence[ScalarLike]) -> List[Vector]:
    """
    return [Vector(arg) for arg in args]
    """
    return [Vector(arg) for arg in args]

__all__ = [
    'Scalar',
    'Vector',
    'Point',
    'Matrix',
    
    'eye',
    'points',
    'vectors',

    'LinearSystem',
    'BilinealForm',
    
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