from pyhsics.linalg.spaces.vector_space import VectorSpace
from pyhsics.linalg.structures import Point, Vector
from pyhsics.printing.printable import Printable


from typing import List, Optional, overload


class AffineSpace(Printable):
    """
    Representa un espacio afín S = p + V, donde p es un punto en ℝ^n y V un VectorSpace.
    """
    _typical_names = iter(["S", "T", "R", "Q", "P"])
    _typical_names_iter = iter(_typical_names)

    def __init__(self,
                 point: Point,
                 *directions: "Vector",
                 name: Optional[str] = None):
        if directions:
            self._vs = VectorSpace(*directions, name=(name or "\\vec{S}"))
        else:
            self._vs = VectorSpace(name=(name or "\\vec{S}"))
        self.point = point
        self.dimension = self._vs.dimension
        self.name = name or next(self._typical_names_iter)

    @classmethod
    def from_points(cls, *points: Point, name: Optional[str] = None) -> "AffineSpace":
        """
        Crea un espacio afín a partir de uno o más puntos.
        Usa el primer punto para definir el espacio afín.
        """
        vectors = [p - points[0] for p in points[1:]]
        return cls(points[0], *vectors, name=name)

    @property
    def directions(self) -> List["Vector"]:
        return self._vs.directions

    @property
    def nullspace(cls) -> "AffineSpace":
        """Espacio afín vacío (sin puntos)."""
        return AffineSpace(point=None, name="∅")

    def __contains__(self, vec: "Vector") -> bool:
        """
        Un vector está en el espacio afín si (vec - punto) está en el espacio vectorial subyacente.
        """
        if self.point is None:
            return False
        return (vec - self.point) in self._vs

    @overload
    def __add__(self, other: "Vector") -> "AffineSpace": ...
    @overload
    def __add__(self, other: "AffineSpace") -> "AffineSpace": ...
    def __add__(self, other):
        if isinstance(other, Vector):
            # Traslación del punto
            p_new = self.point + other
            return AffineSpace(p_new, *self.directions, name=f"{self.name}+p")
        elif isinstance(other, AffineSpace):
            # Suma de Minkowski de dos afines: (p1+p2) + span(dirs1 ∪ dirs2)
            p_new = self.point + other.point
            dirs = [*self.directions, *other.directions]
            return AffineSpace(p_new, *dirs, name=f"{self.name}+{other.name}")
        else:
            return NotImplemented

    @overload
    def __sub__(self, other: "Vector") -> "AffineSpace": ...
    @overload
    def __sub__(self, other: "AffineSpace") -> "VectorSpace": ...
    def __sub__(self, other):
        if isinstance(other, Vector):
            p_new = self.point - other
            return AffineSpace(p_new, *self.directions, name=f"{self.name}-p")
        elif isinstance(other, AffineSpace):
            # Diferencia de dos afines: vectorial subyacente de (S1 - S2)
            # = span(dirs1 ∪ dirs2) + (p1 - p2)
            p_diff = self.point - other.point
            dirs = [*self.directions, *other.directions]
            vs = VectorSpace(*dirs, name=f"{self.name}-{other.name}")
            return AffineSpace(p_diff, *vs.directions, name=f"{self.name}-{other.name}")
        else:
            return NotImplemented

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AffineSpace):
            return False
        # Comparar puntos y vectoriales subyacentes
        return self.point == other.point and self._vs == other._vs

    def _repr_latex_(self, name: str | None = None) -> str:
        if name is not None:
            start = f"\\mathcal{{{name or self.name}}} = "
        else:
            start = ""
        return f"{start}{self.point.latex()} + \\left \\langle {', '.join(v.latex() for v in self.directions)} \\right \\rangle"

    def __str__(self) -> str:
        return f"{self.point} + <{', '.join(str(v) for v in self.directions)}>"