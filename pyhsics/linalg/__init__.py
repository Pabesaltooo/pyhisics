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
