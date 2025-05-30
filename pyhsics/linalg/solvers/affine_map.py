from __future__ import annotations

from pyhsics.printing.printable import Printable
from pyhsics.linalg.structures import Vector, Point, Matrix

class AffineMap(Printable):
    def __init__(self, A: Matrix, B: Point) -> None:
            self.linear_aplication = A
            self.point = B
    
    def __call__(self, X: Point) -> Point:
        return self.linear_aplication * X + self.point    
    
    def inv(self) -> AffineMap:
        A = self.linear_aplication.inv()
        return AffineMap(A, -A*self.point)
    
    def _repr_latex_(self, name: str | None = None) -> str:
         return f'${self.linear_aplication.latex()} X + {self.point.latex()}$'
     
    def __str__(self) -> str:
         return 'AX + B'
     
    def fixed_points(self):
        from .linear_system import LinearSystem
        A = self.linear_aplication
        I = Matrix.eye(3)
        B = self.point
        
        return LinearSystem(A-I, B.vector()).solve()