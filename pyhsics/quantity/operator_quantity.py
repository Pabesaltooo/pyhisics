from __future__ import annotations
from dataclasses import dataclass
from typing import Union

from ..linalg import Algebraic, T_Algebraic, Scalar, Vector, Matrix
from ..linalg.operations import (AlgebraicOperator,
                                 ScalarAddable, ScalarMultiplyable,
                                 VectorialAddable, VectorialMultiplyable,
                                 MatrixAddable, MatrixMultiplyable)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base_quantity import BaseQuantity
    from .quantity_quantity import Quantity

Operable = Union[Algebraic, T_Algebraic, 'BaseQuantity']


@dataclass(frozen=True)
class QuantityOperator:
    Q1: 'BaseQuantity'
    Q2: 'BaseQuantity'
    
    def sum(self) -> Quantity:
        Q1 = self.Q1
        Q2 = self.Q2
        
        if Q1.units != Q2.units:
            raise ValueError(f"Las unidades no son compatibles: {Q1.units} vs {Q2.units}")
        
        v1 = Q1.value
        v2 = Q2.value
        
        if isinstance(v1, ScalarAddable) and isinstance(v2, ScalarAddable):
            from .scalar_quantity import ScalarQuantity
            return ScalarQuantity(v1 + v2, Q1.units)
        
        if isinstance(v1, VectorialAddable) and isinstance(v2, VectorialAddable):
            from .vector_quantity import VectorQuantity
            return VectorQuantity(v1 + v2, Q1.units)
        
        if isinstance(v1, MatrixAddable) and isinstance(v2, MatrixAddable):
            from .matrix_quantity import MatrixQuantity
            return MatrixQuantity(v1 + v2, Q1.units)
        raise ValueError(f'No se pueden sumar estos dos tipos: {type(v1)} + {type(v2)}')

    def mul(self) -> Quantity:
        Q1 = self.Q1
        Q2 = self.Q2
        
        units = Q1.units * Q2.units
        value = Q1.value * Q2.value
        
        if isinstance(value, ScalarMultiplyable):
            from .scalar_quantity import ScalarQuantity
            return ScalarQuantity(value, units)
        
        if isinstance(value, VectorialMultiplyable):
            from .vector_quantity import VectorQuantity
            return VectorQuantity(value, units)
        
        if isinstance(value, MatrixMultiplyable): # type: ignore
            from .matrix_quantity import MatrixQuantity
            return MatrixQuantity(value, units)
        
        raise ValueError(f'No se pueden multiplicar estos dos tipos: {type(Q1.value)} * {type(Q2.value)}')
        
    def div(self) -> Quantity:
        Q1 = self.Q1
        Q2 = self.Q2
        
        if Q2.is_zero:
            raise ZeroDivisionError
        if not isinstance(Q2.value, Scalar):
            raise NotImplemented
        
        new_value = AlgebraicOperator.div(Q1.value,Q2.value)
        
        if isinstance(new_value, Scalar):
            from .scalar_quantity import ScalarQuantity
            return ScalarQuantity(new_value, Q1.units / Q2.units)
        
        if isinstance(new_value, Vector):
            from .vector_quantity import VectorQuantity
            return VectorQuantity(new_value, Q1.units / Q2.units)
        
        if isinstance(new_value, Matrix): #type: ignore
            from .matrix_quantity import MatrixQuantity
            return MatrixQuantity(new_value, Q1.units / Q2.units)
        
        raise ValueError(f'No se pueden dividir estos dos tipos: {type(Q1.value)} / {type(Q2.value)}')

    def pow(self) -> Quantity:
        ...