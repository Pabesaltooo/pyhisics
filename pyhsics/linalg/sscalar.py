from __future__ import annotations

from .operations import *

class _BaseScalar(ScalarAddable, ScalarMultiplyable, AlgebraicClass):
    def __init__(self, value: T_Scalar):
        ScalarAddable.__init__(self, value)
        ScalarMultiplyable.__init__(self, value)    

    def __add__(self, other: Addable) -> Scalar:
        return self.add(other)
    
    def __neg__(self) -> Scalar:
        return self.neg()
    
    def __pow__(self, other: Union[AlgebraicClass, T_Scalar]) -> Algebraic: # Esto va a haber que abstraerlo mas...
        if isinstance(other, _BaseScalar):
            return Scalar(self.value ** other.value)
        elif isinstance(other, (int, float)):  # Si el exponente es un número
            return Scalar(self.value ** other)
        else:
            raise TypeError(f"Operación de potencia no soportada para {type(other)}")

    def __str__(self) -> str:
        return str(self.value)

    
    def __float__(self) -> float:
        return float(self.value)
    
    def __round__(self, n: int = 2) -> Scalar:
        return Scalar(round(self.value, n))
    
    def __abs__(self) -> Scalar:
        return Scalar(abs(self.value))
    
# Implementaciones concretas para escalares, vectores y matrices

class Scalar(_BaseScalar, MulInvertible):
    def _repr_latex_(self,name: Optional[str]=None) -> str:
        from .alg_printer import LatexFormatter
        return LatexFormatter.scalar(self)
    
    @property
    def is_zero(self) -> bool:
        return self.value == 0
    
    @property
    def is_identity(self) -> bool:
        return self.value == 1
    
    def inv(self) -> Scalar:
        return Scalar(1 / self.value)

    


