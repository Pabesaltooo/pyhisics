from dataclasses import dataclass
from typing import Union, Any

from ..linalg import T_Scalar

from .basic_typing import UnitDict
from .unit_composition import UnitComposition


@dataclass(frozen=True, slots=True)
class PrefixedUnit(UnitComposition):
    prefix: T_Scalar = 1.0

    def __init__(self, prefix: T_Scalar, units: Union[UnitComposition, UnitDict]) -> None:
        # Si 'units' es una instancia de UnitComposition, extraemos su diccionario
        if isinstance(units, UnitComposition):
            units = units.unit_dict
        object.__setattr__(self, 'prefix', prefix)
        object.__setattr__(self, 'unit_dict', units)

    def __str__(self) -> str:
        # Llamamos directamente al método __str__ de UnitComposition para evitar problemas con super()
        base_str = UnitComposition.__str__(self)
        if self.prefix == 1.0:
            return base_str
        return f"{self.prefix} {base_str}"

    def simplify(self) -> Union['PrefixedUnit', UnitComposition]:
        """Si el prefijo es 1.0, devuelve la composición subyacente."""
        if self.prefix == 1.0:
            return UnitComposition(self.unit_dict)
        return self

    def __mul__(self, other: Any) -> 'PrefixedUnit':
        if not isinstance(other, PrefixedUnit):
            return NotImplemented
        new_prefix = self.prefix * other.prefix
        # Llamamos directamente al método de la clase base
        new_comp = UnitComposition.__mul__(self, other)
        return PrefixedUnit(new_prefix, new_comp.unit_dict)
        
    def __truediv__(self, other: Any) -> 'PrefixedUnit':
        if not isinstance(other, PrefixedUnit):
            return NotImplemented
        new_prefix = self.prefix / other.prefix
        new_comp = UnitComposition.__truediv__(self, other)
        return PrefixedUnit(new_prefix, new_comp.unit_dict)

    def __pow__(self, exponent: T_Scalar) -> 'PrefixedUnit':
        new_prefix = self.prefix ** exponent
        new_comp = UnitComposition.__pow__(self, exponent)
        return PrefixedUnit(new_prefix, new_comp.unit_dict)

    def __iter__(self):
        return iter((self.prefix, self.unit_dict))
    