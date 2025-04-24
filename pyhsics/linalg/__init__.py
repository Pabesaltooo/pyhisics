from typing import Union

#from .vector import Vector
from .scalar import Scalar
from .vector import Vector
from .matrix import Matrix
from .linear_sistem import LinearSistem
from .algebraic_core import ScalarLike, VectorLike, MatrixLike, Algebraic, T2Algebraic

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
    'Matrix',
    
    'LinearSistem',
    
    'ALG',
    'AlgLike',
    'Algebraic'
]
"""    
    'Symbol', 
    'symbols', 
    'Term', 
    'Expression',
    'Pow'
]"""