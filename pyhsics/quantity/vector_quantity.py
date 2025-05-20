from __future__ import annotations
from typing import Union, overload, TYPE_CHECKING

from ..linalg.structures.matrix.matrix import Matrix


from ..linalg import ScalarLike, Scalar, Vector, Algebraic
from .core_quantity import Quantity, QOPERABLE, T_, QMultiplyable, QAddable

if TYPE_CHECKING:
    from .scalar_quantity import ScalarQuantity

class VectorQuantity(Quantity[Vector]): # Quiero que tambien sea de vectorial para que tenga los atributos necerasios sin reescribirlo.
    """
    Representa una magnitud vectorial: Vector + unidad (fundamental o compuesta).
    Todas las componentes del vector comparten la misma unidad.
    """
    
    @overload
    def __mul__(self, other: Union[ScalarLike, Scalar, ScalarQuantity]) -> VectorQuantity: ...
    @overload
    def __mul__(self, other: Union[Vector, VectorQuantity]) -> ScalarQuantity: ...
    
    def __mul__(self, other: Union[QOPERABLE[T_], QMultiplyable[T_]]):
        if isinstance(other, Union[ScalarLike, Algebraic]):
            if isinstance(other, Matrix):
                raise NotImplementedError
            result = self.value * other
            return Quantity(result, self.units)
        if isinstance(other.value, Matrix):
            raise NotImplementedError
        return Quantity(self.value*other.value, self.units*other.units)
    
    def __rmul__(self, other: Union[Scalar, ScalarLike]) -> VectorQuantity:
        if isinstance(other, ScalarLike):
            result = self.value * other
            return VectorQuantity(result, self.units)
        return NotImplemented
        
    def __add__(self, other: QAddable[Vector]) -> VectorQuantity:
        if self.units == other.units:
            return VectorQuantity(self.value + other.value, self.units)
        raise ValueError("Unidades no compatibles en la suma")    
    
    def __neg__(self) -> VectorQuantity:
        return VectorQuantity(-self.value, self.units)
    
    def __sub__(self, other: QAddable[Vector]) -> VectorQuantity:
        return self + (-other)

    def magnitude(self) -> ScalarQuantity:
        mag = self.value.magnitude
        return Quantity(mag, self.units)
    
    def dot(self, other: Union[Vector, VectorQuantity]) -> ScalarQuantity:
        ...
        
    def cross(self, other: Union[Vector, VectorQuantity]) -> 'VectorQuantity':
        if isinstance(other, VectorQuantity):
            return VectorQuantity(self.value.cross(other.value), self.units * other.units)
        else:
            return VectorQuantity(self.value.cross(other), self.units)

    def angle(self, other: Union[Vector, VectorQuantity]) -> ScalarQuantity:
        raise NotImplementedError
    
    def distance(self, other: Union[Vector, VectorQuantity]) -> ScalarQuantity:
        raise NotImplementedError

    def norm(self) -> 'VectorQuantity':
        return VectorQuantity(self.value.norm())

    def __round__(self, n: int = 2) -> VectorQuantity:
        return VectorQuantity(round(self.value, n), self.units)
    
    def __truediv__(self, other: Union[ScalarLike, Scalar, ScalarQuantity]) -> VectorQuantity:
        if not isinstance(other, Quantity):
            other = Quantity(other)
        num, denom = self.value, other.value
        u1, u2 = self.units, other.units
        return VectorQuantity(num / denom, u1 / u2)