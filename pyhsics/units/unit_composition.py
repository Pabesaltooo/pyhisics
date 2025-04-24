from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict
from typing import Dict, Union
from IPython.display import display, Latex #type: ignore

from .fundamental_unit import FundamentalUnit
from .basic_typing import UnitDict


@dataclass(frozen=True, slots=True)
class UnitComposition:
    """
    Representa una combinación de unidades fundamentales y sus exponentes.
    
    Ejemplo:
        kg·m/s^2 se representa como {FundamentalUnits.KG: 1, FundamentalUnits.M: 1, FundamentalUnits.S: -2}.
    """
    
    unit_dict: "UnitDict"

    def __init__(self, unit_dict: Union["UnitDict", UnitComposition]) -> None:
        if isinstance(unit_dict, UnitComposition):
            unit_dict = unit_dict.unit_dict
        if not isinstance(unit_dict, dict): #type: ignore
            raise TypeError("Se esperaba un diccionario de unidades.")
        clean_units = {u: p for u, p in unit_dict.items() if p != 0}
        object.__setattr__(self, 'unit_dict', clean_units)
           
    def __mul__(self, other: UnitComposition) -> UnitComposition:       
        new_units = defaultdict(int, self.unit_dict)        
        for unit, power in other.unit_dict.items():
            new_units[unit] += power
        return UnitComposition(dict(new_units))._clean()

    def __rmul__(self, other: UnitComposition) -> UnitComposition:
        return self.__mul__(other)

    def __truediv__(self, other: UnitComposition) -> UnitComposition:        
        new_units = defaultdict(int, self.unit_dict)            
        for unit, power in other.unit_dict.items():
            new_units[unit] -= power
        return UnitComposition(dict(new_units))._clean()

    def __rtruediv__(self, other: FundamentalUnit) -> UnitComposition:
        new_units: UnitDict = defaultdict(int, {other: 1})
        for unit, power in self.unit_dict.items():
            new_units[unit] -= power
        return UnitComposition(dict(new_units))._clean()

    def __pow__(self, exponent: float) -> UnitComposition:
        if isinstance(self.unit_dict, UnitComposition):
            return (self.unit_dict ** exponent)._clean()
        return UnitComposition({unit: power * exponent for unit, power in self.unit_dict.items()})._clean()

    def __add__(self, other: UnitComposition) -> UnitComposition:
        if self._clean().unit_dict.keys() != other._clean().unit_dict.keys():
            raise ValueError("No se pueden sumar composiciones con unidades diferentes.")
        return self

    def _clean(self) -> UnitComposition:
        """Devuelve una nueva composición sin unidades con exponente 0."""
         # Pequeño bug corregido
        cleaned: UnitDict = {unit: power for unit, power in self.unit_dict.items() if power != 0}

        return UnitComposition(cleaned)

    def __str__(self) -> str:
        from .unit_printer import UnitPrinter
        return UnitPrinter.py_str(self.unit_dict) # devuelve una str de python con los * como · y los exponentes como superindices

    def display_latex(self): 
        display(Latex(self._latex()))

    def _latex(self): # devuelve una string en formato laTex
        from .unit_printer import UnitPrinter
        return "$" + UnitPrinter.latex_str(self.unit_dict) + "$" 
    
    def latex(self): #devuele una string en formato laTex sin $
        from .unit_printer import UnitPrinter
        return UnitPrinter.latex_str(self.unit_dict)
    
    def __repr__(self) -> str:
        try:
            get_ipython() # type: ignore
            self.display_latex()
            return ''
        except NameError:
            return f"UnitComposition({self.unit_dict})"
    
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UnitComposition):
            return NotImplemented
        return self._clean().unit_dict == other._clean().unit_dict

    @classmethod
    def from_str(cls, text: str) -> UnitComposition:
        """
        Crea una UnitComposition a partir de una cadena.
        
        Ejemplo:
            UnitComposition.from_str("kg / m**2 * s**4 * s")
        """
        from .parser import UnitParser, alias_resolver
            
        mapping: Dict[str, FundamentalUnit] = {unit.value: unit for unit in FundamentalUnit}
        parser = UnitParser(text, mapping, alias_resolver)
        result = parser.parse()
        return result
