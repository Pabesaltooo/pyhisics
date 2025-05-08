from typing import Union

#from .vector import Vector
from .structures.scalar import Scalar
from .structures.vector import Vector
from .structures.matrix import Matrix
from .structures.point  import Point
from .solvers.linear_system import LinearSystem
from .solvers.bilineal_form import Form
from .core.algebraic_core import ScalarLike, VectorLike, MatrixLike, Algebraic, T2Algebraic

"""from .symbolic_math.symbol import Symbol, symbols
from .symbolic_math.term import Term
from .symbolic_math.expression import Expression
from .symbolic_math.symbolic_operator import Pow
"""
AlgLike = Union[ScalarLike, VectorLike, MatrixLike]
ALG = Union[Scalar, Vector, Matrix]

__all__ = [
    'Scalar',
    'Vector',
    'Point',
    'Matrix',
    
    'LinearSystem',
    'Form',
    
    'T2Algebraic',
    
    'ALG',
    'AlgLike',
    'Algebraic'
]
