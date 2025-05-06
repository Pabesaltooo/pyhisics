from __future__ import annotations
from typing import Union, overload, TYPE_CHECKING


from ..linalg import ScalarLike, Scalar, Vector, Matrix, Algebraic
from .core_quantity import Quantity, QOPERABLE, T_, QMultiplyable, QAddable

if TYPE_CHECKING:
    from .scalar_quantity import ScalarQuantity
    from .vector_quantity import VectorQuantity

class MatrixQuantity(Quantity[Matrix]):
    """
    Representa una magnitud matricial: Matrix + unidad (fundamental o compuesta).
    Todas las entradas de la matriz comparten la misma unidad.
    """
    
    def __eq__(self, other: object) -> bool:
        return self.value.__eq__(other)
 
    @overload
    def __mul__(self, other: Union[ScalarLike, Scalar, ScalarQuantity]) -> MatrixQuantity: ...
    @overload
    def __mul__(self, other: Union[Vector, VectorQuantity]) -> VectorQuantity: ...
    @overload
    def __mul__(self, other: Union[Matrix, MatrixQuantity]) -> MatrixQuantity: ...
    
    def __mul__(self, other: Union[QOPERABLE[T_], QMultiplyable[T_]]):
        if isinstance(other, Union[ScalarLike, Algebraic]):
            result = self.value * other
            return type(Quantity)(result, self.units)
        return type(Quantity)(self.value*other.value, self.units*other.units)
    
    def __rmul__(self, other: Union[Scalar, ScalarLike]) -> MatrixQuantity:
        if isinstance(other, ScalarLike):
            result = self.value * other
            return MatrixQuantity(result, self.units)
        return NotImplemented
        
    def __add__(self, other: QAddable[Matrix]) -> MatrixQuantity:
        if self.units == other.units:
            return MatrixQuantity(self.value + other.value, self.units)
        raise ValueError("Unidades no compatibles en la suma")    
    
    def __neg__(self) -> MatrixQuantity:
        return MatrixQuantity(-self.value, self.units)
    
    def __sub__(self, other: QAddable[Matrix]) -> MatrixQuantity:
        return self + (-other)

    def transpose(self) -> 'MatrixQuantity':
        """
        Retorna la transpuesta de la matriz, manteniendo la misma unidad.
        """
        return MatrixQuantity(self.value.T, self.units)

    def determinant(self) -> ScalarQuantity:
        """
        Calcula el determinante de la matriz y lo retorna como ScalarQuantity.
        La unidad del determinante se eleva a la cantidad de filas (o columnas) de la matriz.
        """
        det = self.value.det()
        # Se asume que la unidad se comporta de manera exponencial según el tamaño de la matriz.
        return ScalarQuantity(det, self.units ** self.value.shape[0])