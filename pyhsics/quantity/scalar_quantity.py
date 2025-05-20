from __future__ import annotations
from typing import Union, overload, TYPE_CHECKING, cast

from ..linalg.structures.matrix.matrix import Matrix

from ..linalg import ScalarLike, Scalar, Vector, Algebraic, AlgLike
from ..units import Unit
from .core_quantity import Quantity, QOPERABLE, T_, QMultiplyable, QAddable, ALG_TYPES, process_unit_and_value

if TYPE_CHECKING:
    from .vector_quantity import VectorQuantity
    from .matrix_quantity import MatrixQuantity

class ScalarQuantity(Quantity[Scalar]):
    """
    Representa una magnitud física: valor + unidad (fundamental o compuesta).
    """
    
    __slots__ = ("_value", '_units',)
    
    def __init__(self, value: Union[AlgLike, ALG_TYPES], unit: Union[str, Unit] = '1') -> None:
        val, uni = process_unit_and_value(value, unit)
        self._value = cast(Scalar, val)
        self._units = uni
        
    
    def __abs__(self) -> ScalarQuantity:
        return ScalarQuantity(abs(self.value), self.units)
    
    @overload
    def __mul__(self, other: Union[ScalarLike, Scalar, ScalarQuantity]) -> ScalarQuantity: ...
    @overload
    def __mul__(self, other: Union[Vector, VectorQuantity]) -> VectorQuantity: ...
    @overload
    def __mul__(self, other: Union[Matrix, MatrixQuantity]) -> MatrixQuantity: ...
    
    def __mul__(self, other: Union[QOPERABLE[T_], QMultiplyable[T_]]):
        if isinstance(other, Union[ScalarLike, Algebraic]):
            result = self.value * other
            return Quantity(result, self.units)
        return Quantity(self.value*other.value, self.units*other.units)
    
    def __rmul__(self, other: Union[Scalar, ScalarLike]) -> ScalarQuantity:
        if isinstance(other, ScalarLike):
            result = self.value * other
            return ScalarQuantity(result, self.units)
        return NotImplemented
        
    def __add__(self, other: QAddable[Scalar]) -> ScalarQuantity:
        if self.units == other.units:
            return ScalarQuantity(self.value + other.value, self.units)
        raise ValueError("Unidades no compatibles en la suma")
    
    def __neg__(self) -> ScalarQuantity:
        return ScalarQuantity(-self.value, self.units)
    
    def __sub__(self, other: QAddable[Scalar]) -> ScalarQuantity:
        return self + (-other)
    
    @overload
    def __truediv__(self, other: Union[ScalarLike, Scalar, ScalarQuantity]) -> ScalarQuantity: ...
    @overload
    def __truediv__(self, other: Union[Vector, VectorQuantity]) -> ScalarQuantity: ...
    @overload
    def __truediv__(self, other: Union[Matrix, MatrixQuantity]) -> ScalarQuantity: ...
    
    def __truediv__(self, other: Union[QOPERABLE[T_], QMultiplyable[T_]]):
        if isinstance(other, Union[ScalarLike, Scalar]):
            result = self.value / other
            return ScalarQuantity(result, self.units)
        if isinstance(other, ScalarQuantity):
            return ScalarQuantity(self.value/other.value, self.units/other.units)
        raise ValueError(f'Operacion / no permitida entre {type(self)} / {type(other)}.')
    
    def __rtruediv__(self, other: ScalarLike) -> ScalarQuantity:
        return Quantity(other / self.value, self.units**(-1))
    
    def __pow__(self, other: Union[ScalarLike, Scalar, ScalarQuantity]) -> ScalarQuantity:
        if isinstance(other, ScalarQuantity):
            if not other.units.is_one():
                raise ValueError(f'Sólo se puede elevar a una cantidad adimensional. ({str(self)})^({str(other)})')
            other = other.value
        if isinstance(other, Scalar):
            other = other.value
        if isinstance(other, complex):
            raise ValueError(f'El exponente debe ser real no ({other})')
        return ScalarQuantity(self.value.value ** other, self.units ** other)

    # ---------- comparadores ------------------------------------------------
    def _cmp(self, other: object, op: str) -> bool:
        if isinstance(other, Union[ScalarLike, Scalar]):
            other = ScalarQuantity(other)
        if isinstance(other, ScalarQuantity):
            a = self.value
            b = other.value
        else:
            raise NotImplementedError

        if self.units != other.units:
            raise ValueError("Las unidades deben coincidir para comparar.")
        
        match op:
            case "==": return a == b
            case "!=": return a != b
            case "<":  return a < b
            case "<=": return a <= b
            case ">":  return a > b
            case ">=": return a >= b
            case _:   raise NotImplementedError(op)

    def __eq__(self, other: object) -> bool: return self._cmp(other, "==")
    def __ne__(self, other: object) -> bool: return self._cmp(other, "!=")
    def __lt__(self, other: object) -> bool: return self._cmp(other, "<")
    def __le__(self, other: object) -> bool: return self._cmp(other, "<=")
    def __gt__(self, other: object) -> bool: return self._cmp(other, ">")
    def __ge__(self, other: object) -> bool: return self._cmp(other, ">=")

        
    def __float__(self) -> float:
        return float(self.value.real if isinstance(self.value, complex) else self.value)

    def __int__(self) -> int:
        return int(self.value.real if isinstance(self.value, complex) else self.value)
