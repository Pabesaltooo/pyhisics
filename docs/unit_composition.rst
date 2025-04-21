Fisica - Librería de Cálculos Físicos
===================================

Bienvenido a la documentación de la librería Fisica. Esta librería proporciona herramientas para trabajar con unidades físicas fundamentales, cantidades, medidas y más.

FundamentalUnit
===============

La clase ``FundamentalUnit`` es una enumeración que representa las unidades fundamentales del Sistema Internacional de Unidades (SI). Cada unidad en la enumeración tiene un valor que corresponde a su símbolo o nombre.

Ejemplo de uso:
---------------

```python
from pyhsics.units.unit import FundamentalUnit

# Crear una instancia de la unidad de masa
unit = FundamentalUnit.MASS

# Mostrar el valor de la unidad
print(unit)  # Salida: 'kg'

# Obtener la representación en consola de la unidad
print(repr(unit))  # Salida: <MASS>
```

Métodos:
--------

1. **`__str__(self)`**:
   - Retorna una cadena de texto que representa el valor de la unidad.
   - Ejemplo: `str(FundamentalUnit.MASS)` retorna `'kg'`.

2. **`__repr__(self)`**:
   - Retorna una representación más formal de la unidad, útil para depuración.
   - Ejemplo: `repr(FundamentalUnit.MASS)` retorna `'<MASS>'`.

Orden de las unidades:
----------------------

La lista ``UNIT_ORDER`` proporciona el orden sugerido para mostrar las unidades. El orden sigue una secuencia lógica basada en las categorías del SI:

1. Masa (kg)
2. Ángulo (rad)
3. Distancia (m)
4. Tiempo (s)
5. Luz (cd)
6. Temperatura (K)
7. Corriente eléctrica (A)
8. Cantidad de sustancia (mol)
9. Adimensional (1)

Ejemplo de orden de unidades:

```python
from pyhsics.units.unit import UNIT_ORDER

for unit in UNIT_ORDER:
    print(unit)
```