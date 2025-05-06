from typing import Dict, FrozenSet, List, Tuple, Union
from .basic_typing import *
from .unit_composition import UnitComposition

class UnitAliasManager:
    """
    Maneja los alias para composiciones de unidades.
    """
    _aliases: Dict[FrozenSet[tuple[FundamentalUnit, RealLike]], List[str]] = {}
    
    def __getitem__(self, key: str) -> UnitDict:
        """
        Permite acceder a las unidades mediante indexación como un diccionario.
        """
        return self.get_units_dict(key)
    
    @classmethod
    def get_alias(cls, unit_set: FrozenSet[Tuple[FundamentalUnit, RealLike]]) -> Union[str, None]:
        """
        Devuelve el primer alias asociado a la composición representada por unit_set, si existe.
        """
        aliases = cls._aliases.get(unit_set)
        return aliases[0] if aliases else None

    @classmethod
    def add_alias(cls, units: Union[str, UnitComposition, UnitDict], alias: str) -> None:
        """
        Registra un alias para la composición de unidades.
        
        Parámetros:
        - units: Puede ser una cadena, una instancia de UnitComposition o un diccionario (UnitDict).
        - alias: El alias a asociar, por ejemplo, "N" para newton.
        """
        if isinstance(units, str):
            units = UnitComposition.from_str(units).unit_dict
        if isinstance(units, UnitComposition):
            units = units.unit_dict

        key = frozenset((unit, power) for unit, power in units.items() if power != 0)
        if key in cls._aliases:
            if alias not in cls._aliases[key]:
                cls._aliases[key].insert(0, alias)
        else:
            cls._aliases[key] = [alias]
    
    @classmethod
    def add_aliases(cls, units: Union[str, UnitComposition, UnitDict], aliases: List[str]) -> None:
        """
        Registra múltiples alias para una misma composición de unidades.
        """
        for alias in aliases:
            cls.add_alias(units, alias)
    
    @classmethod
    def get_units_dict(cls, unit: str = '1') -> UnitDict:
        """
        Devuelve el diccionario de unidades (UnitDict) asociado al alias proporcionado.
        Si no se encuentra el alias, lanza una excepción.
        """
        for units, aliases in cls._aliases.items():
            if unit in aliases:
                return dict(units)
        raise KeyError(f"Unidad desconocida: {unit}. Prueba a añadirla con add_alias.")
    
    @classmethod
    def aliases(cls) -> Dict[FrozenSet[Tuple[FundamentalUnit, RealLike]], List[str]]:
        """
        Devuelve el diccionario interno de alias.
        """
        return cls._aliases
    
    @classmethod
    def reset(cls, all: bool=False) -> None:
        """
        Reinicia la memoria interna de alias.
        Útil en entornos como Jupyter para borrar los alias previamente registrados.
        
        all: Si esta activado se borra y no se inician lo default. 
        """
        cls._aliases.clear()
        if not all:
            from .more_units import add_derived_units_to_alias_manager
            add_derived_units_to_alias_manager()
    
    def __repr__(self) -> str:
        text = ''
        for alias in self._aliases:
            text += f'{(self._aliases[alias][0])} -> {repr(dict(alias))} \n'
        return text

