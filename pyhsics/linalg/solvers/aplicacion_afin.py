from ...printing.printable import Printable

from ...linalg import Matrix, Point, Vector

class AplicacionAfin(Printable):
    def __init__(self, A: Matrix, B: Point) -> None:
            self.linear_aplication = A
            self.point = B
    
    def __call__(self, X: Point) -> Point:
        return self.linear_aplication * X + self.point    
    
    def inv(self) -> 'AplicacionAfin':
        A = self.linear_aplication.inv()
        return AplicacionAfin(A, -A*self.point)
    
    def _repr_latex_(self, name: str | None = None) -> str:
         return f'${self.linear_aplication} X + {self.point}$'
            