"""
Módulo quantity:
Define las clases y funciones para representar cantidades físicas (escalares y vectoriales),
incluyendo operaciones aritméticas y conversiones de unidades.
"""
from __future__ import annotations
from typing import Union
from IPython.display import display, Latex #type: ignore

from ..linalg import Scalar, T_Scalar, Algebraic, T_Algebraic
from ..units import Unit

from .base_quantity import BaseQuantity, Operable
from .utils_quantity import process_unit_and_value


class Quantity(BaseQuantity):  
    def __init__(self, value: Union[Algebraic, T_Algebraic], 
                 unit: Union[str,Unit] = '1') -> None:
        
        new_val, new_unit = process_unit_and_value(value, unit)
        
        self._value = new_val
        self._units = new_unit
        
    @property
    def value(self) -> Algebraic:
        return self._value
    
    @property
    def units(self) -> Unit:
        return self._units
    
    @property
    def is_zero(self) -> bool:
        return self.value.is_zero
    
        
    def __add__(self, other: Operable) -> 'Quantity':
        if not isinstance(other, BaseQuantity):
                other = Quantity(other)
        from .operator_quantity import QuantityOperator
        return  QuantityOperator(self, other).sum()
        
    def __mul__(self, other: Operable) -> 'Quantity':
        if not isinstance(other, BaseQuantity):
            other = Quantity(other)
        from .operator_quantity import QuantityOperator
        return  QuantityOperator(self, other).mul()
    
    def __truediv__(self, other: Operable) -> 'Quantity':
        if not isinstance(other, BaseQuantity):
            other = Quantity(other)
        from .operator_quantity import QuantityOperator
        return  QuantityOperator(self, other).div()
    
    def __pow__(self, other: Operable) -> 'Quantity':
        if not isinstance(other, BaseQuantity):
            other = Quantity(other) 
        if not other.units.is_one:
            raise ValueError('El exponente debe ser adimensional.')    
        if not isinstance(other.value, Scalar):
            raise TypeError(f"Operación de potencia no soportada para estos tipos. {type(self.value)} vs {type(other)}")    
    
        return Quantity(self.value ** other.value, 
                        self.units ** other.value.value)
            
    def __float__(self) -> float:
        if isinstance(self.value, Scalar):
            return float(self.value.value)
        else:
            raise NotImplementedError
    
    def __rtruediv__(self, other: Operable) -> 'Quantity':
        if not isinstance(other, BaseQuantity):
            other = Quantity(other)
        from .operator_quantity import QuantityOperator
        return  QuantityOperator(other, self).div()

    def __neg__(self) -> 'Quantity':
        if isinstance(self.value, T_Scalar):
            return Quantity(-self.value, self.units)
        else:
            return Quantity(-self.value, self.units)
        
    def __abs__(self) -> 'Quantity':
        if isinstance(self.value, Scalar):
            return Quantity(
                abs(self.value),
                self.units)
        return NotImplemented
        
    def __round__(self, n: int = 2) -> 'Quantity':
        return Quantity(round(self.value, n), self.units)
            
    def __copy__(self) -> 'Quantity':
        return Quantity(self.value, self.units)
    
    def __str__(self) -> str:
        return f'{self.value} ({self.units})'    
    
    def _latex(self) -> str:
        return "$" + self.value.latex() + "\\;" + self.units.latex() + "$"
    
    def display_latex(self):
        display(Latex(self._latex()))
    
    def __repr__(self) -> str:
        try:
            get_ipython() # type: ignore
            self.display_latex()
            return ''
        except NameError:
            return f'Quantity(value={self.value}, units={self.units})'
