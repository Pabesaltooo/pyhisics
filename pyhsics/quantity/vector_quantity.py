from dataclasses import dataclass
from typing import Union

from ..linalg import T_Vector
from ..units import Unit
from ..linalg import Vector, Point

from .utils_quantity import process_unit_and_value
from .base_quantity import Operable
from .quantity_quantity import Quantity
from .scalar_quantity import ScalarQuantity

def vectorize(other: Operable) -> 'VectorQuantity':
    if isinstance(other, Vector):
        return VectorQuantity(other)
    elif isinstance(other, VectorQuantity):
        return other
    else:
        raise TypeError("El operando no es convertible a VectorQuantity. Se esperaba un Vector o VectorQuantity.")


@dataclass(frozen=True, slots=True)
class VectorQuantity(Quantity): # Quiero que tambien sea de vectorial para que tenga los atributos necerasios sin reescribirlo.
    """
    Representa una magnitud vectorial: Vector + unidad (fundamental o compuesta).
    Todas las componentes del vector comparten la misma unidad.
    """
    _value: Vector
    
    @property
    def value(self) -> Vector:
        return self._value
      
    def __init__(self, value: Union[Vector, T_Vector], unit: Union[str,Unit] = '1') -> None:        
        new_val, new_unit = process_unit_and_value(value, unit)
        if not isinstance(new_val, Vector):
            raise TypeError("El valor debe ser de tipo Vector o convertible a Vector.")
        object.__setattr__(self, "_value", new_val)
        object.__setattr__(self, "_units", new_unit)
    
    def __matmul__(self, other: Operable) -> 'VectorQuantity':
        return self.cross(other)

    def magnitude(self) -> ScalarQuantity:
        mag = self.value.magnitude
        return ScalarQuantity(mag, self.units)
    
    def dot(self, other: Operable) -> ScalarQuantity:
        other = vectorize(other)
        result = self.__mul__(other)
        if isinstance(result, ScalarQuantity):
            return result
        raise ArithmeticError
    
    def cross(self, other: Operable) -> 'VectorQuantity':
        other = vectorize(other)
        return VectorQuantity(
            self.value.cross(other.value), 
            self.units * other.units)

    def angle(self, other: Operable) -> ScalarQuantity:
        raise NotImplementedError
        other = vectorize(other)
        return ScalarQuantity(self.value.angle(other.value), 'rad')
    
    def distance(self, other: Union[Operable, Point]) -> ScalarQuantity:
        raise NotImplementedError
        if not isinstance(other, Point):
            other = vectorize(other).value
        return ScalarQuantity(self.value.distance(other), 'm')
    
    def norm(self) -> 'VectorQuantity':
        return VectorQuantity(self.value.norm())

    def __round__(self, n: int = 2) -> Quantity:
        return VectorQuantity(round(self.value, n), self.units)

    def __str__(self) -> str:
        """
        Representación en cadena con formato decimal corto.
        """
        return f"{self.value} ({self.units})"
        
    def __repr__(self) -> str:
        try:
            get_ipython() # type: ignore
            self.display_latex()
            return ''
        except NameError:
            return f"VectorQuantity(vector={self.value},\n\tunit={self.units})"
