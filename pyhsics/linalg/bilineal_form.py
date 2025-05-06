from __future__ import annotations
from typing import Iterable, List, Union
from .vector import Vector
from .matrix import Matrix
from .linear_sistem import LinearSistem

class Form(Matrix):
    def ker(self) -> Union[Vector,List[Vector], None]:
        return LinearSistem(self, Vector.zeros(len(self))).solve()
    
    def get_ortogonal_subspace(self, v: Vector) -> Union[Vector,List[Vector], None]:
        return LinearSistem([(self*v).value],[0]).solve()
    
    def find_non_isotropic_vector(self) -> Vector:
        n = len(self)
        for i in range(n):
            vec = [0] * n
            vec[i] = 1
            candidate = Vector(vec)
            if candidate.dot(candidate, form=self) != 0:
                return candidate
        raise ValueError("No non-isotropic vector found")
        
    def get_ortogonal_base(self) -> set[Vector]:
        w1 = self.find_non_isotropic_vector()
        beta = {w1}        
        w1_T = self.get_ortogonal_subspace(w1)
        
        if not w1_T:
            return beta
        
        # If w1_T is a list of vectors, check if they are mutually orthogonal.
        if isinstance(w1_T, list):
            if all(v.dot(v_, form=self) == 0 for i, v in enumerate(w1_T) for v_ in w1_T[i+1:]):
                # Union the two sets and return.
                return beta.union(w1_T)
            else:
                # Otherwise, recursively compute an orthogonal base for the subspace.
                # Here we assume that constructing a new Form with w1_T as its rows is valid.
                sub_form = Form(Matrix.from_vecs(w1_T).value)
                return beta.union(sub_form.get_ortogonal_base())
        
        # If w1_T is a single Vector, add it if it's orthogonal to w1.
        elif isinstance(w1_T, Vector):
            if w1.dot(w1_T, form=self) == 0:
                beta.add(w1_T)
            return beta
        
        return beta
    
    
    def get_ortonormal_base(self) -> set[Vector]:
        return {v.norm() for v in self.get_ortogonal_base()}
        
    def get_diagonal_matrix(self) -> Matrix:
        beta = self.get_ortonormal_base()
        return Matrix([[v.dot(w).value for w in beta] for v in beta])
        