"""Type safe scalar implementation used by the linear algebra module."""

from __future__ import annotations

from math import isclose
from typing import Any, Optional, overload, TYPE_CHECKING

from ..core.algebraic_core import (
    Addable, Multiplyable,
    Algebraic, ScalarLike, VectorLike, MatrixLike,
    AlgebraicOps, round_T_Scalar, SCALAR_TYPES
)

if TYPE_CHECKING:
    from .vector import Vector
    from .matrix.matrix import Matrix

# ---------------------------------------------------------------------
# 1.  Scalar: clase concreta
# ---------------------------------------------------------------------
class Scalar(
    Algebraic[ScalarLike],
    Addable[ScalarLike],
    Multiplyable[ScalarLike],
):
    """Número escalar exacto (int, float, complex)."""

    # ------------- init ------------------------------------------------
    def __init__(self, value: ScalarLike) -> None:
        super().__init__(value)

    # ------------- representación -------------------------------------
    def __str__(self) -> str:            # str(s)
        from ...printing.printer_alg import LinAlgTextFormatter
        return LinAlgTextFormatter.scalar_str(self.value)
    
    def _repr_latex_(self, name: Optional[str] = None) -> str:  # Jupyter
        from ...printing.printer_alg import LinAlgTextFormatter
        return LinAlgTextFormatter.scalar_latex(self.value, name)

    # ------------- helpers de Algebraic -------------------------------
    def is_zero(self) -> bool:
        return isclose(abs(self._value), 0.0, abs_tol=0.0)

    def is_identity(self) -> bool:
        return self._value == 1

    # ------------- adición --------------------------------------------
    def __add__(self, other: Addable[ScalarLike])      -> Scalar:
        if not isinstance(other, Scalar):
            other = Scalar(other.value)          # cumple Protocol Addable
        return Scalar(AlgebraicOps.add_scalar_like(self._value, other._value))

    def __neg__(self) -> Scalar:
        return Scalar(-self._value)
    
    # ------------- multiplicación -------------------------------------
    @overload
    def __mul__(self, other: ScalarLike)               -> Scalar: ...
    @overload
    def __mul__(self, other: Multiplyable[ScalarLike]) -> Scalar: ...
    @overload
    def __mul__(self, other: Multiplyable[VectorLike]) -> Vector: ...
    @overload
    def __mul__(self, other: Multiplyable[MatrixLike]) -> Matrix: ...
    
    def __mul__(self, other):  # type: ignore[override]
        from .vector import Vector
        from .matrix.matrix import Matrix
        if isinstance(other, ScalarLike):
            other = Scalar(other)
        if isinstance(other, Scalar):
            return Scalar(AlgebraicOps.mul_scalar_like(self._value, other._value))
        if isinstance(other, Vector):
            return Vector(AlgebraicOps.mul_vector_scalar_like(other.value, self._value))
        if isinstance(other, Matrix):
            return Matrix(AlgebraicOps.mul_matrix_scalar_like(other.value, self._value))
        else:
            return NotImplemented

    __rmul__ = __mul__

    # ------------- división / inverso ---------------------------------
    def inv(self) -> Scalar:
        if self.is_zero():
            raise ZeroDivisionError("0 no tiene inverso multiplicativo")
        return Scalar(1 / self._value)

    @overload
    def __truediv__(self, other: ScalarLike)  -> Scalar: ...
    @overload
    def __truediv__(self, other: Scalar)      -> Scalar: ...

    def __truediv__(self, other: Any):                    # type: ignore[override]
        if isinstance(other, SCALAR_TYPES):
            other = Scalar(other)
        if not isinstance(other, Scalar):
            raise TypeError("Sólo se permite dividir entre escalares.")
        return Scalar(AlgebraicOps.div_scalar_like(self._value, other._value))
    
    def __rtruediv__(self, other: ScalarLike) -> Scalar:
        return Scalar(other / self._value)
    
    # ------------- potencia -------------------------------------------
    @overload
    def __pow__(self, exp: ScalarLike)        -> Scalar: ...
    @overload
    def __pow__(self, exp: Scalar)            -> Scalar: ...

    def __pow__(self, exp):  # type: ignore[override]
        if isinstance(exp, Scalar):
            exp_val = exp._value
        elif isinstance(exp, ScalarLike):
            exp_val = exp
        else:
            raise TypeError(f'El exponente debe ser un escalar.')
        return Scalar(self._value ** exp_val)

    # ------------- coerciones Python ----------------------------------
    def __float__(self) -> float:
        return float(self._value.real if isinstance(self.value, complex) else self.value)

    def __int__(self) -> int:
        return int(self._value.real if isinstance(self.value, complex) else self.value)

    def __round__(self, ndigits: int = 2) -> Scalar:
        return Scalar(round_T_Scalar(self._value, ndigits))

    def __abs__(self) -> Scalar: 
        return Scalar(abs(self._value))
    # ------------- igualdad / orden ya los aporta Algebraic -----------
