from __future__ import annotations
from typing import List
from .operations import AlgebraicClass, Addable, Multiplyable

from .alg_types import *

class Point(AlgebraicClass):
    @property
    def value(self) -> int | float | List[int | float] | List[List[int | float]]:
        raise NotImplementedError

    def mul(self, other: Multiplyable) -> Scalar | Vector | Matrix:
        raise NotImplementedError

    @property
    def is_zero(self) -> bool:
        raise NotImplementedError

    @property
    def is_identity(self) -> bool:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError

    def __add__(self, other: Addable) -> Vector:
        raise NotImplementedError

    def __neg__(self) -> Vector:
        raise NotImplementedError

    def __round__(self, n: int = 2) -> Point:
        raise NotImplementedError

    def __truediv__(self, other: Scalar | Vector | Matrix) -> Algebraic:
        raise NotImplementedError

    def __pow__(self, other: AlgebraicClass | int | float) -> Scalar | Vector | Matrix:
        raise NotImplementedError