from math import floor, log10
from typing import Any, List, Optional, Tuple

from pyhsics.printing.core import BasicPrinter, PrintingMode

from ..linalg import Vector, Scalar, ScalarLike, Matrix
from ..linalg.core.algebraic_core import round_T_Scalar
from .helpers import to_superscript

def _normalize_scalar(value: ScalarLike) -> Tuple[ScalarLike, int]:
    """
    Normalize a scalar to (mantissa, exponent) such that
    value = mantissa * 10**exponent.
    """
    if not isinstance(value, ScalarLike):  # type: ignore
        return value, 0
    if value == 0:
        return 0, 0
    exp = floor(log10(abs(value)))
    factor = 10**exp
    mant = value / factor
    # Clean mantissa
    if isinstance(mant, float) and not isinstance(mant, complex) and mant.is_integer():
        mant = int(mant)
    else:
        mant = round_T_Scalar(mant, 4)
    return mant, exp



def _use_scientific(value: ScalarLike) -> bool:
    """
    Determine if scientific notation should be used based on raw value.
    Use scientific if abs(value) < 0.001 or abs(value) >= 10000.
    """
    _, exp = _normalize_scalar(value)
    if exp == 0:
        return False
    try:
        mag = abs(value)
    except Exception:
        return False
    return not (0.001 <= mag < 10000)

def _matrix_body(rows: List[List[str]], latex: bool = True) -> str:
    """
    Build string for matrix body.
    - If latex=True, returns '\\begin{pmatrix} ... \\end{pmatrix}'.
    - Else ignored (custom str used for plain text).
    """
    if latex:
        lines = [" & ".join(r) for r in rows]
        return r"\begin{pmatrix}" + " \\\\ ".join(lines) + r"\end{pmatrix}"
    return ""

class LinAlgTextFormatter(BasicPrinter):
    """
    General formatter for scalars, vectors, and matrices.
    Provides both LaTeX and plain-text (`str`) methods.
    """
       
    @classmethod
    def _format_simple(cls, x: Any) -> str:
        """
        Return integer string if whole, else rounded string.
        """
        if isinstance(x, Scalar):
            x = x.value
        if isinstance(x, int):
            return str(x)
        if isinstance(x, float) and x.is_integer():
            return str(int(x))
        if cls.printing_mode == PrintingMode.MATH:
            if abs(x) <= 1e-10:
                return "0"
        return str(round_T_Scalar(x, 4))
    @classmethod 
    def _format_scalar_latex(cls, value: ScalarLike) -> str:
        if cls.printing_mode == PrintingMode.MATH:
            if abs(value) <= 1e-10:
                return "0"
        if not _use_scientific(value):
            return cls._format_simple(value)
        else:
            mant, exp = _normalize_scalar(value)
            if mant == 1:
                return f"10^{{{exp}}}"
            else:
                return f"{cls._format_simple(mant)} \\cdot 10^{{{exp}}}"
        
    @classmethod
    def _format_scalar_str(cls, value: ScalarLike) -> str:
        if cls.printing_mode == PrintingMode.MATH:
            if abs(value) <= 1e-10:
                return "0"
        if not _use_scientific(value):
            return cls._format_simple(value)
        else:
            mant, exp = _normalize_scalar(value)
            if mant == 1:
                return f"10·{to_superscript(exp)}"
            else:
                return f"{cls._format_simple(mant)}·10{to_superscript(exp)}"
            
    @classmethod
    def scalar_latex(cls,
                     value: ScalarLike,
                     name: Optional[str] = None) -> str:
        """LaTeX representation of a scalar."""
        # If in normal range, show raw
        body = cls._format_scalar_latex(value)
        if name:
            body = f"{name} = {body}"
        return f"${body}$"

    @classmethod
    def scalar_str(cls,
                   value: ScalarLike,
                   name: Optional[str] = None) -> str:
        """Plain-text representation of a scalar, using unicode superscript."""
        body = cls._format_scalar_str(value)
        if name:
            return f"{name} = {body}"
        return body

    @classmethod
    def vector_latex(cls,
                     vec: Vector,
                     name: Optional[str] = None) -> str:
        """LaTeX representation of a column vector."""
        data = vec.value
        if len(data) == 1:
            return cls.scalar_latex(data[0], name)
        if cls.printing_mode == PrintingMode.PHYSICS:
            return cls._vector_latex_physics(data, name)        
        return cls._vector_latex_math(data, name)

    @classmethod
    def _vector_latex_math(cls, data: List[ScalarLike], name: Optional[str] = None) -> str:
        """Formato LaTeX para vectores en modo MATH."""
        # Determinar el exponente compartido si es necesario
        exps = [e for v in data if v != 0 for (_, e) in [_normalize_scalar(v)]]
        shared = exps[0] if exps and all(e == exps[0] for e in exps) else None
        
        # Si existe un exponente compartido, usar notación científica
        if shared is not None and _use_scientific(10**shared):
            divisor = 10**shared
            rows = [cls._format_simple(v/divisor) for v in data]
            body = f'\\begin{{pmatrix}} {" \\\\ ".join(r for r in rows)} \\end{{pmatrix}}'
            text = f"{body} \\cdot 10^{{{shared}}}"
        else:
            # Si no, representamos en formato columna normal
            rows = [cls._format_simple(v) for v in data]
            text = f'\\begin{{pmatrix}} {" \\\\ ".join(r for r in rows)} \\end{{pmatrix}}'

        if name:
            text = f"{name} = {text}"
        return f"${text}$"

    @classmethod
    def _vector_latex_physics(cls, data: List[ScalarLike], name: Optional[str] = None) -> str:
        """Formato LaTeX para vectores en modo PHYSICS."""
        # Si el vector tiene tres componentes, lo mostramos como i, j, k
        uv = ['i', 'j', 'k']
        if len(data) <= 3:
            components = [f"{cls._format_scalar_latex(v)} \\, \\hat{{{u}}}" if v != 0 else ''
                          for v, u in zip(data, uv)]
        else:
            # Para más de tres componentes, usamos notación general
            components = [
                f"{cls._format_scalar_latex(v)} \\, \\hat{{n_{i}}}" if v != 0 else ''
                for i, v in enumerate(data)
            ]
        
        # Reemplazar ' + -' con ' - ' para mejorar la notación
        text = " + ".join(c for c in components if c).replace('+ -', '- ')

        if name:
            text = f"{name} = {text}"
        return f"${text}$"

    @classmethod
    def vector_str(cls,
                   vec: Vector,
                   name: Optional[str] = None) -> str:
        """Plain-text representation of a column vector."""
        data = vec.value
        
        # Si el vector tiene solo un valor, utilizamos el formato escalar
        if len(data) == 1:
            return cls.scalar_str(data[0], name)

        if cls.printing_mode == PrintingMode.PHYSICS:
            # Modo PHYSICS: mostrar el vector como combinación lineal de i, j, k
            return cls._vector_str_physics(data, name)

        # Modo MATH: determinar si usar notación científica
        return cls._vector_str_math(data, name)

    @classmethod
    def _vector_str_math(cls, data: List[ScalarLike], name: Optional[str] = None) -> str:
        """Formato de texto para vectores en modo MATH."""
        exps = [e for v in data if v != 0 for (_, e) in [_normalize_scalar(v)]]
        shared = exps[0] if exps and all(e == exps[0] for e in exps) else None
        
        if shared is not None and _use_scientific(10**shared):
            divisor = 10**shared
            rows = [[cls._format_simple(v/divisor)] for v in data]
            lines = ["(" + row[0] + ")" for row in rows]
            text = "\n".join(lines) + f"·10{to_superscript(shared)}"
        else:
            entries = [cls._entry_str(v) for v in data]
            text = "(" + ", ".join(entries) + ")"

        if name:
            return f"{name} = {text}"
        return text

    @classmethod
    def _vector_str_physics(cls, data: List[ScalarLike], name: Optional[str] = None) -> str:
        """Formato de texto para vectores en modo PHYSICS."""
        components = [
             f"{cls._format_scalar_str(v)}i" if idx == 0 else
            (f"{cls._format_scalar_str(v)}j" if idx == 1 else 
             f"{cls._format_scalar_str(v)}k")
            for idx, v in enumerate(data)
        ]
        text = " + ".join(components).replace('+ -', '- ')

        if name:
            return f"{name} = {text}"
        return text

    @classmethod
    def matrix_latex(cls,
                     mat: Matrix,
                     name: Optional[str] = None) -> str:
        """LaTeX representation of a matrix."""
        if mat.shape == (1,1):
            return cls.scalar_latex(mat.value[0][0], name)
        # Determine shared exponent
        flat = [v for row in mat.value for v in row if v != 0]
        exps = [e for v in flat for (_, e) in [_normalize_scalar(v)]]
        shared = exps[0] if exps and all(e == exps[0] for e in exps) else None
        if shared is not None and _use_scientific(10**shared):
            divisor = 10**shared
            rows = [[cls._format_simple(v/divisor) for v in row] for row in mat.value]
            body = _matrix_body(rows, latex=True)
            text = f"{body} \\cdot 10^{{{shared}}}"
        else:
            rows = [[cls._entry_latex(v) for v in row] for row in mat.value]
            text = _matrix_body(rows, latex=True)
        if name:
            text = f"{name} = {text}"
        return f"${text}$"

    @classmethod
    def matrix_str(cls,
                   mat: Matrix,
                   name: Optional[str] = None) -> str:
        """Plain-text representation of a matrix with aligned columns."""
        if mat.shape == (1,1):
            return cls.scalar_str(mat.value[0][0], name)
        rows_raw = [[cls._entry_str(v) for v in row] for row in mat.value]
        col_widths = [
            max(len(rows_raw[i][j]) for i in range(len(rows_raw)))
            for j in range(len(rows_raw[0]))
        ]
        lines: List[str] = []
        for _, row in enumerate(rows_raw):
            cells = [f"{row[j]:<{col_widths[j]}}" for j in range(len(row))]
            lines.append("[" + "  ".join(cells) + "]")
        body = "\n".join(lines)
        text = body
        if name:
            return f"{name} = {text}"
        return text

    @classmethod
    def _entry_latex(cls, v: ScalarLike) -> str:
        # Inline uses same logic as scalar
        if not _use_scientific(v):
            return cls._format_simple(v)
        mant, exp = _normalize_scalar(v)
        if mant == 1:
            return f"10^{{{exp}}}"
        return f"{cls._format_simple(mant)} \\cdot 10^{{{exp}}}"

    @classmethod
    def _entry_str(cls, v: ScalarLike) -> str:
        if not _use_scientific(v):
            return cls._format_simple(v)
        mant, exp = _normalize_scalar(v)
        if mant == 1:
            return f"10·{to_superscript(exp)}"
        return f"{cls._format_simple(mant)}·10{to_superscript(exp)}"
