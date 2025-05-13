from __future__ import annotations

from math import floor, log10
from typing import TYPE_CHECKING, Optional, Tuple, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from IPython.display import display, Latex #type: ignore

from ..printing.printable import Printable
from ..quantity import ScalarQuantity
from ..units import Unit
from .utils_measure import Operable, operable_to_measure

if TYPE_CHECKING:
    from .direct_measure import DirectMeasure


@dataclass(frozen=True)
class MeasureBaseClass(Printable, ABC):
    """
    Clase base para medidas que define el comportamiento común, incluidos
    los operadores aritméticos. 
    """
    
    @property
    @abstractmethod
    def value(self) -> ScalarQuantity:
        pass
    
    @property
    @abstractmethod
    def error(self) -> ScalarQuantity:
        pass
    
    @property
    @abstractmethod
    def units(self) -> Unit: 
        pass
    
    @abstractmethod
    def __neg__(self) -> 'DirectMeasure':
        pass

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        pass
    
    @abstractmethod
    def _repr_latex_(self, name: Optional[str] = None) -> str:
        """Crea un string para representar el objeto en LaTex"""
        pass
    
    def __add__(self, other: Operable) -> 'DirectMeasure':
        from .operator_measure import MeasureAlgebraicOperator
        return MeasureAlgebraicOperator.sum(self, other)

    def __sub__(self, other: Operable) -> 'DirectMeasure':
        return self.__add__(-other)

    def __rsub__(self, other: Operable) -> 'DirectMeasure':
        return (-self).__add__(other)

    def __mul__(self, other: Operable) -> "DirectMeasure":
        from .operator_measure import MeasureAlgebraicOperator
        return MeasureAlgebraicOperator.mul(self, other)

    def __rmul__(self, other: Operable) -> 'DirectMeasure':
        """Multiplicación Asociativa (a·b = b·a)"""
        return self.__mul__(other)

    def __truediv__(self, other: Operable) -> "DirectMeasure":
        from .operator_measure import MeasureAlgebraicOperator
        return MeasureAlgebraicOperator.div(self, other)

    def __rtruediv__(self, other: Operable) -> "DirectMeasure":
        other = operable_to_measure(other)
        from .operator_measure import MeasureAlgebraicOperator
        return MeasureAlgebraicOperator.div(self, other)

    def __pow__(self, other: Operable) -> "DirectMeasure":
        from .operator_measure import MeasureAlgebraicOperator
        return MeasureAlgebraicOperator.pow(self, other)
        
    def normalice_str(self) -> Tuple[Union[int,  float], Union[int,  float], int]:
        """value, error, exp"""
        from .utils_measure import round_measure
        value_rnd, error_rnd = round_measure(self.value, self.error)
        # Extraemos el exponente a partir del valor redondeado
        exponent = floor(log10(abs(error_rnd)))
        factor: int = 10 ** exponent
        # Normalizamos dividiendo por el factor
        value_norm = value_rnd / factor
        error_norm = error_rnd / factor
        value_norm = int(value_norm) if value_norm.is_integer() else value_norm
        error_norm = int(error_norm) if error_norm.is_integer() else error_norm
        return (value_norm, error_norm, exponent)
