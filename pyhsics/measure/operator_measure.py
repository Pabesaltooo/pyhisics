from dataclasses import dataclass
from math import sqrt

from ..units import Unit
from .direct_measure import DirectMeasure
from .utils_measure import *

@dataclass(frozen=True)
class MeasureAlgebraicOperator:
    """
    Clase que implementa las operaciones aritméticas entre medidas,
    aplicando la propagación de errores.
    """
    @classmethod
    def _init(cls, measure1: Operable, measure2: Operable) -> Tuple[Tuple[float, float, Unit], Tuple[float, float, Unit]]:
        M1 = operable_to_measure(measure1)
        M2 = operable_to_measure(measure2)
        
        unit1 = M1.units
        unit2 = M2.units
        
        v1 = float(M1.value)
        e1 = float(M1.error)
        
        v2 = float(M2.value)
        e2 = float(M2.value)
        
        return (v1, e1, unit1), (v2, e2, unit2)
        
    @classmethod
    def sum(cls, measure1: Operable, measure2: Operable) -> DirectMeasure:
        (v1, e1, unit1), (v2, e2, unit2) = cls._init(measure1, measure2)
        if unit1 != unit2:
            raise ValueError(f"Las unidades no son compatibles: {unit1} vs {unit2}")
        new_value = v1 + v2
        new_error = sqrt(e1**2 + e2**2)
        return DirectMeasure(new_value, new_error, unit1)       
    
    @classmethod
    def mul(cls, measure1: Operable, measure2: Operable) -> DirectMeasure:
        (v1, e1, unit1), (v2, e2, unit2) = cls._init(measure1, measure2)
        new_value  = abs(v1 * v2)
        rel_error1 = e1 / abs(v1) if v1 else 0
        rel_error2 = e2 / abs(v2) if v2 else 0
        new_error = new_value * sqrt(rel_error1 ** 2 + rel_error2 ** 2)
        return DirectMeasure(new_value, new_error, unit1*unit2)
    
    @classmethod
    def div(cls, measure1: Operable, measure2: Operable) -> DirectMeasure:
        (v1, e1, unit1), (v2, e2, unit2) = cls._init(measure1, measure2)
        if v2 == 0:
            raise ZeroDivisionError
        new_value = abs(v1 / v2)
        rel_error1 = e1 / abs(v1) if v1 else 0
        rel_error2 = e2 / abs(v2) if v2 else 0
        new_error = new_value * sqrt(rel_error1**2 + rel_error2**2)
        new_units = unit1 / unit2
        return DirectMeasure(new_value, new_error, new_units)
    
    @classmethod
    def pow(cls, measure1: Operable, measure2: Operable) -> DirectMeasure:
        (base, e1, unit1), (exponent, _, unit2) = cls._init(measure1, measure2)
        if not unit2.is_one:
            raise ValueError("El exponente debe ser un número adimensional.")
        
        new_value = base ** exponent
        
        rel_error = e1 / abs(base) if base else 0
        new_error = abs(new_value) * abs(exponent) * rel_error
        new_unit = unit1 ** exponent
        return DirectMeasure(new_value, new_error, new_unit)