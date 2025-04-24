from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Union, Sequence

from dataclasses import dataclass

from .exceptions import *
from .printable import Printable
from .symbolic import Expression, _Term

T = TypeVar('T', bound=Union[Expression, List[Expression], List[List[Expression]]])

class Algebraic(Generic[T],Printable, ABC):
    """Value: T, sobrecarga de operadores arimeticos y logico-booleanos"""
    pass

class Scalar(Algebraic[Expression]):
    pass

class Vector(Algebraic[List[Expression]]):
    pass

class Matrix(Algebraic[List[List[Expression]]]):
    pass



      
VectorLike = Sequence[Expression]    
MatrixLike = Sequence[Sequence[Expression]]

@dataclass(frozen=True)
class AlgebraicOperator:
    """Define Sumas, Multiplicaciones, Restas, Divisiones y Potencias para objetos `Algebraic` como `Scalar, Vector, Matrix`"""
    
    @classmethod
    def sum_scalar_scalar(cls, a: Algebraic[Expression], b: Algebraic[Expression]) -> Scalar:
        return a + b
    @classmethod
    def sum_matrix_matrix(cls, a: MatrixLike, b: MatrixLike) -> MatrixLike:
        if len(a) != len(b) or any(len(row) != len(other_row) for row, other_row in zip(a, b)):
            raise DimensionMatchError("Las matrices deben tener las mismas dimensiones.")
        return [[a_ij + b_ij for a_ij, b_ij in zip(row, other_row)]
                for row, other_row in zip(a, b)]
    @classmethod
    def sum_vector_vector(cls, a: VectorLike, b: VectorLike) -> VectorLike:
        if len(a) != len(b):
            raise DimensionMatchError("Los vectores deben tener la misma dimensión.")
        return [a_i + b_i for a_i, b_i in zip(a, b)]
    
    @classmethod
    def mul_scalar_scalar(cls, a: Expression, b: Expression) -> Expression:
        return a * b
    
    @classmethod
    def mul_vector_scalar(cls, a: VectorLike, b: Expression) -> VectorLike:
        return [a_i * b for a_i in a]
    
    @classmethod
    def mul_vector_vector(cls, a: VectorLike, b: VectorLike, M: MatrixLike) -> Expression:
        """Se usa el producto punto estandar de un espacio euclideo."""
        if len(a) != len(b):
            raise DimensionMatchError("Los vectores deben tener la misma dimensión.")
        return sum((Expression([_Term(a[i] * M[i][j] * b[j])]) for i in range(len(a)) for j in range(len(b))), start=Expression())
    
    @classmethod
    def mul_vector_matrix(cls, a: VectorLike, b: MatrixLike) -> VectorLike:
        raise DimensionMatchError("Los vectores deben multiplicarse a la derecha de las matrices: `M * v`. Si no prueba `v.T * M`")

    @classmethod
    def mul_matrix_scalar(cls, a: MatrixLike, b: Expression) -> MatrixLike:
        return [[a_ij * b for a_ij in row] for row in a]
    
    @classmethod
    def mul_matrix_vector(cls, a: MatrixLike, b: VectorLike) -> Union[VectorLike, Expression]:
        if len(a[0]) != len(b):
            raise DimensionMatchError(f"Dimensiones incompatibles: {len(a[0])} x {len(a)} vs. {len(b)} x 1 para multiplicación de matriz por vector.")
        rv = [sum((a_ij * b_i for a_ij, b_i in zip(row, b)), start=Expression()) for row in a]
        return rv[0] if len(rv) == 1 else rv
        
        
    @classmethod
    def mul_matrix_matrix(cls, a: MatrixLike, b: MatrixLike) -> MatrixLike:
        if len(a[0]) != len(b):
            raise DimensionMatchError(f"Dimensiones incompatibles: {len(a)} x {len(a[0])} vs. {len(b)} x {len(b[0])} para multiplicación matrices.")
        result: MatrixLike  = []
        for i in range(len(a)):
            new_row: VectorLike = []
            for j in range(len(b[0])):
                sum_product = Expression()
                for k in range(len(a[0])):
                    sum_product += a[i][k] * b[k][j]
                new_row.append(sum_product)
            result.append(new_row)
        return result
    
    @classmethod
    def div_scalar(cls, a: Expression, b: Expression) -> Expression:
        return a / b
    @classmethod
    def div_vector_scalar(cls, a: VectorLike, b: Expression) -> VectorLike:
        return [a_i / b for a_i in a]
    @classmethod
    def div_matrix_scalar(cls, a: MatrixLike, b: Expression) -> MatrixLike:
        return [[a_ij / b for a_ij in row] for row in a]

    @classmethod
    def div(cls, a: Algebraic, b: Algebraic) -> Union[Expression, VectorLike, MatrixLike]:
        if not isinstance(b, Scalar):
            raise ValueError(f"No se puede dividir por un {type(b)}.")
        if isinstance(a, Scalar):
            return AlgebraicOperator.div_scalar(a.value, b.value)
        if isinstance(a, Vector):
            return AlgebraicOperator.div_vector_scalar(a.value, b.value)
        if isinstance(a, Matrix):
            return AlgebraicOperator.div_matrix_scalar(a.value, b.value)
        raise TypeError(f"Operación no soportada para tipo {type(a)}.")

