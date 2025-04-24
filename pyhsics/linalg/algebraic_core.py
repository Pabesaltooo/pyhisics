# algebraic_core.py
# --------------------------------------------------------------
# Versión “clean‑typing” del núcleo algebraico
# --------------------------------------------------------------
#  • Evita isinstance(…, Union[…]) → se usan tuplas reales de tipos.
#  • Se reemplazan TypeVar bound=Union por TypeAlias y Protocols.
#  • Se eliminan dependencias cíclicas: los módulos hijo importan ESTO,
#    no al revés.  Las factorías viven en `T2Algebraic`.
# --------------------------------------------------------------

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import (
    TypeAlias, TypeVar, Generic, Any, Protocol, Union, overload, runtime_checkable, List, TYPE_CHECKING
)

from ..printing.printable import Printable

if TYPE_CHECKING:
    from .scalar  import Scalar
    from .vector  import Vector
    from .matrix  import Matrix

# ---------------------------------------------------------------------------
# 1.  Aliases de primer nivel ===============================================
# ---------------------------------------------------------------------------
ScalarLike: TypeAlias = int | float | complex
VectorLike: TypeAlias = List[ScalarLike]
MatrixLike: TypeAlias = List[VectorLike]

# Alias útiles para runtime (isinstance, etc.)
SCALAR_TYPES: tuple[type, ...] = (int, float, complex)

# ---------------------------------------------------------------------------
# 2.  TypeVars ===============================================================
# ---------------------------------------------------------------------------
T    = TypeVar("T")   # valor interno
T_co = TypeVar("T_co", covariant=True)
T_   = TypeVar("T_", covariant=True)   # valor “otro” en operaciones binarias

# ---------------------------------------------------------------------------
# 3.  Interfaces algebraicas (Protocols ‑ no ABC) ===========================
# ---------------------------------------------------------------------------
@runtime_checkable
class SupportsValue(Protocol[T_co]):
    """Cualquier objeto que exponga .value."""
    @property
    def value(self) -> T_co: ...

@runtime_checkable
class Addable(SupportsValue[T], Protocol[T]):
    def __add__(self, other: Addable[T]) -> Algebraic[T]: ...
    def __neg__(self) -> Algebraic[T]: ...
    def __sub__(self, other: Addable[T]) -> Algebraic[T]: ...


@runtime_checkable
class Multiplyable(SupportsValue[T_co], Protocol[T_co]):
    def __mul__( self, other: Union[ScalarLike, Multiplyable[Any]]) -> Algebraic[Any]: ...
    def __rmul__(self, other: ScalarLike) -> Algebraic[Any]: ...


# ---------------------------------------------------------------------------
# 4.  Clase base común: Algebraic ============================================
# ---------------------------------------------------------------------------
class Algebraic(Addable[T], Multiplyable[T], Printable, ABC, Generic[T]):
    """
    Clase raíz para Scalar, Vector, Matrix, …
    Implementa operaciones de comparación y helpers comunes.
    """
    __slots__ = ("_value",)

    # ------------- init / value --------------------------------------------
    def __init__(self, value: T) -> None:
        self._value = value

    @property
    def value(self) -> T:
        return self._value

    # ------------- “bool–comparators” --------------------------------------
    def _cmp(self, other: object, op: str) -> bool:
        if not isinstance(other, Algebraic):
            other: Algebraic[Any] = T2Algebraic(other)
        match op:
            case "==": return self.value == other.value
            case "!=": return self.value != other.value
            case "<":  return self.value <  other.value    # sólo escalares
            case ">":  return self.value >  other.value
            case "<=": return self.value <= other.value
            case ">=": return self.value >= other.value
            case _: raise NotImplementedError(op)

    def __eq__(self, other: object) -> bool: return self._cmp(other, "==")
    def __ne__(self, other: object) -> bool: return self._cmp(other, "!=")
    def __lt__(self, other: object) -> bool: return self._cmp(other, "<")
    def __le__(self, other: object) -> bool: return self._cmp(other, "<=")
    def __gt__(self, other: object) -> bool: return self._cmp(other, ">")
    def __ge__(self, other: object) -> bool: return self._cmp(other, ">=")

    def __sub__(self, other: Addable[T]) -> Algebraic[T]:
        return type(self)((self + (-other)).value)        

    # ------------- helpers abstractos --------------------------------------
    @abstractmethod
    def is_zero(self)     -> bool: ...
    @abstractmethod
    def is_identity(self) -> bool: ...
    @abstractmethod
    def __round__(self, n:int=2) -> Algebraic[T]: ...
    
    @overload
    @abstractmethod
    def __truediv__(self, other: ScalarLike) -> Algebraic[T]: ...
    @overload
    @abstractmethod
    def __truediv__(self, other: Algebraic[ScalarLike]) -> Algebraic[T]: ...

    @abstractmethod
    def __truediv__(self, other): Algebraic[T] # type: ignore[override]

# ---------------------------------------------------------------------------
# 5.  Operaciones elementales puestas en funciones ==========================
# ---------------------------------------------------------------------------
def _validate_same_len(a: VectorLike, b: VectorLike) -> None:
    if len(a) != len(b):
        raise ValueError("Dimensiones incompatibles")

def _validate_same_dim(a: MatrixLike, b: MatrixLike) -> None:
    if len(a) != len(b) and len(a[0]) != len(b[0]):
        raise ValueError("Dimensiones incompatibles")

@dataclass(frozen=True)
class AlgebraicOps:
    """Funciones puras para + * / entre tipos primitivos (Scalar/Vector/Matrix)."""

    # --- Suma ---------------------------------------------------------------
    @staticmethod
    def add_scalar(a: ScalarLike, b: ScalarLike) -> ScalarLike:
        return a + b

    @staticmethod
    def add_vector(a: VectorLike, b: VectorLike) -> VectorLike:
        _validate_same_len(a, b)
        return [x + y for x, y in zip(a, b)]

    @staticmethod
    def add_matrix(a: MatrixLike, b: MatrixLike) -> MatrixLike:
        _validate_same_dim(a, b)
        return [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]

    # --- Producto -----------------------------------------------------------
    @staticmethod
    def mul_scalar(a: ScalarLike, b: ScalarLike) -> ScalarLike:
        return a * b

    @staticmethod
    def mul_vector_scalar(v: VectorLike, k: ScalarLike) -> VectorLike:
        return [x * k for x in v]

    @staticmethod
    def mul_matrix_scalar(M: MatrixLike, k: ScalarLike) -> MatrixLike:
        return [[x * k for x in row] for row in M]

    @staticmethod
    def dot(a: VectorLike, b: VectorLike) -> ScalarLike:
        _validate_same_len(a, b)
        return sum(x * y for x, y in zip(a, b))

    @staticmethod
    def mat_vec(M: MatrixLike, v: VectorLike) -> VectorLike:
        if len(M[0]) != len(v):
            raise ValueError("Dimensiones incompatibles MxN · N")
        return [sum(x * y for x, y in zip(row, v)) for row in M]

    @staticmethod
    def mat_mat(A: MatrixLike, B: MatrixLike) -> MatrixLike:
        if len(A[0]) != len(B):
            raise ValueError("Dimensiones incompatibles")
        Bt: list[list[ScalarLike]] = [list(row) for row in zip(*B)]  # traspuesta para cache lineal
        return [[sum(x * y for x, y in zip(row, col)) for col in Bt] for row in A]

    # --- División nueva ---------------------------------------------
    @staticmethod
    def div_scalar(a: ScalarLike, b: ScalarLike) -> ScalarLike:
        return a / b

    @staticmethod
    def div_vector_scalar(v: VectorLike, k: ScalarLike) -> VectorLike:
        return [x / k for x in v]

    @staticmethod
    def div_matrix_scalar(M: MatrixLike, k: ScalarLike) -> MatrixLike:
        return [[x / k for x in row] for row in M]

# ---------------------------------------------------------------------------
# 6.  Factoría: de “valor suelto” a objeto Algebraic ========================
# ---------------------------------------------------------------------------
def _is_vector(val: object) -> bool:
    return (
        isinstance(val, Sequence)
        and not isinstance(val, (str, bytes))
        and all(isinstance(x, SCALAR_TYPES) for x in val)
    )

def _is_matrix(val: object) -> bool:
    return (
        isinstance(val, Sequence)
        and len(val) > 0
        and all(_is_vector(r) for r in val)
        and len({len(r) for r in val}) == 1  # todas las filas igual de largas
    )

@overload
def T2Algebraic(val: ScalarLike) -> Scalar: ...
@overload
def T2Algebraic(val: VectorLike) -> Vector: ...
@overload
def T2Algebraic(val: MatrixLike) -> Matrix: ...

def T2Algebraic(val: object): # type: ignore[overload]
    """
    Convierte cualquier representación literal (nativo Python) a
    Scalar | Vector | Matrix.  Evita dependencias inversas.
    """
    from .scalar  import Scalar   # import local p/ romper ciclos
    from .vector  import Vector
    from .matrix  import Matrix

    if isinstance(val, ScalarLike):
        return Scalar(val)
    if _is_vector(val):
        return Vector(list(val))                   # type: ignore 
    if _is_matrix(val):
        return Matrix([list(r) for r in val])      # type: ignore
    raise TypeError(f"Tipo no soportado: {val.__class__.__name__!s}")

def round_T_Scalar(x: ScalarLike, n: int = 2) -> ScalarLike:
    return round(x, n) if not isinstance(x, complex) else round(x.real, n) + round(x.imag, n)*1j


