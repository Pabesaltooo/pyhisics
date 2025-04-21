from abc import ABC, abstractmethod
from typing import Union, List
from numbers import Real

from .sscalar import Scalar
from .vvector import Vector, Poly
from .mmatrix import Matrix



# Tipos base para números, vectores y matrices.
# Ahora tambien tenemos Symbol y Expression, me gustaria que estos se pudieran añadir al value de una clase
T_Scalar = Union[int, float] # Seria mejor un TypeVar para poder definir operaciones entre diferentes tipos de escalares (complejos, simbolicos...)
T_Vector = List[T_Scalar]
T_Matrix = List[T_Vector]



T_Algebraic = Union[T_Scalar, T_Vector, T_Matrix]
Algebraic = Union[Scalar, Vector, Matrix, Poly]
    
def T2Algebraic(val: T_Algebraic) -> Algebraic:
    """Convierte un valor de T_Algebraic en una instancia de Algebraic"""
    if isinstance(val, T_Scalar):
        return Scalar(val)
    elif isinstance(val, list) and all(isinstance(i, T_Scalar) for i in val): 
        return Vector(val)
    elif isinstance(val, list) and all(isinstance(i, list) and all(isinstance(j, T_Scalar) for j in i) for i in val):
        return Matrix(val)
    else:
        raise TypeError(f"Tipo no soportado: {type(val)}")