from math import floor, log10
from typing import Dict, List, Optional, Tuple
from sympy import Symbol, sympify, Expr, diff, sqrt # type: ignore

from ..quantity import ScalarQuantity
from ..units import Unit

from .base_measure import MeasureBaseClass
from .direct_measure import DirectMeasure

class CalculatedMeasure(MeasureBaseClass):
    """
    Medida calculada a partir de una fórmula simbólica y un diccionario de DirectMeasure.
    Se encarga de evaluar numéricamente el valor, el error y las unidades.
    """
    @property
    def value(self) -> ScalarQuantity:
        return self._value
    
    @property
    def error(self) -> ScalarQuantity:
        return self._error
    
    @property
    def units(self) -> Unit: 
        return self._units


    def __init__(self, formula_str: str, measurements: Dict[str, DirectMeasure]):
        if '=' in formula_str:
            name = formula_str.split('=')[0].strip()
            formula_expr = formula_str.split('=')[1].strip()
        else:
            name = None
            formula_expr = formula_str
        
        self.name:          Optional[str]               = name
        self.formula_str:   str                         = formula_str
        self.measurements:  Dict[str, DirectMeasure]  = measurements
        self._sym_dict:     dict[str, Symbol]           = {key: Symbol(key) for key in measurements.keys()}
        self.formula:       Expr                        = sympify(formula_expr, locals=self._sym_dict).simplify() # type: ignore
        
        units = self.calc_units()
        self._value = ScalarQuantity(self.calc_numeric_value(), units)
        self._error = ScalarQuantity(self.calc_numeric_error(), units)
        self._units = units

    def error_formula(self) -> Expr:
        errors: List[Tuple[Expr, Symbol]] = []
        for var in self._sym_dict.values():
            delta_sym = Symbol(f"Δ{var}")
            dfdx = diff(self.formula, var)
            errors.append((dfdx, delta_sym))
        return sqrt(sum((d * d_sym) ** 2 for d, d_sym in errors)) # type: ignore

    def calc_numeric_error(self) -> float:
        subs = {}
        for key, dm in self.measurements.items():
            subs[self._sym_dict[key]] = dm.value.value
            subs[Symbol(f"Δ{self._sym_dict[key]}")] = dm.error.value
        return float(self.error_formula().subs(subs)) # type: ignore

    def calc_numeric_value(self) -> float:
        subs = {self._sym_dict[key]: dm.value.value for key, dm in self.measurements.items()}
        return float(self.formula.subs(subs)) # type: ignore

    def calc_units(self) -> Unit:
        from .unit_calculator import UnitCalculator
        calculator = UnitCalculator(self.formula, self.measurements)
        return Unit.from_unit_composition(calculator.compute_total_units())

    def as_direct_measure(self) -> 'DirectMeasure':
        from .direct_measure import DirectMeasure
        return DirectMeasure(self.value, 
                             self.error, 
                             self.units)

    def __str__(self) -> str:
        dm = self.as_direct_measure()
        if self.name:
            return f"{self.name} = {dm}"
        return str(dm)

    def _latex(self) -> str:
        formula_latex = self.formula._repr_latex_().replace('$', '') # type: ignore
        if self.name:
            formula_latex = self.name + '\\;=\\;' + formula_latex
        dm = self.as_direct_measure()
        
        from .utils_measure import round_measure
        value_rnd, error_rnd = round_measure(dm.value, dm.error)
        if 0.001 < abs(value_rnd) < 10_000:
            return f"${formula_latex} = ({value_rnd} \\pm {error_rnd})" + "\\;\\;" + self.units.latex() + "$"
        else:
            (value_norm, error_norm, exponent) = self.normalice_str()
            return f"${formula_latex} =  ({value_norm} \\pm {error_norm}) \\cdot 10^" + "{" + str(exponent)+ "} \\;\\;" + self.units.latex() + "$"
        
    def __repr__(self) -> str:
        try:
            get_ipython() # type: ignore
            self.display_latex()
            return ''
        except NameError:
            from .utils_measure import round_measure
            value_rnd, error_rnd = round_measure(self.value, self.error)
            return f"CalculatedMeasure({self.formula_str}, {value_rnd}, {error_rnd}, {self.units})"
        

    def __neg__(self) -> 'DirectMeasure':
        from .direct_measure import DirectMeasure
        return DirectMeasure(-self.value.value, self.error.value, self.units)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MeasureBaseClass):
            return False
        same_units = self.units == other.units
        value_difference = abs(self.value - other.value)
        tolerance = self.error + other.error
        return same_units and value_difference < tolerance
