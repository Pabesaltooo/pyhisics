"""Linear algebra primitives exported for public use.

This package exposes common algebraic structures such as ``Scalar`` and
``Vector`` as well as solvers like ``LinearSystem``.  It gathers the most
useful pieces of the :mod:`pyhsics.linalg` submodules so they can be imported
directly from ``pyhsics.linalg``.
"""

from typing import Union

from pyhsics.linalg.core.algebraic_core import ScalarLike, VectorLike, MatrixLike, Algebraic, T2Algebraic
from pyhsics.linalg.structures import Scalar, Vector, Matrix, Point
from pyhsics.linalg.solvers.linear_system import LinearSystem
from pyhsics.linalg.solvers.bilineal_form import BilinealForm

AlgLike = Union[ScalarLike, VectorLike, MatrixLike]
ALG = Union[Scalar, Vector, Matrix]

__all__ = [
    'Scalar',
    'Vector',
    'Point',
    'Matrix',
    
    'LinearSystem',
    'BilinealForm',
    
    'T2Algebraic',
    
    'ALG',
    'AlgLike',
    'Algebraic'
]
