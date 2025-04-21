from __future__ import annotations
from dataclasses import dataclass
from math import atan2, cos, sin, sqrt
from random import gauss, random
from typing import Dict, Optional, Tuple, Union, List, TYPE_CHECKING

from .operations import (Multiplyable, Addable, AlgebraicOperator,
    VectorialAddable, VectorialMultiplyable, AlgebraicClass)
from .sscalar import Scalar

if TYPE_CHECKING:
    from .alg_types import (T_Scalar, T_Vector, Algebraic, Matrix)


class _BaseVector(VectorialAddable, VectorialMultiplyable, AlgebraicClass):    
    
    @property
    def is_zero(self) -> bool:
        return all(v_i == 0 for v_i in self.value)
    
    @property
    def is_identity(self) -> bool:
        return all(v_i == 1 for v_i in self.value)
    
    @property
    def T(self) -> Matrix:
        """Devuelve una Matriz de `1 x n` vertical"""
        from .mmatrix import Matrix
        return Matrix([[v] for v in self]).T
    
    def __init__(self, value: T_Vector):
        """Crea un vector horizontal"""
        VectorialAddable.__init__(self, value)
        VectorialMultiplyable.__init__(self, value)
        
    def __post_init__(self):
        if len(self) == 1:
            self = Scalar(self[0])
            # Crea un Scalar(self[0]) y se lo asigna a si mismo? 

    def __add__(self, other: Addable) -> Vector:
        return self.add(other)
    
    def __neg__(self) -> Vector:
        return self.neg()
    
    def __pow__(self, other: Union[AlgebraicClass, T_Scalar]) -> Algebraic:
        raise NotImplementedError

    def __round__(self, n: int = 2) -> Vector:
        return Vector([round(v_i, n) for v_i in self.value])
    
    def __rtruediv__(self, other: Multiplyable) -> ValueError:
        raise ValueError(f"No se puede dividir un {type(other)} por un vector.")

    # Metodos especificos de los vectores:
    def __iter__(self):
        """Itera sobre los componentes del vector."""
        return iter(self._value)
    
    def __getitem__(self, n: int) -> T_Scalar:
        try:
            return self._value[n]
        except IndexError:
            raise IndexError(f'No existe el elemento vec[{n}]') from None

    def __len__(self) -> int:
        return len(self._value)

    def __index__(self):
        return self.value

class Vector(_BaseVector):  
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return False
        return not self.are_linear_indep(self, other)
    
    def __hash__(self):
        return hash(tuple(self.norm().value)) 
      
    def __str__(self) -> str:
        return '(' + ', '.join(str(elem)  for elem in self.value) + ')'

    def _repr_latex_(self,name: Optional[str]=None) -> str:
        from .alg_printer import LatexFormatter
        return LatexFormatter.vector(self)
    
    
    def dot(self, other: _BaseVector,bilineal_form: Optional[Matrix] = None) -> Scalar:
        """Calcula el producto de dos vectores usando una forma bilineal o el producto escalar estándar.
        
        Si no se proporciona una forma bilineal, se asume la matriz identidad para el producto escalar estándar.
        El producto se define como b(v, w) = v^t · M_beta · w, donde M_beta es la matriz asociada a la forma bilineal.
        
        Si no se da una forma bilineal, el producto será simplemente el producto escalar estándar de los vectores."""
        
        # Si no se proporciona una forma bilineal, usamos la matriz identidad
        if bilineal_form is None:
            bilineal_form = Matrix.eye(len(self))
        
        # Verificamos que los vectores tengan las dimensiones adecuadas con la matriz de forma bilineal
        if len(self.value) != len(other.value) or len(self.value) != bilineal_form.shape[0]:
            raise ValueError("Las dimensiones de los vectores y la matriz de forma bilineal no son compatibles.")
        
        return Scalar(AlgebraicOperator.mul_vector_vector(self.value, other.value, bilineal_form.value))
    

    @property
    def magnitude(self) -> Scalar:
        """Calcula la magnitud del vector, con la definicion."""
        from .mmatrix import Matrix
        I = Matrix.eye(len(self))
        return Scalar(sqrt(self.dot(self, I)))
    
    def norm(self) -> Vector: 
        """Hace que sea de magnitud 1."""
        mag = self.magnitude.value
        if mag == 0:
            raise ValueError("No se puede normalizar un vector nulo.")
        return Vector(AlgebraicOperator.div_vector_scalar(self.value, mag))
    
    def cross(self, other: _BaseVector) -> Vector:
        """Producto cruz entre dos vectores de R3."""
        if len(self) != 3 or len(other) != 3:
            raise ValueError("El producto cruz sólo está definido para vectores en R3.")
        return Vector([
            self[1]*other[2] - self[2]*other[1],
            self[2]*other[0] - self[0]*other[2],
            self[0]*other[1] - self[1]*other[0]
        ])
        
    @classmethod
    def zeros(cls, Rn: int = 3) -> Vector:
        """Crea un vector nulo de dimensión Rn."""
        return Vector([0 for _ in range(Rn)])
    
    @classmethod
    def ones(cls, Rn: int = 3) -> Vector:
        """Crea un vector de unos de dimensión Rn."""
        return Vector([1 for _ in range(Rn)])
    
    @classmethod
    def unit_vec(cls, Rn: int = 3) -> List[Vector]:
        return ([Vector([1 if i == j else 0 for j in range(Rn)]) for i in range(Rn)])
    
    @classmethod
    def rand(cls, Rn: int = 3) -> Vector:
        """Crea un vector aleatorio de dimensión Rn."""
        return Vector([random() for _ in range(Rn)])
    
    @classmethod
    def randn(cls, Rn: int = 3) -> Vector:
        """Crea un vector aleatorio con distribución normal de dimensión Rn."""
        return Vector([gauss(0, 1) for _ in range(Rn)])
    
    @classmethod
    def from_points(cls, p1: Vector, p2: Vector) -> Vector:
        return p2.sub(p1)
    
    @classmethod
    def from_polar(cls, r: float, theta: float) -> Vector:
        return Vector([r*cos(theta), r*sin(theta)])
    
    @property
    def x(self) -> Scalar:
        return Scalar(self[0])
    
    @property
    def y(self) -> Scalar:
        return Scalar(self[1])
    
    @property
    def z(self) -> Scalar:
        return Scalar(self[2])
    
    def to_polar(self) -> Tuple[Scalar, Scalar]:
        r = self.magnitude
        theta = atan2(self[1], self[0])
        return r, Scalar(theta)
    
    @classmethod
    def are_linear_indep(cls, v1: Vector, v2: Vector) -> bool:
        from .mmatrix import Matrix as Mat
        return Mat.from_vecs([v1, v2]).rank() == 2

@dataclass(frozen=True)
class VectorSpaceBase:
    """Clase que representa una base de vectores en un espacio o subespacio vectorial."""
    vectors: List[Vector]

    def __post_init__(self):
        if not self.is_linearly_independent():
            raise

    def __len__(self):
        return len(self.vectors)
    
    def __iter__(self):
        return iter(self.vectors)

    
    def __str__(self) -> str:
        return "Base de vectores: " + ", ".join(str(v) for v in self.vectors)
    
    def is_linearly_independent(self) -> bool:
        """Verifica si los vectores en la base son linealmente independientes."""
        from .mmatrix import Matrix
        # Para comprobar si son linealmente independientes usamos la matriz formada por estos vectores
        matrix = Matrix([v.value for v in self.vectors])  # Creamos una matriz con los vectores como filas
        return matrix.rank() == len(self.vectors)
    
    def add_vector(self, vector: Vector) -> None:
        """Añade un nuevo vector a la base y verifica si sigue siendo independiente."""
        self.vectors.append(vector)
        if not self.is_linearly_independent():
            self.vectors.remove(vector)
            raise ValueError("El vector no es linealmente independiente respecto a la base.")
    
    def remove_vector(self, vector: Vector) -> None:
        """Elimina un vector de la base."""
        if vector in self.vectors:
            self.vectors.remove(vector)
        else:
            raise ValueError("El vector no pertenece a la base.")
    
    def dimension(self) -> int:
        """Devuelve la dimensión del subespacio, que es el número de vectores linealmente independientes en la base."""
        return len(self.vectors)
    
    def span(self) -> Matrix:
        """Devuelve una matriz cuyo rango genera el subespacio de la base."""
        from .mmatrix import Matrix
        return Matrix([v.value for v in self.vectors])
    
    def is_subspace(self, candidate: VectorSpaceBase) -> bool:
        """Verifica si la base candidata está contenida en el subespacio generado por la base actual."""
        from .mmatrix import Matrix
        matrix = Matrix([v.value for v in self.vectors])
        return matrix.rank() == candidate.dimension()
    
    def orthogonal_complement(self) -> List[Vector]:
        """Devuelve una lista de vectores que forman el complemento ortogonal de la base."""
        # Esto se puede implementar usando la forma bilineal o el método de Gram-Schmidt
        pass
    
    def to_matrix(self) -> Matrix:
        """Devuelve la matriz formada por los vectores de la base."""
        from .mmatrix import Matrix
        return Matrix([v.value for v in self.vectors])

    @classmethod
    def unit_vecs(cls, Rn: int = 3) -> List[Vector]:
        return [Vector([1 if i==j else 0 for j in range(Rn)]) for i in range(Rn)]


class Poly(_BaseVector):
    """Se trataran los polinomios como vectores para poder operar"""
    
    def __init__(self, exprseion: str):
        """Crea un polinomio a partir de una str."""
        self._coeffs = list(self.parse(exprseion).values())
        _BaseVector.__init__(self, self._coeffs)
        
    def __str__(self) -> str:
        return ' + '.join(f'{c}x^{i}' for i, c in enumerate(self._coeffs) if c != 0) or '0'
    
    def _repr_latex_(self, name: str | None = None) -> str:
        from .alg_printer import LatexFormatter
        return LatexFormatter.poly(self, name)
    
    @classmethod
    def parse(cls, expression: str, pytonic: bool=True) -> Dict[int, T_Scalar]:
        """Parses a polynomial expression and returns its coefficients, exponents mus be integeers.
        Ejemplo de entrada: "3x^2 + 2x - 5", "3*x**2 + 2x - 5"
        Ejemplo de salida: {0: -5, 1: 2, 2: 3}, {0: -5, 1: 2, 2: 3}
        """
        # Implementar el método de análisis de expresiones polinómicas aquí
        # Por simplicidad, asumimos que la expresión es un polinomio en una variable x
        # y que los coeficientes son números reales.
        expression = expression.replace('**', '^') # "3*x**-2 + 2x - 5" -> "3*x^-2 + 2x - 5"
        expression = expression.replace('*', '')   # "3*x^-2  + 2x - 5" -> "3x^-2  + 2x - 5"
        
        pol: Dict[int, T_Scalar] = {}
        terms = expression.replace(' ', '').replace('-','+-').split('+')
        for term in terms:
            if 'x' in term:
                if '^' in term:
                    coeff, power = term.split('x^')
                    power = int(power)
                else:
                    coeff = term[:-1]
                    power = 1
            else:
                coeff = term
                power = 0
            
            pol[power] = float(coeff) if coeff else 1.0
        
        #Añadir terminos con coeficientes cero
        pol = {i: pol.get(i, 0) for i in range(max(pol.keys()) + 1)}
        # Ordenar los términos por el exponente
        pol = dict(sorted(pol.items()))
        return pol
    
    @classmethod
    def from_coeffs(cls, coeffs: List[T_Scalar]) -> Poly:
        """Crea un polinomio a partir de una lista de coeficientes."""
        return cls(' + '.join(f'{c}x^{i}' for i, c in enumerate(coeffs) if c != 0) or '0')
    
    def __mul__(self, other: Multiplyable | int | float) -> Poly:
        """Multiplica un polinomio por un escalar o por otro polinomio."""
        new_pol = super().__mul__(other)
        if isinstance(new_pol, _BaseVector):
            return Poly.from_coeffs(new_pol.value)
        raise ValueError('No se puede crear un polinoomio a partir de esta multiplicación')
    
    def __add__(self, other: Addable) -> Poly:
        """Suma dos polinomios."""
        new_pol = super().__add__(other)
        return Poly.from_coeffs(new_pol.value)
    
    def roots(self) -> List[Scalar]:
        """Calcula las raices del polinomio."""
        from numpy import roots
        coeffs = [c for c in self._coeffs if c != 0]
        return [Scalar(r) for r in roots(coeffs)]
    
    def derivative(self) -> Poly:
        """Calcula la derivada del polinomio."""
        coeffs = [c * i for i, c in enumerate(self._coeffs)][1:]
        return Poly.from_coeffs(coeffs)
    
    def integral(self) -> Poly:
        """Calcula la integral indefinida del polinomio."""
        coeffs = [c / (i + 1) for i, c in enumerate(self._coeffs)]
        return Poly.from_coeffs(coeffs)
    
    def evaluate(self, x: T_Scalar) -> T_Scalar:
        """Evalua el polinomio en un punto x."""
        return sum(c * (x ** i) for i, c in enumerate(self._coeffs))
    
    def __call__(self, x: T_Scalar) -> T_Scalar:
        """Evalua el polinomio en un punto x."""
        return self.evaluate(x)
    
    def __pow__(self, other: Union[AlgebraicClass, T_Scalar]) -> Poly:
        """Eleva el polinomio a la potencia `other`."""
        if isinstance(other, int):
            coeffs = [c ** other for c in self._coeffs]
            return Poly.from_coeffs(coeffs)
        else:
            raise NotImplementedError("Solo se soporta la potencia entera.")
        
    