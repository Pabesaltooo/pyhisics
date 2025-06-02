# core_quantity.py
# --------------------------------------------------------------
from __future__ import annotations

from abc import ABC
from typing import (
    Any, Generic, Optional, Protocol, TypeVar, Union, runtime_checkable,
    TYPE_CHECKING, overload, TypeAlias, Tuple, cast
)

from ..linalg.structures.matrix.matrix import Matrix

# NOTE: Estos módulos se inicializan mucho antes y no depeden de este módulo
from ..printing.printable import Printable
from ..linalg import (Scalar, Vector, ScalarLike, VectorLike, MatrixLike, AlgLike,
                      T2Algebraic)
from ..units import Unit,UnitComposition

if TYPE_CHECKING:
    from .scalar_quantity import ScalarQuantity
    from .vector_quantity import VectorQuantity
    from .matrix_quantity import MatrixQuantity

# ---------------------------------------------------------------------------
# 1. Protocols / TypeVars ####################################################
# ---------------------------------------------------------------------------

ALG_TYPES: TypeAlias = Union[Scalar, Vector, Matrix]
QOPERABLE: TypeAlias = Union[ScalarLike, Scalar, Vector, Matrix, "Quantity[T_]"]

T_co   = TypeVar("T_co",    Scalar, Vector, Matrix, covariant=True)
T      = TypeVar("T",       Scalar, Vector, Matrix)   # valor interno
T_     = TypeVar("T_",      Scalar, Vector, Matrix)   # valor “otro” en operaciones binarias

@runtime_checkable
class SupportsUnits(Protocol):
    @property
    def units(self) -> Unit: ...

@runtime_checkable
class SupportsValue(Protocol[T_co]):
    @property
    def value(self) -> T_co: ...

@runtime_checkable
class QAddable(SupportsValue[T], SupportsUnits, Protocol[T]):
    def __add__(self, other: QAddable[T]) -> Quantity[T]: ...
    def __neg__(self) -> Quantity[T]: ...
    def __sub__(self, other: QAddable[T]) -> Quantity[T]: ...

@runtime_checkable
class QMultiplyable(SupportsValue[T_co], SupportsUnits, Protocol[T_co]):
    def __mul__( self, other: Union[QOPERABLE[T_], QMultiplyable[T_]]) -> Quantity[Any]: ...
    def __rmul__(self, other: ScalarLike) -> Quantity[Any]: ...

# ---------------------------------------------------------------------------
# 1.  Aliases de primer nivel ===============================================
# ---------------------------------------------------------------------------

def get_prefix_and_composition(unit: Union[str, Unit]) -> Tuple[ScalarLike, UnitComposition]:
    """
    Devuelve el factor de prefijo (antes de convertirlo en Scalar) 
    y la composición interna de la unidad.
    """
    u = Unit(unit) if isinstance(unit, str) else unit
    # `u.prefix` suele ser un int o float, `u.composition` es un dict
    return u.prefix, u.composition


@overload
def process_unit_and_value(value: Union[Scalar, ScalarLike], unit: Union[str, Unit]) -> Tuple[Scalar, Unit]: ...
@overload
def process_unit_and_value(value: Union[Vector, VectorLike], unit: Union[str, Unit]) -> Tuple[Vector, Unit]: ...
@overload
def process_unit_and_value(value: Union[Matrix, MatrixLike], unit: Union[str, Unit]) -> Tuple[Matrix, Unit]: ...

def process_unit_and_value(value: Union[Scalar, ScalarLike, Vector, VectorLike, Matrix, MatrixLike], unit: Union[str, Unit]) -> Tuple[Union[Scalar, Vector, Matrix], Unit]:
    """
    Procesa el valor y la unidad, aplicando el factor del prefijo y creando la instancia de Unit.
    """
    raw_prefix, composition = get_prefix_and_composition(unit)
    prefix = Scalar(raw_prefix)  # Convertimos el prefijo a Scalar

    # Dependiendo del tipo de 'value', lo procesamos
    if isinstance(value, Scalar):
        new_val = prefix * value
    elif isinstance(value, Vector):
        new_val = prefix * value
    elif isinstance(value, Matrix):
        new_val = prefix * value
    else:
        new_val = prefix * T2Algebraic(value)

    new_unit = Unit.from_unit_composition(composition)
    return new_val, new_unit

# ---------------------------------------------------------------------------
# 4. Clase base común: Quantity =============================================
# ---------------------------------------------------------------------------
class Quantity(QAddable[T], QMultiplyable[T], Printable, ABC, Generic[T]):
    """Raíz para magnitudes (escalares, vectoriales, matriciales) con unidades."""

    __slots__ = ("_value", '_units',)
    
    def __init__(self, value: Union[AlgLike, ALG_TYPES], unit: Union[str, Unit] = '1') -> None:
        val, uni = process_unit_and_value(value, unit)
        self._value = cast(T, val)
        self._units = uni
        
    # ---------- propiedades -------------------------------------------------
    @property
    def value(self) -> T: # Será Scalar, Vector o Matrix
        return self._value

    @property
    def units(self) -> Unit:
        return self._units
    
    # ---------- representacion ----------------------------------------------
    def __str__(self) -> str:
        return f"{self.value} {self.units}"

    def _repr_latex_(self, name: Optional[str] = None) -> str:
        ss = '$'
        if name:
            ss += name + ' = '
        return f"{ss}{self.value.latex()}\\;{self.units.latex()}$"

    # ---------- Nueva -------------------------------------------------------
    @overload
    def __new__(cls, value: Union[ScalarLike, Scalar], unit: Union[str, Unit] = '1') -> ScalarQuantity: ...
    @overload
    def __new__(cls, value: Union[VectorLike, Vector], unit: Union[str, Unit] = '1') -> VectorQuantity: ...
    @overload
    def __new__(cls, value: Union[MatrixLike, Matrix], unit: Union[str, Unit] = '1') -> MatrixQuantity: ...
    
    def __new__(cls, value: Union[AlgLike, ALG_TYPES], unit: Union[str, Unit] = '1') -> Quantity[Any]:
        from .scalar_quantity import ScalarQuantity
        from .vector_quantity import VectorQuantity
        from .matrix_quantity import MatrixQuantity

        if cls is Quantity:
            value, unit = process_unit_and_value(value, unit)
            if isinstance(value, Matrix):
                return object.__new__(MatrixQuantity)
            elif isinstance(value, Vector):
                return object.__new__(VectorQuantity)
            elif isinstance(value, Scalar): # type: ignore
                return object.__new__(ScalarQuantity)
            else:
                raise ValueError(f'Tipo de dato no habilitado para objetos algebricos. {type(value)}')
        else:
            return super().__new__(cls)


    # ---------- helpers  ----------------------------------------------------
    def is_zero(self) -> bool:
        return self.value.is_zero()
    
    def is_identity(self) -> bool:
        return self.value.is_identity() and self.units.is_one()

    # ---------- utilidades --------------------------------------------------
    def __hash__(self) -> int:
        return hash((self.value, self.units))
    
    def __neg__(self) -> Quantity[T]:
        return type(self)(-self.value, self.units)
    
    # ---------- abstract methods ---------------------------------------------
    def __sub__(self, other: QAddable[T]) -> Quantity[T]:
        raise NotImplementedError
    
    def __mul__(self, other: Union[QOPERABLE[T_], QMultiplyable[T_]]) -> Quantity[Any]:
        raise NotImplementedError

    def __rmul__(self, other: ScalarLike) -> Quantity[Any]:
        raise NotImplementedError

    def __add__(self, other: QAddable[T]) -> Quantity[T]:
        raise NotImplementedError
