"""
Módulo de unidades derivadas.

Define constantes de unidades derivadas (por ejemplo, newton, joule, watt, etc.) 
utilizando la composición de unidades fundamentales.
"""
from .fundamental_unit import FundamentalUnit
from .unit_composition import UnitComposition
from .alias_manager import UnitAliasManager

newton = UnitComposition({
    FundamentalUnit.MASS: 1,
    FundamentalUnit.DISTANCE: 1,
    FundamentalUnit.TIME: -2
})

joule = UnitComposition({
    FundamentalUnit.MASS: 1,
    FundamentalUnit.DISTANCE: 2,
    FundamentalUnit.TIME: -2
})

watt = UnitComposition({
    FundamentalUnit.MASS: 1,
    FundamentalUnit.DISTANCE: 2,
    FundamentalUnit.TIME: -3
})

watt_m2 = UnitComposition({
    FundamentalUnit.MASS: 1,
    FundamentalUnit.TIME: -3
})

coulomb = UnitComposition({
    FundamentalUnit.ELECTRIC_CURRENT: 1,
    FundamentalUnit.TIME: 1
})

volt = UnitComposition({
    FundamentalUnit.MASS: 1,
    FundamentalUnit.DISTANCE: 2,
    FundamentalUnit.TIME: -3,
    FundamentalUnit.ELECTRIC_CURRENT: -1
})

ohm  = UnitComposition({
    FundamentalUnit.MASS: 1,
    FundamentalUnit.DISTANCE: 2,
    FundamentalUnit.TIME: -3,
    FundamentalUnit.ELECTRIC_CURRENT: -2
})

hertz = UnitComposition({
    FundamentalUnit.TIME: -1
})

pascal = UnitComposition({
    FundamentalUnit.DISTANCE: -1,
    FundamentalUnit.TIME: -2,
    FundamentalUnit.MASS: 1,
})

tesla = UnitComposition({
    FundamentalUnit.MASS: 1,
    FundamentalUnit.TIME: -2,
    FundamentalUnit.ELECTRIC_CURRENT: -1
})

farad = UnitComposition({
    FundamentalUnit.MASS: -1,
    FundamentalUnit.DISTANCE: -2,
    FundamentalUnit.TIME: 4,
    FundamentalUnit.ELECTRIC_CURRENT: 2
})

webber = UnitComposition({
    FundamentalUnit.MASS: 1,
    FundamentalUnit.TIME: -2,
    FundamentalUnit.DISTANCE: 2,
    FundamentalUnit.ELECTRIC_CURRENT: -1    
})

henrry = UnitComposition({
    FundamentalUnit.MASS: 1,
    FundamentalUnit.TIME: -2,
    FundamentalUnit.DISTANCE: 2,
    FundamentalUnit.ELECTRIC_CURRENT: -2})

ohm_m = UnitComposition({
    FundamentalUnit.MASS: 1,
    FundamentalUnit.DISTANCE: 3,
    FundamentalUnit.TIME: -3,
    FundamentalUnit.ELECTRIC_CURRENT: -2
    })

volt_m = UnitComposition({
    FundamentalUnit.MASS: 1,
    FundamentalUnit.DISTANCE: 1,
    FundamentalUnit.TIME: -3,
    FundamentalUnit.ELECTRIC_CURRENT: -1
})

def add_derived_units_to_alias_manager():
    # Al iniciar el modulo
    # Registrar las unidades derivadas en el gestor de alias
    UnitAliasManager.add_alias(newton.unit_dict, "N")   # Newton
    UnitAliasManager.add_alias(joule.unit_dict, "J")    # Julio
    UnitAliasManager.add_alias(watt.unit_dict, "W")     # Vatio
    UnitAliasManager.add_alias(coulomb.unit_dict, "C")  # Coulomb
    UnitAliasManager.add_alias(volt.unit_dict, "V")     # Volt
    UnitAliasManager.add_aliases(ohm.unit_dict, ['Ohm', 
                                            'ohm',
                                            'Ω'])# Ohm
    UnitAliasManager.add_alias(hertz.unit_dict, "Hz")   # Hertz
    UnitAliasManager.add_alias(pascal.unit_dict, "Pa")  # Pascal
    UnitAliasManager.add_alias(tesla.unit_dict, "T")    # Tesla
    UnitAliasManager.add_alias(farad.unit_dict, "F")    # Faradio
    UnitAliasManager.add_alias(webber.unit_dict, "Wb")  # Webber
    UnitAliasManager.add_alias(henrry.unit_dict, "H")
    
    UnitAliasManager.add_alias(ohm_m.unit_dict, "Ωm")
    UnitAliasManager.add_alias(watt_m2.unit_dict, "W/m**2")
    UnitAliasManager.add_alias(volt_m.unit_dict, "V/m")