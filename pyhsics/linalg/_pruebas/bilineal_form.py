from __future__ import annotations
from typing import List, Set, TYPE_CHECKING
from dataclasses import dataclass
from math import isclose

if TYPE_CHECKING:
    from ..sscalar import Scalar
    from ..vvector import Vector
    from ..mmatrix import Matrix

@dataclass
class BilinealForm:
    M: Matrix
    base_vecs: Set[Vector]
    
    def ortogonal_base(self) -> List[Vector]:
        n, _ = self.M.shape
        base = [Vector([self.M[i][j] for j in range(n)]) for i in range(n)]
        return self.gram_schmidt(base)
    
    def gram_schmidt(self, vectors: List[Vector]) -> List[Vector]:
        ortogonal_base: List[Vector] = []
        for v in vectors:
            for u in ortogonal_base:
                proj = self.projection(v, u)
                v = v - proj
            ortogonal_base.append(v)
        return ortogonal_base
    
    def projection(self, v: Vector, u: Vector) -> Vector:
        scalar = self.dot_product(v, u) / self.dot_product(u, u)
        return scalar * u
    
    def dot_product(self, v: Vector, w: Vector) -> Scalar:
        return Scalar(sum(v[i] * self.M[i][j] * w[j] for i in range(len(v)) for j in range(len(w))))
    
    def multiply_vector(self, u: Vector, scalar: Scalar) -> Vector:
        return Vector([(u[i] * scalar).value for i in range(len(u))])
    
    def subtract(self, v: Vector, w: Vector) -> Vector:
        return Vector([v[i] - w[i] for i in range(len(v))])
    
    def are_ortogonal(self, v: Vector, w: Vector, tol: float = 1e-10) -> bool:
        return abs(self.dot_product(v, w).value) < tol
    
    @property
    def signature(self):
        vecs = self.ortogonal_base()
        pos, neg, null = 0, 0, 0
        for v in vecs:
            result = self.dot_product(v, v).value
            if isclose(result, 0, abs_tol=1e-10):
                null += 1
            elif result > 0:
                pos += 1
            else:
                neg += 1
        return (pos, neg, null)
    
    @property
    @classmethod
    def scalar_st(cls, n: int = 3) -> Matrix:
        return Matrix.eye(n)
