from typing import Union, Tuple

from ..linalg import *
from ..linalg import T2Algebraic
from ..units import Unit

def get_prefix_and_composition(unit: Union[str, Unit]):
    """Obtiene el prefijo y la composición de la unidad."""
    if isinstance(unit, str):
        converted_unit = Unit(unit)
    else:
        converted_unit = unit
    prefix = converted_unit.prefix
    composition = converted_unit.composition
    return prefix, composition

def process_unit_and_value(value: Union[Algebraic, T_Algebraic], 
                            unit: Union[str, Unit]
                            ) -> Tuple[Algebraic, Unit]:
    """
    Procesa el valor y la unidad, aplicando el factor del prefijo y creando la instancia de Unit.
    """
    prefix, composition = get_prefix_and_composition(unit)
    prefix = Scalar(prefix)  # Convertimos el prefijo a un escalar
    
    # Dependiendo del tipo de 'value', lo procesamos
    if isinstance(value, Scalar):
        new_val = prefix * value
    elif isinstance(value, Vector):
        new_val = prefix * value
    elif isinstance(value, Matrix):
        new_val = prefix * value
    else:
        new_val = prefix * T2Algebraic(value)

    # Creamos una nueva unidad usando la composición
    new_unit = Unit.from_unit_composition(composition)
    return new_val, new_unit