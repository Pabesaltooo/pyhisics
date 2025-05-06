from enum import Enum, EnumMeta
from abc import ABCMeta
from typing import Dict
from ..printing.printable import Printable

class ABCEnumMeta(EnumMeta, ABCMeta):
    pass

class FundamentalUnit(Printable, Enum, metaclass=ABCEnumMeta):
    """Enumeración de unidades fundamentales del SI."""
    ONE                 = '1'    # Adimensional
    ANGLE               = 'rad'  # Radianes (adimensional)
    LIGHT               = 'cd'   # Candela
    MASS                = 'kg'   # Masa
    TEMPERATURE         = 'K'    # Temperatura
    SUBSTANCE_QUANTITY  = 'mol'  # Cantidad de sustancia
    ELECTRIC_CURRENT    = 'A'    # Corriente eléctrica
    DISTANCE            = 'm'    # Longitud
    TIME                = 's'    # Tiempo
    MONEY               = '€'    # Dinero (adimensional)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"<{self.name}>"

    def _repr_latex_(self) -> str:
        return f'$ \\text{{{self.value}}} $'

# Orden sugerido para la representación
UNIT_ORDER = [
    FundamentalUnit.MASS,
    FundamentalUnit.ANGLE,
    FundamentalUnit.DISTANCE,
    FundamentalUnit.TIME,
    FundamentalUnit.LIGHT,
    FundamentalUnit.TEMPERATURE,
    FundamentalUnit.ELECTRIC_CURRENT,
    FundamentalUnit.SUBSTANCE_QUANTITY,
    FundamentalUnit.ONE,
]


# Diccionario de prefijos SI (clave: prefijo, valor: factor numérico)
PREFIXES_MAP: Dict[str, float] = {
    "Y": 1e24,
    "Z": 1e21,
    "E": 1e18,
    "P": 1e15,
    "T": 1e12,
    "G": 1e9,
    "M": 1e6,
    "k": 1e3,
    "h": 1e2,
    "da": 1e1,
    "d": 1e-1,
    "c": 1e-2,
    "m": 1e-3,
    "µ": 1e-6,
    "u": 1e-6,
    "n": 1e-9,
    "p": 1e-12,
    "f": 1e-15,
    "a": 1e-18,
    "z": 1e-21,
    "y": 1e-24,
}

