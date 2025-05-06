from __future__ import annotations
import math
from typing import Tuple, Union, TYPE_CHECKING, SupportsFloat

from ..linalg import ScalarLike, Scalar
from ..units import Unit

if TYPE_CHECKING:
    from .base_measure import MeasureBaseClass
    from .direct_measure import DirectMeasure
    
Operable = Union[ScalarLike, Scalar, 'MeasureBaseClass']

def round_significant_error(error: SupportsFloat, sig: int = 1) -> float:
    error = float(error)
    if error == 0:
        return 0
    exponent = math.floor(math.log10(abs(error)))
    factor = 10 ** (-exponent + sig - 1)
    return round(error * factor) / factor

def round_by_error(value: float, error: float) -> float:
    """
    Redondea 'value' según la magnitud del 'error'.
    Si error >= 1 se redondea a múltiplos de 10^(n-1), si error < 1 a la cantidad de decimales necesaria.
    """
    error = abs(error)
    if error == 0:
        return value

    exponent = math.floor(math.log10(error))
    if exponent >= 0:
        factor = 10 ** exponent
        return round(value / factor) * factor
    else:
        decimals = -exponent
        return round(value, decimals)

def round_measure(value: SupportsFloat, error: SupportsFloat) -> Tuple[float, float]:
    value, error = float(value), float(error)
    error_rounded = round_significant_error(error, 1)
    value_rounded = round_by_error(value, error_rounded)
    value_rounded = int(value_rounded) if value_rounded.is_integer() else value_rounded
    error_rounded = int(error_rounded) if error_rounded.is_integer() else error_rounded
    return value_rounded, error_rounded


def operable_to_measure(dm: Operable) -> DirectMeasure:
    from .calculated_measure import CalculatedMeasure
    from .direct_measure import DirectMeasure
    if isinstance(dm, Scalar):
        dm = dm.value
    if isinstance(dm, int):
        return DirectMeasure(dm, 0.0001)
    elif isinstance(dm, float):
        error = float(f"1e-{len(str(dm).split('.')[1])}")
        return DirectMeasure(dm, error)
    elif isinstance(dm, CalculatedMeasure):
        return dm.as_direct_measure()
    else:
        return DirectMeasure(dm.value.value, dm.error.value, dm.units)


def get_prefix_and_composition(unit: Union[str,Unit]):
    if isinstance(unit, str):
        converted_unit = Unit(unit)
    else:
        converted_unit = unit
    prefix = converted_unit.prefix
    composition = converted_unit.composition
    return prefix, composition

def process_measure_error_unit(value: Union[ScalarLike, Scalar], error: ScalarLike, 
                            unit: Union[str, Unit]
                            ) -> Tuple[ScalarLike,ScalarLike, Unit]:
    """
    Procesa el valor y la unidad, aplicando el factor del prefijo y creando la instancia de Unit.
    """    
    value = float(value)
    prefix, composition = get_prefix_and_composition(unit)
    new_val = prefix * value
    new_err = prefix * error
    new_unit = Unit.from_unit_composition(composition)
    return new_val, new_err, new_unit