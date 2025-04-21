from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Union

from ..linalg import T_Scalar
from ..units import Unit
from ..linalg import *

from .operator_quantity import Operable
from .utils_quantity import T2Algebraic

if TYPE_CHECKING:
    from quantity_quantity import Quantity

@dataclass(frozen=True)
class BaseQuantity(ABC):
        
    @property
    @abstractmethod
    def value(self) -> Algebraic: ...
    
    @property
    @abstractmethod
    def units(self) -> Unit: ...
    
    @property
    @abstractmethod
    def is_zero(self) -> bool: ...
    # ---------------- Métodos abstractos ---------------- 
        
    @abstractmethod
    def __add__(self, other: Operable) -> Quantity: ...
    
    @abstractmethod
    def __mul__(self, other: Operable) -> 'Quantity': ...

    @abstractmethod
    def __truediv__(self, other: Operable) -> 'Quantity': ...

    @abstractmethod
    def __rtruediv__(self, other: Operable) -> 'Quantity': ...
           
    @abstractmethod
    def __neg__(self) -> 'Quantity': ...
    
    @abstractmethod
    def __pow__(self, other: T_Scalar) -> 'Quantity': ...
    
    @abstractmethod
    def __float__(self) -> float: ...
    
    @abstractmethod
    def __abs__(self) -> 'Quantity': ...

    @abstractmethod
    def __copy__(self) -> 'Quantity': ...
    
    @abstractmethod
    def __round__(self, n: int = 2) -> 'Quantity': ...
    
    # ---------------- Métodos comparativos ---------------- 
    
    def __eq__(self, other: object) -> bool:
        """
        Igualdad (==) entre dos objetos BaseQuantity.
        """
        if not isinstance(other, BaseQuantity):
            return NotImplemented 

        return self.units == other.units and self.value == other.value
    
    def __ne__(self, other: object) -> bool:
        """
        Desigualdad (!=) entre dos objetos BaseQuantity.
        """
        result = self.__eq__(other)
        return NotImplemented if result is NotImplemented else not result
        
    def __lt__(self, other: object) -> bool:
        """
        Menor que (<) comparación entre objetos BaseQuantity.
        """
        if not isinstance(other, BaseQuantity):
            return NotImplemented

        if not (isinstance(self.value, T_Scalar) and isinstance(other.value, T_Scalar)):
            return NotImplemented

        return self.units == other.units and self.value < other.value

    def __le__(self, other: object) -> bool:
        """
        Menor o igual que (<=) comparación entre objetos BaseQuantity.
        """
        if not isinstance(other, BaseQuantity):
            return NotImplemented

        return self < other or self == other

    def __gt__(self, other: object) -> bool:
        """
        Mayor que (>) comparación entre objetos BaseQuantity.
        """
        if not isinstance(other, BaseQuantity):
            return NotImplemented

        return other.value < self.value  # Se invierte la comparación de __lt__

    def __ge__(self, other: object) -> bool:
        """
        Mayor o igual que (>=) comparación entre objetos BaseQuantity.
        """
        if not isinstance(other, BaseQuantity):
            return NotImplemented

        return self > other or self == other
        
    # ---------------- Operaciones Aritméticas ---------------- 
    
    def __radd__(self, other: Operable) -> 'Quantity':
        return self.__add__(other)
    
    def __sub__(self, other: Operable) -> 'Quantity':
        if not isinstance(other, Union[Algebraic, BaseQuantity]):
            other = T2Algebraic(other)
        return self.__add__(other.__neg__())
    
    def __rsub__(self, other: Operable) -> 'Quantity':
        return (self.__sub__(other)).__neg__()
    
    def __rmul__(self, other: Operable) -> 'Quantity':
        return self.__mul__(other)
    
        
    def __hash__(self) -> int:
        """ Permite el uso de BaseQuantity como clave en diccionarios. """
        return hash((self.value, self.units))
