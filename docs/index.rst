**Pyhsics** - Librería de Cálculos Físicos
===================================

Bienvenido a la documentación de Fisica, una librería para realizar cálculos físicos utilizando unidades, medidas y más.

Índice:
-------

.. toctree::
   :maxdepth: 2
   :caption: Contenidos

   unit
   unit_composition
   fundamental_unit
   prefixed_unit
   parser
   unit_alias_manager
   more_units
   tests/test_units/test_unit
   tests/test_units/test_prefixed_unit
   tests/test_units/test_parser
   tests/test_units/test_unit_alias_manager

Unidades y Cálculos:
-------------------

- **Unit**: Representa unidades físicas y permite operaciones aritméticas entre ellas.
- **UnitComposition**: Representa una composición de unidades físicas.
- **FundamentalUnit**: Enumeración de las unidades fundamentales del SI.
- **PrefixedUnit**: Extiende `UnitComposition` para trabajar con unidades prefijadas.

Pruebas:
--------

La librería incluye una suite de pruebas unitarias para garantizar la validez de las funcionalidades:

- **Pruebas de `Unit`**
- **Pruebas de `PrefixedUnit`**
- **Pruebas de `Parser`**
- **Pruebas de `UnitAliasManager`**
