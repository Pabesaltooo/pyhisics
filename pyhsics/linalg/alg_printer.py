from dataclasses import dataclass
from typing import Optional, Tuple
from math import floor, log10

from .alg_types import Vector, Scalar, Matrix, Poly, T_Scalar

from .symbolic_math.symbolic_operator import SymPrintable


def _normalice_scalar(scalar: T_Scalar) -> Tuple[T_Scalar, int]:
    """Dado un valor numérico, devuelve una tupla (valor_normalizado, exponente).
    Cada subclase debe definir cómo normaliza su valor."""
    from .alg_types import T_Scalar        
    if not isinstance(scalar, T_Scalar): # type: ignore
        return (scalar, 1)
    if scalar == 0:
        return (0, 0)
    exponent = floor(log10(abs(scalar)))
    factor: int = 10 ** exponent
    value_norm = scalar / factor
    if isinstance(scalar, float) and value_norm.is_integer():
        value_norm = int(value_norm)
    else:
        value_norm = round(value_norm, 4)
    return (value_norm, exponent)

@dataclass
class LatexFormatter:
    """
    Dataclass que encapsula la lógica para generar representaciones en LaTeX
    de una lista de valores (por ejemplo, los componentes de un vector).
    """
    @classmethod
    def sym(cls, sym: SymPrintable):
        return sym.latex()
    
    @classmethod
    def format_individual(cls, vec: Vector, v: float) -> str:
        if isinstance(v, SymPrintable):
            return cls.sym(v)
        if v == 0:
            return '0'
        elif 0.001 <= abs(v) < 10000:
            r_v = round(v, 4)
            return str(int(r_v)) if float(r_v).is_integer() else str(r_v)
        else:
            norm, exp = _normalice_scalar(v)
            if exp == 0:
                return str(norm)
            elif norm == 1:
                return f"10^{{{exp}}}"
            else:
                return f"{norm} \\cdot 10^{{{exp}}}"
    
    @classmethod
    def scalar(cls, self: Scalar, name: Optional[str]=None) -> str:
        return f'${cls.format_individual(Vector([self.value]), self.value)}$'
    
    @classmethod
    def vector(cls, vec: Vector, name: Optional[str]=None) -> str:
        if len(vec) == 1:
            if isinstance(vec.value[0], SymPrintable):
                return f"${vec.value[0].latex()}$"
            else:
                return f"${Scalar(vec.value[0]).latex()}$"
        
        # Función para generar la cadena LaTeX de la matriz
        def make_matrix(components: list[str]) -> str:
            return r"\begin{pmatrix} " + r" \\ ".join(components) + r" \end{pmatrix}"

        # Formatea un valor usando un divisor (por defecto 1)
        def format_value(v: float, divisor: float = 1) -> str:
            if v == 0:
                return '0'
            adjusted = round(v / divisor, 4)
            return str(int(adjusted)) if float(adjusted).is_integer() else str(adjusted)


                    
        # Vamos a comprobar que no haya objetos SymPrintable en los elementos  del vector, si hay algun elemento ese lo tratamos distinto y solo llamamos a obj.latex()...
        # En realidad un vetor no deberia tener ningun obejto que no fuera escalar dentro de si, pero a veces si que meto symbols o expresiones dentro...
        # Caso: todos los no nulos comparten exponente
        if not any(isinstance(v, SymPrintable) for v in vec):
            exponents = [_normalice_scalar(v)[1] for v in vec.value if v != 0]
        else:
            exponents = []
            
        if exponents and len(set(exponents)) == 1:
            common_exponent = exponents[0]
            # Si el exponente está en rango, no se ajusta; de lo contrario se usa el divisor
            divisor = 1 if (common_exponent >= -3 and common_exponent <= 3) else 10 ** common_exponent
            components = [format_value(v, divisor) for v in vec]
            matrix = make_matrix(components)
            if divisor == 1 or common_exponent == 0:
                return f'${matrix}$'
            else:
                return f'${matrix} \\, \\cdot 10^{{{common_exponent}}}$'
        else:
            # Caso: cada componente se formatea de forma individual
            components = [cls.format_individual(vec, v) for v in vec.value]
            matrix = make_matrix(components)
            return f'${matrix}$'

    @classmethod
    def matrix(cls, mat: Matrix, name: Optional[str]=None) -> str:
        # Caso especial: si es una matriz 1x1, se muestra como escalar.
        if mat.shape == (1,1):
            if not any(isinstance(v, SymPrintable) for row in mat for v in row):
                return f"${Scalar(mat.value[0][0]).latex()}$"
            elif isinstance(mat.value[0][0], SymPrintable):
                return f"${mat.value[0][0].latex()}$"

        # Función para construir la cadena LaTeX de la matriz.
        def make_matrix(rows: list[list[str]]) -> str:
            # Se unen los elementos de cada fila con " & " y se separan filas con " \\ "
            return r"\begin{pmatrix} " + r" \\ ".join([" & ".join(row) for row in rows]) + r" \end{pmatrix}"

        # Función para formatear un valor con un divisor opcional (por defecto 1)
        def format_value(v: float, divisor: float = 1) -> str:
            if v == 0:
                return '0'
            adjusted = round(v / divisor, 4)
            if isinstance(adjusted, Scalar):
                adjusted = adjusted.value
            return str(int(adjusted)) if float(adjusted).is_integer() else str(adjusted)

        if not any(isinstance(v, SymPrintable) for row in mat for v in row):
            exponents = [_normalice_scalar(v)[1] for row in mat.value for v in row if v != 0]
        else:
            exponents = []
            
        if exponents and len(set(exponents)) == 1:
            common_exponent = exponents[0]
            # Si el exponente está en un rango "normal", no se ajusta; de lo contrario se usa un divisor
            divisor = 1 if (common_exponent > -3 and common_exponent <= 3) else 10 ** common_exponent
            rows_components = [[format_value(v, divisor) for v in row] for row in mat.value]
            matrix_latex = make_matrix(rows_components)
            if divisor == 1 or common_exponent == 0:
                return f'${matrix_latex}$'
            else:
                return f'${matrix_latex} \\, \\cdot 10^{{{common_exponent}}}$'
        else:
            # Si no se puede unificar el exponente, se formatea cada elemento individualmente
            rows_components = [[cls.format_individual(Vector(row), v) for v in row] for row in mat.value]
            matrix_latex = make_matrix(rows_components)
            return f'${matrix_latex}$'

    @classmethod
    def poly(cls, poly: Poly, name: Optional[str]=None) -> str:
        # Caso especial: si es un polinomio de grado 0, se muestra como escalar.
        if len(poly.value) == 1:
            return f"${Scalar(poly.value[0]).latex()}$"

        poly_latex = '' if name is None else f"${name}\\;=\\;"
        for i, v in enumerate(poly.value):
            if v == 0.0:
                continue
            if v < 0:
                poly_latex += '-' if poly_latex == '' else ' - '
                v = abs(v)
            else:
                poly_latex += '+' if poly_latex != '' else ''
            if i == 0:
                poly_latex += f"{Scalar(v).latex()}"
            elif i == 1:
                poly_latex += f"{Scalar(v).latex()}x"
            else:
                poly_latex += f"{Scalar(v).latex()}x^{{{i}}}"

        return f'${poly_latex}$'