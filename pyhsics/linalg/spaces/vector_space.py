from typing import Optional, List, Tuple, overload, Union
from collections import OrderedDict

from pyhsics.linalg.spaces.affine_space import AffineSpace
from pyhsics.printing.printable import Printable
from pyhsics.linalg.structures import Vector, Point

# Asumiendo que Vector y sus métodos ya están implementados:
# Vector.are_linear_dependent(vectors: List[Vector]) -> bool
# Vector supports +, -, scalar multiplication, equality, zero vector via Vector.zero(dim)
# y que Vector.__len__ retorna la dimensión.

class VectorSpace(Printable):
    """
    Representa un espacio vectorial V ⊆ ℝ^n generado por un conjunto de vectores independientes.
    """
    _typical_names = iter(["V", "W", "U", "S", "T", "R", "Q", "P"])
    _typical_names_iter = iter(_typical_names)
    def __init__(self,
                 *generators: "Vector",
                 name: Optional[str] = None):
        if not generators:
            self.directions: List["Vector"] = []
        else:
            # Filtrar un conjunto independiente y en orden
            basis: List["Vector"] = []
            for v in generators:
                if v.is_zero():
                    continue
                if set(v, *basis) == set(basis):
                    # v es combinación lineal de los generadores
                    continue
                basis.append(v)
            self.directions = basis
        self.dimension = len(self.directions)
        self.name = next(self._typical_names_iter) if name is None else name

    @property
    def nullspace(cls) -> "VectorSpace":
        """Espacio vectorial {0}."""
        return VectorSpace(Vector.zeros(1), name="∅")

    def __contains__(self, vec: "Vector") -> bool:
        """
        Un vector está en el span si al añadirlo a los generadores pasa a ser linealmente dependiente.
        """
        if vec.is_zero():
            return True
        return set(vec, *self.directions) == set(self.directions)
    
    def __len__(self) -> int:
        """
        Retorna la dimensión del espacio vectorial.
        """
        return self.dimension

    @overload
    def __add__(self, other: "Vector") -> "AffineSpace": ...
    @overload
    def __add__(self, other: "VectorSpace") -> "VectorSpace": ...
    @overload
    def __add__(self, other: Point) -> "AffineSpace": ...
    
    def __add__(self, other):
        if isinstance(other, Vector):
            # Trasladamos el espacio a un espacio afín
            from copy import deepcopy
            return AffineSpace(point=other,
                               *deepcopy(self.directions),
                               name=f"{self.name}+p")
        elif isinstance(other, VectorSpace):
            # Minkowski sum: span(dirs1 ∪ dirs2)
            return VectorSpace(*self.directions, *other.directions,
                               name=f"{self.name}+{other.name}")
        elif isinstance(other, Point):
            # Trasladamos el espacio a un espacio afín
            from copy import deepcopy
            return AffineSpace(point=other,
                               *deepcopy(self.directions),
                               name=f"{self.name}+p")
        else:
            return NotImplemented

    @overload
    def __sub__(self, other: "Vector") -> "AffineSpace": ...
    @overload
    def __sub__(self, other: "VectorSpace") -> "VectorSpace": ...
    def __sub__(self, other):
        if isinstance(other, Vector):
            # Traslación inversa
            from copy import deepcopy
            p = -other
            return AffineSpace(point=p,
                               *deepcopy(self.directions),
                               name=f"{self.name}-p")
        elif isinstance(other, VectorSpace):
            # Diferencias de espacios: span(dirs1 ∪ dirs2)
            return VectorSpace(*self.directions, *other.directions,
                               name=f"{self.name}-{other.name}")
        else:
            return NotImplemented

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VectorSpace):
            return False
        # Mismos generadores (up to span): cada uno en el otro
        return all(v in other for v in self.directions) and all(v in self for v in other.directions)

    def _repr_latex_(self, name: str | None = None) -> str:
        if name is not None:
            start = f"\\mathcal{{{name or self.name}}} = "
        else:
            start = ""
        return f"{start} \\left \\langle {', '.join(v.latex() for v in self.directions)} \\right \\rangle"

    def __str__(self) -> str:
        return f"<{', '.join(str(v) for v in self.directions)}>"


