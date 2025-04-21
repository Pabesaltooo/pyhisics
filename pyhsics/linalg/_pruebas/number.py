from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Union

from dataclasses import dataclass
from .printable import Printable

class InAlgebraicGroup(ABC):
    """
    Abstract base class representing an element in an algebraic group.
    This class defines the interface for objects that behave as elements of an algebraic group,
    requiring implementations for checking the zero element, the identity element, and for
    computing the additive inverse (negation) and the multiplicative inverse.  ç
    
    Methods:
    
    - `is_zero() -> bool`
        - Returns True if the element is the zero element of the group, otherwise False.
    - `is_identity() -> bool`
        - Returns True if the element is the identity element of the group, otherwise False.
    - `neg() -> InAlgebraicGroup`
        - Returns the additive inverse (negation) of the element.
    - `inv() -> InAlgebraicGroup`
        - Returns the multiplicative inverse of the element.
    """
    
    @abstractmethod
    def is_zero(self) -> bool:
        pass
    
    @abstractmethod
    def is_identity(self) -> bool:
        pass 
    
    @abstractmethod
    def neg(self) -> InAlgebraicGroup:
        pass
    
    @abstractmethod
    def inv(self) -> InAlgebraicGroup:
        pass

 
T_Numeric = Union[int, complex, float]

@dataclass(frozen=True)
class Number(InAlgebraicGroup, Printable):
    """Una clase que soporta, guarda y opera con int, float, decimal, complex, real y demas, seria como un cuerpo algebraic"""
    value: Union[int, float, complex]
    
    def __post_init__(self):
        if not isinstance(self.value, T_Numeric): # type: ignore
            print(f'WARNING: {self.value} es tipo {type(self.value)}')
            return self.value
    
    def __neg__(self) -> Number:
        return self.neg()

    def __add__(self, other: Union[Number, T_Numeric]) -> Number:
        from .symbolic import SupportsSymbolic 
        if isinstance(other, SupportsSymbolic):  
            return other.to_expression().__radd__(self) # type: ignore
        if not isinstance(other, Number):
            other = Number(other)
        return Number(self.value + other.value)

    def __radd__(self, other: Union[Number, T_Numeric]) -> Number:
        from .symbolic import SupportsSymbolic 
        if isinstance(other, SupportsSymbolic):  
            return other.to_expression().__add__(self) # type: ignore
        if not isinstance(other, Number):
            other = Number(other)
        return Number(other.value + self.value)

    def __sub__(self, other: Union[Number, T_Numeric]) -> Number:
        from .symbolic import SupportsSymbolic 
        if isinstance(other, SupportsSymbolic):  
            return other.to_expression().__rsub__(self) # type: ignore
        if not isinstance(other, Number):
            other = Number(other)
        return Number(self.value - other.value)

    def __rsub__(self, other: Union[Number, T_Numeric]) -> Number:
        from .symbolic import SupportsSymbolic 
        if isinstance(other, SupportsSymbolic):  
            return other.to_expression().__sub__(self) # type: ignore
        if not isinstance(other, Number):
            other = Number(other)
        return Number(other.value - self.value)

    def __mul__(self, other: Union[Number, T_Numeric]) -> Number:        
        from .symbolic import SupportsSymbolic 
        if isinstance(other, SupportsSymbolic):  
            return other.to_expression().__rmul__(self) # type: ignore
        if not isinstance(other, Number):
            other = Number(other)
        return Number(self.value * other.value)

    def __rmul__(self, other: Union[Number, T_Numeric]) -> Number:
        from .symbolic import SupportsSymbolic 
        if isinstance(other, SupportsSymbolic):  
            return other.to_expression().__mul__(self) # type: ignore
        if not isinstance(other, Number):
            other = Number(other)
        return Number(other.value * self.value)

    def __truediv__(self, other: Union[Number, T_Numeric]) -> Number:
        from .symbolic import SupportsSymbolic 
        if isinstance(other, SupportsSymbolic):  
            return other.to_expression().__rtruediv__(self) # type: ignore
        if not isinstance(other, Number):
            other = Number(other)
        return Number(self.value / other.value)

    def __rtruediv__(self, other: Union[Number, T_Numeric]) -> Number:
        from .symbolic import SupportsSymbolic 
        if isinstance(other, SupportsSymbolic):  
            return other.to_expression().__truediv__(self) # type: ignore
        if not isinstance(other, Number):
            other = Number(other)
        return Number(other.value / self.value)

    def __pow__(self, other: Union[Number, T_Numeric]) -> Number:
        from .symbolic import SupportsSymbolic 
        if isinstance(other, SupportsSymbolic):  
            return other.to_expression().__rpow__(self) # type: ignore
        if not isinstance(other, Number):
            other = Number(other)
        return Number(self.value ** other.value)

    def __rpow__(self, other: Union[Number, T_Numeric]) -> Number:
        from .symbolic import SupportsSymbolic 
        if isinstance(other, SupportsSymbolic):  
            return other.to_expression().__pow__(self) # type: ignore
        if not isinstance(other, Number):
            other = Number(other)
        return Number(other.value ** self.value)

    def __float__(self) -> float:
        if isinstance(self.value, complex):
            return float(self.value.real)
        return float(self.value)
    
    def __str__(self) -> str:
        return str(self.value)
    
    def _repr_latex_(self) -> str:
        if isinstance(self.value, complex):
            return f"${str(self.value).replace('j', 'i')}$"
        return f"${self.value}$"
    
    def __abs__(self) -> Number:
        return Number(abs(self.value))

    def is_zero(self) -> bool:
        return self.value == 0

    def is_identity(self) -> bool:
        return self.value == 1

    def neg(self) -> Number:
        return Number(-self.value)

    def inv(self) -> Number:
        return Number(1/self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Number):
            return self.value == other.value
        return self.value == other

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: object) -> bool:
        a = self.value
        b = other.value if isinstance(other, Number) else other
        if not isinstance(b, T_Numeric):
            raise ValueError(f'No se puede comparar un Numeric con {type(b)}')
        if isinstance(a, complex) or isinstance(b, complex):
            return abs(a) < abs(b)
        return a < b

    def __le__(self, other: object) -> bool:
        a = self.value
        b = other.value if isinstance(other, Number) else other
        if not isinstance(b, T_Numeric):
            raise ValueError(f'No se puede comparar un Numeric con {type(b)}')
        if isinstance(a, complex) or isinstance(b, complex):
            return abs(a) <= abs(b)
        return a <= b

    def __gt__(self, other: object) -> bool:
        a = self.value
        b = other.value if isinstance(other, Number) else other
        if not isinstance(b, T_Numeric):
            raise ValueError(f'No se puede comparar un Numeric con {type(b)}')
        if isinstance(a, complex) or isinstance(b, complex):
            return abs(a) > abs(b)
        return a > b

    def __ge__(self, other: object) -> bool:
        a = self.value
        b = other.value if isinstance(other, Number) else other
        if not isinstance(b, T_Numeric):
            raise ValueError(f'No se puede comparar un Numeric con {type(b)}')
        if isinstance(a, complex) or isinstance(b, complex):
            return abs(a) >= abs(b)
        return a >= b

    def __hash__(self) -> int:
        return hash(self.value)

