from dataclasses import dataclass
from typing import Dict, Optional
from IPython.display import display, Latex #type: ignore

from ..linalg import ScalarLike


from .basic_typing import RealLike
from .fundamental_unit import FundamentalUnit
from .unit_composition import UnitComposition
from .prefixed_unit import PrefixedUnit
from .alias_manager import UnitAliasManager

@dataclass(frozen=True, slots=True) 
class Unit:
    """
    Clase Publica para el manejo de unidades.
    
    Entrada:
    - formula: str
    
    Atributos:
    - formula: str
    - prefix: float
    - composition: UnitComposition
    - alias: str (si la formula vine dada por N = kg*m/s**2, alias = 'N'), es decir, si hay un "=" en la formula
    
    """
    alias_manager = UnitAliasManager
    formula: str
    prefix: ScalarLike
    composition: UnitComposition
    alias: Optional[str] = None
    _visualize_formula: bool = False
    
    def __init__(self, data: str, visualize_formula: bool = False) -> None:
        formula = data
        alias = None
        if "=" in formula:
            alias, formula = map(str.strip, formula.split("=", 1))
        mapping: Dict[str, FundamentalUnit] = {unit.value: unit for unit in FundamentalUnit}

        from .parser import UnitParser, alias_resolver    
        parser = UnitParser(formula, mapping, alias_resolver)
        result = parser.parse()
    
        if alias:
            self.alias_manager.add_alias(result.unit_dict, alias)

        composition = UnitComposition(result.unit_dict)
        prefix = result.prefix
        
        object.__setattr__(self, "alias", alias)        
        object.__setattr__(self, "formula", formula)
        object.__setattr__(self, "prefix", prefix)
        object.__setattr__(self, "composition", composition)
        object.__setattr__(self, "_visualize_formula", visualize_formula)
    
    @classmethod
    def from_prefixed_unit(cls, prefixed_unit: 'PrefixedUnit') -> 'Unit':
        
        prefix = prefixed_unit.prefix
        composition = UnitComposition(prefixed_unit.unit_dict)
        
        new_unit = cls.__new__(cls)
        object.__setattr__(new_unit, "alias", None)
        object.__setattr__(new_unit, "formula", str(composition))
        object.__setattr__(new_unit, "composition", composition)
        object.__setattr__(new_unit, "prefix", prefix)
        
        return new_unit
    
    @classmethod
    def from_unit_composition(cls, unit_composition: 'UnitComposition') -> 'Unit':
        prefix = 1
        composition = unit_composition
        new_unit = cls.__new__(cls)
        object.__setattr__(new_unit, "alias", None)
        object.__setattr__(new_unit, "formula", str(composition))
        object.__setattr__(new_unit, "composition", composition)
        object.__setattr__(new_unit, "prefix", prefix)
        
        return new_unit
        
    def __str__(self) -> str:
        #if self._visualize_formula:
        #    return f'{self.formula}'
        
        base = str(self.composition)
        return base if self.prefix == 1.0 else f'{self.prefix} {base}'
    
    def display_latex(self):
        display(Latex(self._repr_latex_()))

    def _repr_latex_(self): # devuelve una string en formato laTex
        from .unit_printer import UnitPrinter
        return "$" + UnitPrinter.latex_str(self.composition.unit_dict) + "$" 
    
    def latex(self): #devuele una string en formato laTex sin $
        from .unit_printer import UnitPrinter
        return UnitPrinter.latex_str(self.composition.unit_dict)
    
    def __repr__(self) -> str:
        try:
            get_ipython() # type: ignore
            self.display_latex()
            return ''
        except NameError:
            return f'Unit({str(self)})'
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Unit):
            units = self.composition == other.composition
            prefix = self.prefix == other.prefix
            return units and prefix
        return False
    
    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash((self.formula, self.prefix))
    
    def __truediv__(self, other: 'Unit') -> 'Unit':
        new = PrefixedUnit(
            self.prefix / other.prefix,
            self.composition / other.composition
        )
        return Unit.from_prefixed_unit(new)
    
    def __mul__(self, other: 'Unit') -> 'Unit':
        new = PrefixedUnit(
            self.prefix * other.prefix,
            self.composition * other.composition
        )
        return Unit.from_prefixed_unit(new)
    
    def __pow__(self, other: RealLike) -> 'Unit':
        new = PrefixedUnit(
            self.prefix ** other,
            self.composition ** other
        )
        return Unit.from_prefixed_unit(new)
    
    @property
    def is_one(self):
        return self.composition.unit_dict == {}