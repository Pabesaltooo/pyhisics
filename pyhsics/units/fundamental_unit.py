from enum import Enum

class FundamentalUnit(Enum):
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

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"<{self.name}>"
    
    
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