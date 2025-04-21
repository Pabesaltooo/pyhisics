from .alias_manager import UnitAliasManager
from .more_units import add_derived_units_to_alias_manager
from .unit import Unit

# Inicializamos el alias manager con unidades predefinidas.
add_derived_units_to_alias_manager()

ONE_UNIT = Unit('1') # TODO Implementar que esto sea False

__all__ = ['Unit',
           'UnitAliasManager']

