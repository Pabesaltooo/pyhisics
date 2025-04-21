Unit
====

La clase ``Unit`` permite representar y manipular unidades físicas. Cada instancia de esta clase corresponde a una unidad física que puede estar compuesta de varias unidades fundamentales (como `kg`, `m`, `s`, etc.) y puede tener un prefijo (como `km`).

Atributos:
---------

- **`formula`**: La fórmula que representa la unidad en formato de cadena.
- **`prefix`**: El prefijo multiplicador de la unidad (por ejemplo, `1e3` para kilómetros).
- **`composition`**: La composición de unidades representada por `UnitComposition`.
- **`alias`**: Un alias opcional para la unidad (como `"N"` para newton).

Métodos:
--------

- **`__init__(self, data: str)`**: Inicializa una unidad a partir de una cadena que representa la fórmula. Si se incluye un alias (por ejemplo, `N = kg * m / s**2`), se asigna.
- **`from_prefixed_unit(cls, prefixed_unit: 'PrefixedUnit') -> 'Unit'`**: Crea una unidad a partir de un `PrefixedUnit`.
- **`from_unit_composition(cls, unit_composition: 'UnitComposition') -> 'Unit'`**: Crea una unidad a partir de una `UnitComposition`.
- **`__str__(self) -> str`**: Devuelve una representación en cadena de la unidad, incluyendo el prefijo si es diferente de 1.
- **`__repr__(self) -> str`**: Representación oficial de la unidad.
- **`__eq__(self, other: object) -> bool`**: Compara si dos unidades son iguales.
- **`__mul__(self, other: 'Unit') -> 'Unit'`**: Multiplica dos unidades.
- **`__truediv__(self, other: 'Unit') -> 'Unit'`**: Divide dos unidades.
- **`__pow__(self, other: Number) -> 'Unit'`**: Eleva la unidad a un exponente.

Ejemplo de uso:
---------------
```python
from pyhsics.units.unit import Unit

# Crear una unidad a partir de una fórmula
unit = Unit("kg * m / s**2")
print(unit)  # Salida: kg * m / s^2
