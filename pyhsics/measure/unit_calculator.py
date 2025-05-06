from __future__ import annotations
from sympy import Expr, Symbol 
from typing import Dict, TYPE_CHECKING

from ..units.unit_composition import UnitComposition

if TYPE_CHECKING:
    from .direct_measure import DirectMeasure

dimensionless = UnitComposition({})

class UnitCalculator:
    """
    Esta clase se encarga de calcular la composición de unidades a partir
    de una expresión simbólica y un diccionario de medidas.
    """

    def __init__(self, formula: Expr, measurements: Dict[str, DirectMeasure]):
        self.formula = formula
        self.measurements = measurements

    def get_unit(self, symbol: Symbol) -> UnitComposition:
        """
        Retorna la composición de unidad para un símbolo dado.
        Si el símbolo no se encuentra en measurements, se lanza un error.
        """
        sym_str = str(symbol)
        if sym_str in self.measurements:
            unit = self.measurements[sym_str].units.composition
            return unit
        else:
            raise ValueError(f"Medida para {sym_str} no encontrada en measurements.")

    def parse_expression(self, expr: Expr) -> UnitComposition:
        """
        Función recursiva que devuelve la composición de unidades correspondiente a la expresión.
        Maneja casos de suma, multiplicación y potencia.
        """
        if expr.is_Number:
            # Los números se consideran adimensionales
            return UnitComposition({})

        if expr.is_Symbol:
            return self.get_unit(expr)  # type: ignore

        if expr.is_Add:
            # En una suma, se espera que todos los términos tengan la misma unidad.
            term_units = [self.parse_expression(arg) for arg in expr.args]  # type: ignore
            base_unit = term_units[0]
            for u in term_units[1:]:
                if u != base_unit:
                    raise ValueError("Incompatibilidad de unidades en la suma.")
            return base_unit

        if expr.is_Mul:
            # Para una multiplicación, se combinan las unidades multiplicativamente.
            result = UnitComposition({})
            for factor in expr.args:
                factor_unit = self.parse_expression(factor)  # type: ignore
                result *= factor_unit
            return result

        if expr.is_Pow:
            # Para una potencia, se evalúa la base y se eleva la unidad al exponente.
            base, exponent = expr.as_base_exp()
            base_unit = self.parse_expression(base)
            if exponent.is_number:
                exp_val = float(exponent)
                return base_unit ** exp_val
            else:
                # Se permite el uso de exponentes simbólicos
                return base_unit ** exponent
        
        if expr.is_Function:
                # Identificamos la función por su nombre
                func_name = expr.func.__name__

                # Funciones matemáticas que requieren argumentos adimensionales
                # (puedes ampliar esta lista según tus necesidades)
                dimensionless_funcs = {
                    "sin", "cos", "tan", "asin", "acos", "atan",
                    "sinh", "cosh", "tanh", "asinh", "acosh", "atanh",
                    "exp", "log", "ln"
                }

                if func_name in dimensionless_funcs:
                    # Verificamos que todos los argumentos sean adimensionales
                    for arg in expr.args:
                        arg_unit = self.parse_expression(arg)
                        if arg_unit != dimensionless:
                            raise ValueError(
                                f"Los argumentos de la función '{func_name}' deben ser adimensionales. "
                                f"Se encontró {arg_unit} en su lugar."
                            )
                    # El resultado de estas funciones suele ser adimensional
                    return dimensionless

                # Si se requieren más validaciones o comportamientos diferentes,
                # se pueden agregar elif adicionales aquí.
                # Por ejemplo, si quisieras tratar específicamente el ángulo en radianes,
                # podrías manejarlo aparte.

                raise NotImplementedError(
                    f"La función '{func_name}' no está soportada para análisis de unidades."
                )

        # Si el tipo de expresión no se reconoce, se lanza un error.
        raise TypeError(f"Tipo de expresión no soportada: {expr}")

    def compute_total_units(self) -> UnitComposition:
        """
        Calcula la composición total de unidades evaluando recursivamente la expresión.
        Esto permite procesar fórmulas complejas, como (a*b + a*c)*b, y asegurar que se
        validen las unidades en cada operación.
        """
        try:
            total_units = self.parse_expression(self.formula)
            return total_units
        except Exception as e:
            raise e
