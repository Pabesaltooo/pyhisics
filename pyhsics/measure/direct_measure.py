from typing import Optional, Union

from ..linalg import Scalar, ScalarLike

from ..quantity import ScalarQuantity
from ..units import Unit
from .base_measure import MeasureBaseClass

class DirectMeasure(MeasureBaseClass):
    """
    Medida directa que representa un valor, su incertidumbre y sus unidades.
    """
    _real_value: Scalar
    _real_error: Scalar
    
    _value: ScalarQuantity
    _error: ScalarQuantity
    _units: Unit
    
    @property
    def value(self) -> ScalarQuantity:
        return self._value
    
    @property
    def error(self) -> ScalarQuantity:
        return self._error
    
    @property
    def units(self) -> Unit: 
        return self._units

    def __init__(self, 
                 value: Union[ScalarQuantity, Scalar, ScalarLike], 
                 error: Union[ScalarQuantity, Scalar, ScalarLike], 
                 units: Union[str, Unit] = "1") -> None:
        
        from .utils_measure import round_measure, process_measure_error_unit
        if isinstance(value, complex) or isinstance(error, complex):
            raise ValueError("Complex numbers are not supported.")
        value = float(value)
        error = float(error)
        
        new_val, new_err, new_units = process_measure_error_unit(value, error, units)        
        value_rnd, error_rnd = round_measure(new_val, new_err)
        
        self._real_value = Scalar(value)
        self._real_error = Scalar(error)
        
        self._value = ScalarQuantity(value_rnd, new_units)
        self._error = ScalarQuantity(error_rnd, new_units)
        self._units = new_units
        
    def __str__(self) -> str:
        from .utils_measure import round_measure
        value_rnd, error_rnd = round_measure(self.value, self.error)
        if 0.001 < abs(value_rnd) < 10000:
            return f"({value_rnd} ± {error_rnd}) {self.units}"
        else:
            (value_norm, error_norm, exponent) = self.normalice_str()
            from ..printing.helpers import to_superscript
            exp_str = to_superscript(exponent)
            return f"({value_norm} ± {error_norm})·10{exp_str} {self.units}"

    def _repr_latex_(self, name: Optional[str] = None) -> str:
        from .utils_measure import round_measure
        value_rnd, error_rnd = round_measure(self.value, self.error)
        if 0.001 < abs(value_rnd) < 10_000:
            return f"$({value_rnd} \\pm {error_rnd})" + "\\;\\;" + self.units.latex() + "$"
        else:
            (value_norm, error_norm, exponent) = self.normalice_str()
            return f"$({value_norm} \\pm {error_norm}) \\cdot 10^" + "{" + str(exponent)+ "} \\;\\;" + self.units.latex() + "$"
        
    def __neg__(self) -> "DirectMeasure":
        return DirectMeasure(-self.value.value, self.error.value, self.units)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MeasureBaseClass):
            return False
        same_units = self.units == other.units
        value_difference = abs(self.value - other.value).value
        tolerance = (self.error + other.error).value
        return same_units and value_difference <= tolerance
        