from __future__ import annotations
from dataclasses import dataclass
from typing import Union
from IPython.display import display, Latex # type: ignore

from .utils_quantity import process_unit_and_value
from .quantity_quantity import Quantity

from ..linalg import T_Scalar, Scalar
from ..units import Unit

@dataclass(frozen=True, slots=True)
class ScalarQuantity(Quantity):
    """
    Representa una magnitud física: valor + unidad (fundamental o compuesta).
    """
    
    _value: Scalar
    
    @property
    def value(self) -> Scalar:
        return self._value
    
    def __init__(self, value: Union[Scalar, T_Scalar], unit: Union[str,Unit] = '1') -> None:        
        new_val, new_unit = process_unit_and_value(value, unit)
        if not isinstance(new_val, Scalar):
            raise TypeError("El valor debe ser de tipo Scalar o convertible a Scalar.")
        object.__setattr__(self, "_value", new_val)
        object.__setattr__(self, "_units", new_unit)

    
    def __abs__(self) -> ScalarQuantity:
        return ScalarQuantity(abs(self.value), self.units)

    def __str__(self) -> str:
        return f"{self.value} ({self.units})"
    
    def __repr__(self) -> str:
        try:
            get_ipython() # type: ignore
            self.display_latex()
            return ''
        except NameError:
            return f"ScalarQuantity(value={self.value}, units={self.units})"
