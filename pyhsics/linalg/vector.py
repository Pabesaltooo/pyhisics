# vector.py  ---------------------------------------------------------------
# Implementación “type‑safe” de Vector alineada con la versión de Scalar.
# -------------------------------------------------------------------------
#  • Usa Alias & Protocols definidos en algebraic_core.py
#  • Mantiene los helpers clásicos (dot, norm, cross…)
#  • Sólo admite *, / con escalares.  El dot‑product se expone como método.
# -------------------------------------------------------------------------

from __future__ import annotations

from random import random, gauss
from typing import (
    Iterable, Iterator, List, Optional,
    overload, TYPE_CHECKING
)

from .algebraic_core import (
    Algebraic, Addable, Multiplyable,
    ScalarLike, VectorLike,
    AlgebraicOps, round_T_Scalar
)

if TYPE_CHECKING:                       # — tipos sólo para el checker
    from .scalar import Scalar
    from .matrix import Matrix
    from .point import Point
    
# -------------------------------------------------------------------------
# 1  Clase base sencilla (con utilidades comunes) --------------------------
# -------------------------------------------------------------------------
class VectorCore(Algebraic[VectorLike]):
    """Métodos utilitarios comunes; no exportes esta clase."""

    # ---------------- init / iterable -------------------------------------
    def __init__(self, value: Iterable[ScalarLike]) -> None:
        super().__init__(list(value))            # copia defensiva

    def __iter__(self) -> Iterator[ScalarLike]:
        return iter(self._value)

    def __getitem__(self, idx: int) -> ScalarLike:
        return self._value[idx]

    def __len__(self) -> int:
        return len(self._value)

    # ---------------- helpers Algebraic -----------------------------------
    def is_zero(self) -> bool:
        return all(x == 0 for x in self._value)

    def is_identity(self) -> bool:
        return all(x == 1 for x in self._value)
    

# -------------------------------------------------------------------------
# 2  Vector público --------------------------------------------------------
# -------------------------------------------------------------------------
class Vector(
    VectorCore,
    Addable[VectorLike],
    Multiplyable[VectorLike],
):
    """Vector fila de dimensión arbitraria."""
    @property
    def T(self):
        from .matrix import Matrix
        return Matrix([self._value])
    
    # ---------------- representación --------------------------------------
    def __str__(self) -> str:
        from ..printing.printer_alg import LinAlgTextFormatter
        return LinAlgTextFormatter.vector_str(self)
    
    def _repr_latex_(self, name: Optional[str] = None) -> str:
        from ..printing.printer_alg import LinAlgTextFormatter
        return LinAlgTextFormatter.vector_latex(self, name)
    
    # ------------- suma ---------------------------------------------------
    def __add__(self, other: Addable[VectorLike]) -> Vector:
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(AlgebraicOps.add_vector_like(self._value, other._value))
    
    def __sub__(self, other: Addable[VectorLike]) -> Vector:
        return Vector((self + (-other)).value)

    def __neg__(self) -> Vector:
        return Vector([-x for x in self._value])

    # ------------- multiplicación  ---------------------------------------
    @overload
    def __mul__(self, other: ScalarLike) -> Vector: ...
    @overload
    def __mul__(self, other: Scalar)     -> Vector: ...
    @overload
    def __mul__(self, other: Vector)     -> Scalar: ...
    
    def __mul__(self, other):                             # type: ignore[override]
        from .scalar import Scalar                        
        if isinstance(other, ScalarLike):
            other = Scalar(other)

        if isinstance(other, Scalar):
            return Vector(AlgebraicOps.mul_vector_scalar_like(self._value, other.value))

        if isinstance(other, Vector):
            return self.dot(other)
        
        return NotImplemented
    
    def __rmul__(self, other: ScalarLike) -> Vector:
        return self.__mul__(other)

    # ------------- división (vector / escalar) ----------------------------
    @overload
    def __truediv__(self, other: ScalarLike) -> Vector: ...
    @overload
    def __truediv__(self, other: Scalar)    -> Vector: ...

    def __truediv__(self, other):                           # type: ignore[override]
        from .scalar import Scalar
        if isinstance(other, ScalarLike):
            other = Scalar(other)

        if isinstance(other, Scalar):
            return Vector(AlgebraicOps.div_vector_scalar_like(self._value, other.value))

        raise TypeError("Un vector sólo se puede dividir por un escalar.")

    # (no hay __rtruediv__: escalar / vector no permitido)

    # ---------------------------------------------------------------------
    # 3  Operaciones vectoriales específicas -------------------------------
    # ---------------------------------------------------------------------
    def dot(self, other: Vector, *, form: Optional[Matrix] = None) -> Scalar:
        """Producto punto usando forma bilineal opcional (identidad por defecto)."""
        from .scalar import Scalar

        if form is None:
            return Scalar(AlgebraicOps.st_dot(self._value, other._value))
        
        if len(form.value) != len(self) or len(form.value[0]) != len(other):
            raise ValueError("Dimensiones incompatibles en producto bilineal")

        #   vᵀ · M · w  ==  (Mᵀ·v)·w
        Mv = AlgebraicOps.mul_mat_vec_like(form.value, self._value)
        return Scalar(AlgebraicOps.st_dot(Mv, other._value))

    @property
    def magnitude(self) -> Scalar:
        from .scalar import Scalar
        mag2 = AlgebraicOps.st_dot(self._value, self._value)
        return Scalar((mag2)**(1/2))

    def norm(self) -> Vector:
        mag = self.magnitude.value
        if mag == 0:
            raise ValueError("No se puede normalizar un vector nulo.")
        return Vector(AlgebraicOps.div_vector_scalar_like(self._value, mag))

    # --- cross sólo para R³ ----------------------------------------------
    def cross(self, other: Vector) -> Vector:
        if len(self) != 3 or len(other) != 3:
            raise ValueError("El producto cruz sólo está definido en R³")
        a1, a2, a3 = self._value
        b1, b2, b3 = other._value
        return Vector([a2 * b3 - a3 * b2,
                       a3 * b1 - a1 * b3,
                       a1 * b2 - a2 * b1])

    # ---------------------------------------------------------------------
    # 4  Constructores de clase utilitarios --------------------------------
    # ---------------------------------------------------------------------
    @classmethod
    def zeros(cls, n: int = 3) -> Vector:
        return cls([0] * n)

    @classmethod
    def ones(cls, n: int = 3) -> Vector:
        return cls([1] * n)

    @classmethod
    def unit_vectors(cls, n: int = 3) -> List[Vector]:
        return [cls([1 if i == j else 0 for j in range(n)]) for i in range(n)]

    @classmethod
    def rand(cls, n: int = 3) -> Vector:
        return cls(random() for _ in range(n))

    @classmethod
    def randn(cls, n: int = 3) -> Vector:
        return cls(gauss(0, 1) for _ in range(n))

    # ---------------------------------------------------------------------
    # 5  Accesos cortos x, y, z -------------------------------------------
    # ---------------------------------------------------------------------
    @property
    def x(self) -> Scalar:
        from .scalar import Scalar
        return Scalar(self[0])

    @property
    def y(self) -> Scalar:
        from .scalar import Scalar
        return Scalar(self[1])

    @property
    def z(self) -> Scalar:
        from .scalar import Scalar
        if len(self) < 3:
            raise AttributeError("Vector de dimensión < 3 no tiene 'z'")
        return Scalar(self[2])

    # ---------------------------------------------------------------------
    # 6  Igualdad con tolerancia / hash ------------------------------------
    # ---------------------------------------------------------------------
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return False
        return not self.are_linear_indep(self, other)

    def __hash__(self):
        return hash(tuple(self.norm().value))

    @classmethod
    def are_linear_indep(cls, v1: Vector, v2: Vector) -> bool:
        from .matrix import Matrix
        return Matrix.from_vecs([v1, v2]).rank() == 2
    
    def __round__(self, ndigits: int = 2) -> Vector:
        return Vector(round_T_Scalar(v, ndigits) for v in self)
    
    @classmethod
    def unit_vecs(cls, n: int = 3) -> List[Vector]:
        return [Vector(1 if i == j else 0 for i in range(n)) for j in range(n)]

    def point(self) -> Point:
        from .point import Point
        return Point(self._value)