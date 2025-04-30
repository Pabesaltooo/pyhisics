from __future__ import annotations

from random import random, gauss
from typing import (
    Any, Iterable, Iterator, List, Optional, Union,
    overload, TYPE_CHECKING
)

from .algebraic_core import (
     Addable, Multiplyable,
    ScalarLike, VectorLike,
    AlgebraicOps, round_T_Scalar
)

from .vector import VectorCore

if TYPE_CHECKING:                       # — tipos sólo para el checker
    from .scalar import Scalar
    from .matrix import Matrix
    from .vector import Vector


class Point(VectorCore, Addable[VectorLike], Multiplyable[VectorLike]):
    def is_identity(self) -> bool:
        return False
    
    def __str__(self) -> str: # TODO
        from .matrix import Matrix
        return str(Matrix([self._value]))
    
    def _repr_latex_(self) -> str: # TODO
        from .matrix import Matrix
        return f'${Matrix([self._value]).latex()}$'

    @overload
    def __mul__(self, other: ScalarLike) -> Point: ...
    @overload
    def __mul__(self, other: Scalar) -> Point: ...
    @overload
    def __mul__(self, other: Matrix) -> Point: ...
    
    def __mul__(self, other): # type: ignore
        from .scalar import Scalar                        
        from .matrix import Matrix                      
        if isinstance(other, ScalarLike):
            other = Scalar(other)
        if isinstance(other, Scalar):
            return Point(AlgebraicOps.mul_vector_scalar_like(self._value, other.value))
        if isinstance(other, Matrix):
            return Point(AlgebraicOps.mul_mat_vec_like(other.value, self._value))
        return NotImplemented

    def __rmul__(self, other: ScalarLike) -> Point:
        return self * other

    @overload
    def __add__(self, other: Point) -> Vector: ...
    @overload
    def __add__(self, other: Vector) -> Point: ...
    
    def __add__(self, other: Addable[VectorLike]):
        from .vector import Vector
        if isinstance(other, Point):
            return Vector(AlgebraicOps.add_vector_like((-self)._value, other.value))
        if isinstance(other, Vector):
            return Point(AlgebraicOps.add_vector_like(self._value, other.value))
        raise NotImplementedError
    
    def __neg__(self) -> Point:
        return Point([-x for x in self._value])

    def __sub__(self, other: Addable[VectorLike]) -> Vector:
        from .vector import Vector
        return Vector(AlgebraicOps.add_vector_like(other.value, (-self)._value))

    def __round__(self, ndigits: int = 2) -> Point:
        return Point(round_T_Scalar(v, ndigits) for v in self)

    @overload
    def __truediv__(self, other: ScalarLike) -> Point:
        ...
    @overload
    def __truediv__(self, other: Scalar) -> Point:
        ...

    def __truediv__(self, other):
        from .scalar import Scalar                        
        if isinstance(other, ScalarLike):
            other = Scalar(other)
        if isinstance(other, Scalar):
            return Point(AlgebraicOps.div_vector_scalar_like(self._value, other.value))
        return NotImplemented

    def vector(self) -> Vector:
        from .vector import Vector
        return Vector(self._value)
