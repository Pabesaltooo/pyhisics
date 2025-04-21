from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from math import floor, log10
from typing import TYPE_CHECKING, Optional, Tuple, List
from IPython.display import display, Latex  # type: ignore

if TYPE_CHECKING:
    from .alg_types import *

# =============================================================================
# Excepciones Especializadas
# =============================================================================
class AlgebraicCompatibilityError(Exception):
    """Excepción para indicar incompatibilidades en operaciones algebraicas."""
    pass

class DimensionMatchError(Exception):
    """Excepción para indicar que las dimensiones de vectores o matrices no coinciden."""
    pass

# =============================================================================
# Utilidades para Validar Dimensiones
# =============================================================================
def validate_same_dimensions_matrix(a: List[List[float]], b: List[List[float]]) -> None:
    if len(a) != len(b) or any(len(row) != len(other_row) for row, other_row in zip(a, b)):
        raise DimensionMatchError("Las matrices deben tener las mismas dimensiones.")

def validate_same_length(a: List[float], b: List[float]) -> None:
    if len(a) != len(b):
        raise DimensionMatchError("Los vectores deben tener la misma dimensión.")




@dataclass(frozen=True)
class AlgebraicOperator:
    @classmethod
    def sum_scalar_scalar(cls, a: T_Scalar, b: T_Scalar) -> T_Scalar:
        return a + b
    @classmethod
    def sum_matrix_matrix(cls, a: T_Matrix, b: T_Matrix) -> T_Matrix:
        if len(a) != len(b) or any(len(row) != len(other_row) for row, other_row in zip(a, b)):
            raise DimensionMatchError("Las matrices deben tener las mismas dimensiones.")
        return [[a_ij + b_ij for a_ij, b_ij in zip(row, other_row)]
                for row, other_row in zip(a, b)]
    @classmethod
    def sum_vector_vector(cls, a: T_Vector, b: T_Vector) -> T_Vector:
        if len(a) != len(b):
            raise DimensionMatchError("Los vectores deben tener la misma dimensión.")
        return [a_i + b_i for a_i, b_i in zip(a, b)]
    
    @classmethod
    def mul_scalar_scalar(cls, a: T_Scalar, b: T_Scalar) -> T_Scalar:
        return a * b
    
    @classmethod
    def mul_vector_scalar(cls, a: T_Vector, b: T_Scalar) -> T_Vector:
        return [a_i * b for a_i in a]
    
    @classmethod
    def mul_vector_vector(cls, a: T_Vector, b: T_Vector, M: T_Matrix) -> T_Scalar:
        """Se usa el producto punto estandar de un espacio euclideo."""
        if len(a) != len(b):
            raise DimensionMatchError("Los vectores deben tener la misma dimensión.")
        return sum(a[i] * M[i][j] * b[j] for i in range(len(a)) for j in range(len(b)))
    
    @classmethod
    def mul_vector_matrix(cls, a: T_Vector, b: T_Matrix) -> T_Vector:
        raise DimensionMatchError("Los vectores deben multiplicarse a la derecha de las matrices: `M * v`. Si no prueba `v.T * M`")

    @classmethod
    def mul_matrix_scalar(cls, a: T_Matrix, b: T_Scalar) -> T_Matrix:
        return [[a_ij * b for a_ij in row] for row in a]
    
    @classmethod
    def mul_matrix_vector(cls, a: T_Matrix, b: T_Vector) -> Union[T_Vector, T_Scalar]:
        if len(a[0]) != len(b):
            raise DimensionMatchError(f"Dimensiones incompatibles: {len(a[0])} x {len(a)} vs. {len(b)} x 1 para multiplicación de matriz por vector.")
        rv = [sum(a_ij * b_i for a_ij, b_i in zip(row, b)) for row in a]
        return rv[0] if len(rv) == 1 else rv
        
        
    @classmethod
    def mul_matrix_matrix(cls, a: T_Matrix, b: T_Matrix) -> T_Matrix:
        if len(a[0]) != len(b):
            raise DimensionMatchError(f"Dimensiones incompatibles: {len(a)} x {len(a[0])} vs. {len(b)} x {len(b[0])} para multiplicación matrices.")
        result: T_Matrix  = []
        for i in range(len(a)):
            new_row: T_Vector = []
            for j in range(len(b[0])):
                sum_product = 0
                for k in range(len(a[0])):
                    sum_product += a[i][k] * b[k][j]
                new_row.append(sum_product)
            result.append(new_row)
        return result
    
    @classmethod
    def div_scalar(cls, a: T_Scalar, b: T_Scalar) -> T_Scalar:
        return a / b
    @classmethod
    def div_vector_scalar(cls, a: T_Vector, b: T_Scalar) -> T_Vector:
        return [a_i / b for a_i in a]
    @classmethod
    def div_matrix_scalar(cls, a: T_Matrix, b: T_Scalar) -> T_Matrix:
        return [[a_ij / b for a_ij in row] for row in a]

    @classmethod
    def div(cls, a: Multiplyable, b: Multiplyable) -> Algebraic:
        if not isinstance(b, ScalarMultiplyable):
            raise ValueError(f"No se puede dividir por un {type(b)}.")
        if isinstance(a, ScalarMultiplyable):
            from .sscalar import Scalar
            return Scalar(AlgebraicOperator.div_scalar(a.value, b.value))
        if isinstance(a, VectorialMultiplyable):
            from .vvector import Vector
            return Vector(AlgebraicOperator.div_vector_scalar(a.value, b.value))
        if isinstance(a, MatrixMultiplyable):
            from .mmatrix import Matrix
            return Matrix(AlgebraicOperator.div_matrix_scalar(a.value, b.value))
        raise TypeError(f"Operación no soportada para tipo {type(a)}.")

@dataclass(frozen=True)
class AlgebraicComparator:
    @classmethod
    def equal(cls, a: T_Algebraic, b: T_Algebraic) -> bool:
        from .alg_types import T_Scalar
        if isinstance(a, T_Scalar) and isinstance(b, T_Scalar):
            return a == b
        elif isinstance(a, list) and all(isinstance(i, T_Scalar) for i in a): 
            return a == b
        elif isinstance(a, list) and all(isinstance(i, list) and all(isinstance(j, T_Scalar) for j in i) for i in a):
            return a == b
        return False
    
    @classmethod
    def greatter_than(cls, a: T_Algebraic, b: T_Algebraic) -> bool:
        from .alg_types import T_Scalar
        if isinstance(a, T_Scalar) and isinstance(b, T_Scalar):
            return a > b
        elif isinstance(a, list) and all(isinstance(i, T_Scalar) for i in a): 
            raise NotImplemented
        elif isinstance(a, list) and all(isinstance(i, list) and all(isinstance(j, T_Scalar) for j in i) for i in a):
            raise NotImplemented
        raise NotImplemented
    
    @classmethod
    def lower_than(cls, a: T_Algebraic, b: T_Algebraic) -> bool:
        from .alg_types import T_Scalar
        if isinstance(a, T_Scalar) and isinstance(b, T_Scalar):
            return a < b
        elif isinstance(a, list) and all(isinstance(i, T_Scalar) for i in a): 
            raise NotImplemented
        elif isinstance(a, list) and all(isinstance(i, list) and all(isinstance(j, T_Scalar) for j in i) for i in a):
            raise NotImplemented
        raise NotImplemented
    
    @classmethod
    def greatter_equal(cls,  a: T_Algebraic, b: T_Algebraic) -> bool:
        return cls.equal(a,b) or cls.greatter_than(a,b)
    
    @classmethod
    def lower_equal(cls,  a: T_Algebraic, b: T_Algebraic) -> bool:
        return cls.equal(a,b) or cls.lower_than(a,b)

class Addable(ABC):
    @property
    @abstractmethod
    def value(self) -> T_Algebraic:
        pass

    @abstractmethod
    def add(self, other: Addable) -> Algebraic:
        pass

    @abstractmethod
    def neg(self) -> Algebraic:
        pass

    @abstractmethod
    def sub(self, other: Addable) -> Algebraic: ...
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return str(self)

class Multiplyable(ABC):
    @property
    @abstractmethod
    def value(self) -> T_Algebraic:
        pass

    @abstractmethod
    def mul(self, other: Multiplyable) -> Algebraic:
        pass
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return str(self)

class MulInvertible(ABC):
    @abstractmethod
    def inv(self) -> Algebraic:
        pass

class ScalarAddable(Addable):
    def __init__(self, value: T_Scalar):
        self._value = value

    @property
    def value(self) -> T_Scalar:
        return self._value

    def add(self, other: Addable) -> Scalar:
        if isinstance(other, ScalarAddable):
            from .sscalar import Scalar
            return Scalar(AlgebraicOperator.sum_scalar_scalar(self.value, other.value))
        raise TypeError(f"Operación no soportada para tipo {type(other)}.")

    def neg(self) -> Scalar:
        from .sscalar import Scalar
        return Scalar(-self.value)
    
    def sub(self, other: Addable) -> Scalar:
        return self.add(other.neg())

class ScalarMultiplyable(Multiplyable):
    def __init__(self, value: T_Scalar):
        self._value = value

    @property
    def value(self) -> T_Scalar:
        return self._value

    def mul(self, other: Multiplyable) -> Algebraic:
        if isinstance(other, ScalarMultiplyable):
            from .sscalar import Scalar
            return Scalar(
                AlgebraicOperator.mul_scalar_scalar(self.value, other.value))
        if isinstance(other, VectorialMultiplyable):
            from .vvector import Vector
            return Vector(
                AlgebraicOperator.mul_vector_scalar(other.value, self.value))
        if isinstance(other, MatrixMultiplyable):
            from .mmatrix import Matrix
            return Matrix(
                AlgebraicOperator.mul_matrix_scalar(other.value, self.value))
        raise TypeError(f"Operación no soportada para Scalar y {type(other)}.")

class VectorialAddable(Addable):
    def __init__(self, value: T_Vector):
        self._value = value

    @property
    def value(self) -> T_Vector:
        return self._value

    def add(self, other: Addable) -> Vector:
        if isinstance(other, VectorialAddable):
            from .vvector import Vector
            return Vector(AlgebraicOperator.sum_vector_vector(self.value, other.value))
        raise TypeError(f"Operación no soportada para tipo {type(other)}.")

    def neg(self) -> Vector:
        from .vvector import Vector
        return Vector([-a for a in self.value])
    
    def sub(self, other: Addable) -> Vector:
        return self.add(other.neg())

class VectorialMultiplyable(Multiplyable):
    def __init__(self, value: T_Vector):
        self._value = value

    @property
    def value(self) -> T_Vector:
        return self._value

    def mul(self, other: Multiplyable) -> Algebraic:
        if isinstance(other, ScalarMultiplyable):
            from .vvector import Vector
            return Vector(
                AlgebraicOperator.mul_vector_scalar(self.value,other.value))
        if isinstance(other, VectorialMultiplyable):
            from .sscalar import Scalar
            from .mmatrix import Matrix
            return Scalar(
                AlgebraicOperator.mul_vector_vector(self.value, other.value, Matrix.eye(len(self.value)).value))
        if isinstance(other, MatrixMultiplyable):
            from .vvector import Vector
            return Vector(
                AlgebraicOperator.mul_vector_matrix(self.value, other.value))
        raise TypeError(f"Operación no soportada para Vector y {type(other)}.")
    
class MatrixAddable(Addable):
    def __init__(self, value: T_Matrix):
        self._value = value

    @property
    def value(self) -> T_Matrix:
        return self._value

    def add(self, other: Addable) -> Matrix:
        if isinstance(other, MatrixAddable):
            from .mmatrix import Matrix
            return Matrix(AlgebraicOperator.sum_matrix_matrix(self.value, other.value))
        raise TypeError(f"Operación no soportada para tipo {type(other)}.")

    def neg(self) -> Matrix:
        result = [[-elem for elem in row] for row in self.value]
        from .mmatrix import Matrix
        return Matrix(result)
    
    def sub(self, other: Addable) -> Matrix:
        return self.add(other.neg())
    
class MatrixMultiplyable(Multiplyable):
    def __init__(self, value: T_Matrix):
        self._value = value

    @property
    def value(self) -> T_Matrix:
        return self._value

    def mul(self, other: Multiplyable) -> Algebraic:
        if isinstance(other, ScalarMultiplyable):
            from .mmatrix import Matrix
            return Matrix(
                AlgebraicOperator.mul_matrix_scalar(self.value,other.value))
        if isinstance(other, VectorialMultiplyable):
            from .vvector import Vector
            from .sscalar import Scalar
            rv = AlgebraicOperator.mul_matrix_vector(self.value, other.value)
            return Vector(rv) if isinstance(rv, List) else Scalar(rv)
        if isinstance(other, MatrixMultiplyable):
            from .mmatrix import Matrix
            return Matrix(
                AlgebraicOperator.mul_matrix_matrix(self.value, other.value))
        raise TypeError(f"Operación no soportada para Vector y {type(other)}.")
          
class BaseAlgebraicComparableClass(Multiplyable, ABC):
    def __eq__(self, other: object) -> bool:
        if isinstance(other, AlgebraicClass):
            return AlgebraicComparator.equal(self.value, other.value)
        try:
            from .alg_types import T2Algebraic
            other = T2Algebraic(other)
            return AlgebraicComparator.equal(self.value, other.value)
        except TypeError as e:
            raise e
    
    def __ne__(self, other: object) -> bool:
        return not self == other
    
    def __lt__(self, other: object) -> bool:
        if isinstance(other, AlgebraicClass):
            return AlgebraicComparator.lower_than(self.value, other.value)
        try:
            from .alg_types import T2Algebraic
            other = T2Algebraic(other)
            return AlgebraicComparator.lower_than(self.value, other.value)
        except TypeError as e:
            raise e
        
    def __le__(self, other: object) -> bool:
        if isinstance(other, AlgebraicClass):
            return AlgebraicComparator.lower_equal(self.value, other.value)
        try:
            from .alg_types import T2Algebraic
            other = T2Algebraic(other)
            return AlgebraicComparator.lower_equal(self.value, other.value)
        except TypeError as e:
            raise e
    
    def __gt__(self, other: object) -> bool:
        if isinstance(other, AlgebraicClass):
            return AlgebraicComparator.greatter_than(self.value, other.value)
        try:
            from .alg_types import T2Algebraic
            other = T2Algebraic(other)
            return AlgebraicComparator.greatter_than(self.value, other.value)
        except TypeError as e:
            raise e
    
    def __ge__(self, other: object) -> bool:    
        if isinstance(other, AlgebraicClass):
            return AlgebraicComparator.greatter_equal(self.value, other.value)
        try:
            from .alg_types import T2Algebraic
            other = T2Algebraic(other)
            return AlgebraicComparator.greatter_equal(self.value, other.value)
        except TypeError as e:
            raise e
            
class BaseAlgebraicOperableClass(Multiplyable, ABC):
    @abstractmethod
    def __add__(self, other: Addable) -> Algebraic:
        pass
    
    @abstractmethod
    def __neg__(self) -> Algebraic:
        pass
    
    @abstractmethod
    def __round__(self, n: int = 2) -> Algebraic:
        pass
    
    def __truediv__(self, other: Union[Multiplyable, T_Scalar]) -> Algebraic:
        from .alg_types import T_Scalar, Scalar
        if isinstance(other, T_Scalar):
            other = Scalar(other)
        return AlgebraicOperator.div(self, other)   
    
    @abstractmethod
    def __pow__(self, other: Union[AlgebraicClass, T_Scalar]) -> Algebraic:
        pass
        
    # Metodos implementados    
    def __mul__(self, other: Union[Multiplyable, T_Scalar]) -> Algebraic:
        from .alg_types import T_Scalar, Scalar
        if isinstance(other, T_Scalar):
            other = Scalar(other)
        return self.mul(other)    
    
    def __sub__(self, other: Addable) -> Algebraic:
        return self.__add__(other.neg())
    
    def __radd__(self, other: Addable) -> Algebraic:
        return self.__add__(other)
    
    def __rsub__(self, other: Addable) -> Algebraic:
        return self.__sub__(other).neg()
    
    def __rmul__(self, other: Union[Multiplyable, T_Scalar]) -> Algebraic:
        return self.__mul__(other)
 
class BaseAlgebraicPrintableClass(ABC):    
    @abstractmethod
    def __str__(self) -> str:
        pass
    
    @abstractmethod
    def _repr_latex_(self, name: Optional[str] = None) -> str:
        pass
    
    @classmethod
    def _normalice_value(cls, scalar: T_Scalar) -> Tuple[T_Scalar, int]:
        """Dado un valor numérico, devuelve una tupla (valor_normalizado, exponente).
        Cada subclase debe definir cómo normaliza su valor."""
        from .alg_types import T_Scalar        
        if not isinstance(scalar, T_Scalar):
            return (scalar, 1)
        if scalar == 0:
            return (0, 0)
        exponent = floor(log10(abs(scalar)))
        factor: int = 10 ** exponent
        value_norm = scalar / factor
        if isinstance(scalar, float) and value_norm.is_integer():
            value_norm = int(value_norm)
        else:
            value_norm = round(value_norm, 4)
        return (value_norm, exponent)
    
    def latex(self):
        return self._repr_latex_().replace('$', '')
    
    def __repr__(self) -> str:
        try:
            get_ipython() # type: ignore
            self.display_latex()
            return ''
        except NameError:
            return f'{self.__class__.__name__}({self.latex()})'
    
    def display_latex(self, name: Optional[str] = None) -> None:
        display(Latex(self._repr_latex_()))
    
BACC = BaseAlgebraicComparableClass
BAOC = BaseAlgebraicOperableClass
BAPC = BaseAlgebraicPrintableClass

class NotSymbolic:
    pass

class AlgebraicClass(BACC, BAOC, BAPC, Multiplyable, NotSymbolic, ABC):   
    @property
    @abstractmethod
    def is_zero(self) -> bool:
        pass
    
    @property
    @abstractmethod
    def is_identity(self) -> bool: 
        pass

    