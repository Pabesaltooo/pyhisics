from __future__ import annotations
from typing import Iterable, List, Tuple

from .operations import *


class _BaseMatrix(MatrixAddable, MatrixMultiplyable, AlgebraicClass):
    @property
    def is_zero(self) -> bool:
        return all(a_ij == 0 for row in self.value for a_ij in row)

    @property
    def shape(self) -> Tuple[int, int]:
        """Devuelve una tupla (filas, columnas) representando la dimensión de la matriz."""
        return len(self.value), len(self.value[0])

    @property
    def is_identity(self) -> bool:
        """Indica si la matriz es la identidad (únicamente para matrices cuadradas)."""
        rows, cols = self.shape
        if rows != cols:
            return False
        return all(self.value[i][j] == (1 if i == j else 0)
                   for i in range(rows) for j in range(cols))

    def __init__(self, value: T_Matrix):
        MatrixAddable.__init__(self, value)
        MatrixMultiplyable.__init__(self, value)
        
        row_length = len(self.value[0])
        if any(len(row) != row_length for row in self.value):
            raise ValueError('Todas las filas deben tener la misma longitud.')

    def __str__(self) -> str:
        col_widths = [
            max(len(str(self.value[i][j])) 
                for i in range(len(self.value))) 
            for j in range(len(self.value[0]))
            ]        
        matrix_str = '\n'.join(
            '[' + '  '.join(f"{str(self.value[i][j]):<{col_widths[j]}}" 
                            for j in range(len(self.value[0]))) + ']'
            for i in range(len(self.value))
        )    
        return matrix_str  
    
    def __add__(self, other: Addable) -> Matrix:
        return self.add(other)
    
    def __neg__(self) -> Matrix:
        return self.neg()
    
    def __pow__(self, other: Union[AlgebraicClass, T_Scalar]) -> Algebraic:
        # Si la potencia es menor a n (habra que testear tiemmpos) entonces hace la potenciacion por mutiplicacion n veces
        # Si es mayor a n entonces diagonaliza la matriz, obtiene la matriz de cambio de base, eleva los elementos de la diagonal
        # finalmente cambia la base para obtener el resultado.
        raise NotImplementedError


    
    def __round__(self, n: int = 2) -> Matrix:
        """Redondea los elementos de la matriz a n decimales."""
        return Matrix([[round(elem, n) for elem in row] for row in self.value])
    
    def __getitem__(self, n: int) -> Vector:
        try:
            from .vvector import Vector
            return Vector(self.value[n])
        except IndexError:
            raise IndexError(f'No existe la fila mat[{n}]') from None
        
    def __len__(self) -> int:
        return len(self.value)
    
    def __iter__(self):
        return iter(self.value)
    
    def __index__(self):
        return self.value
        
    def row(self, n: int) -> Vector:
        return self[n]
    
    def col(self, n: int) -> Vector:
        from .vvector import Vector
        return Vector([row[n] for row in self.value])
    


@dataclass 
class MatrixMethods:   
    @classmethod
    def det(cls, A: Matrix) -> Scalar:
        """Calcula el determinante de la matriz (solo para matrices cuadradas)."""
        from .sscalar import Scalar
        if A.shape[0] != A.shape[1]:
            raise ValueError("El determinante solo está definido para matrices cuadradas.")
        
        M = cls.row_echelon_form(A).value
        det = 1
        for i in range(len(M)):
            det *= M[i][i]
        return Scalar(det)
    
    @classmethod      
    def transpose(cls, A: Matrix) -> Matrix:
        return Matrix([[A[j][i] for j in range(len(A))] for i in range(len(A[0]))])
    
    @classmethod
    def row_echelon_form(cls, A: Matrix) -> Matrix:
        B = [fila[:] for fila in A]
        n = len(B)
        m = len(B[0]) if n > 0 else 0

        for i in range(min(n, m)):
            if B[i][i] == 0:
                for k in range(i + 1, n):
                    if B[k][i] != 0:
                        B[i], B[k] = B[k], B[i]
                        break
            if B[i][i] == 0:
                continue
            
            pivote = B[i][i]
            for j in range(i, m):
                B[i][j] /= pivote
            
            for k in range(i + 1, n):
                factor = B[k][i]
                for j in range(i, m):
                    B[k][j] -= factor * B[i][j]
        return Matrix(B)
    
    @classmethod
    def reduced_row_echelon_form(cls, A: Matrix) -> Matrix:
        """
        Calcula la forma reducida por filas de una matriz A,
        cuyos elementos pueden ser simbólicos, usando el 
        procedimiento de Gauss-Jordan. 
        Retorna una nueva matriz (no muta A).
        """
        # 1) Copiar la matriz original para trabajar sobre la copia
        B = [fila[:] for fila in A.value]

        n = len(B)
        m = len(B[0]) if n > 0 else 0

        pivot_row = 0
        pivot_col = 0

        while pivot_row < n and pivot_col < m:
            # 2) Buscar una fila `r` >= pivot_row tal que B[r][pivot_col] no sea 0
            #    (en sentido simbólico)
            pivot_found = False
            for r in range(pivot_row, n):
                if not (B[r][pivot_col]) == 0:  # <-- aquí tu método simbólico
                    # Intercambiamos la fila r con la fila pivot_row si no son la misma
                    if r != pivot_row:
                        B[pivot_row], B[r] = B[r], B[pivot_row]
                    pivot_found = True
                    break

            # Si no hay pivote en esta columna, pasamos a la siguiente
            if not pivot_found:
                pivot_col += 1
                continue

            # 3) Hacer que el pivote sea 1.
            #    pivot := B[pivot_row][pivot_col]
            pivot = B[pivot_row][pivot_col]
            #    Dividimos toda la fila por 'pivot'
            #    (en simbólico: multiplicamos por inv(pivot))
            inv_pivot = 1/(pivot)   # inverso simbólico
            for c in range(pivot_col, m):
                B[pivot_row][c] = (B[pivot_row][c] *  inv_pivot)

            # 4) Eliminar la columna pivot_col en todas las demás filas
            for r in range(n):
                if r != pivot_row:
                    factor = B[r][pivot_col]
                    if not (factor) == 0:
                        # Queremos B[r] := B[r] - factor * B[pivot_row]
                        for c in range(pivot_col, m):
                            B[r][c] = (B[r][c] - (factor * B[pivot_row][c]))

            pivot_row += 1
            pivot_col += 1

        return Matrix(B)

    

class Matrix(_BaseMatrix):
    def _repr_latex_(self, name: Optional[str]=None) -> str:
        from .alg_printer import LatexFormatter
        return LatexFormatter.matrix(self, name)
    
    @classmethod
    def eye(cls, n: int) -> Matrix:
        return cls([[1 if i == j else 0 for j in range(n)] for i in range(n)])
    
    @property
    def T(self) -> Matrix:
        """Retorna la traspuesta de la matriz."""
        return MatrixMethods.transpose(self)
    
    @property
    def rg(self) -> int:
        """Retorna el rango de la matriz."""
        return self.rank()
    
    @property
    def is_orthogonal(self) -> bool:
        """Verifica si la matriz es ortogonal."""
        if not self.is_squared:
            return False
        # La matriz A es ortogonal si A^T * A = I (identidad)
        return self.T.mul(self).is_identity

    
    @property
    def is_symmetric(self) -> bool:
        """Verifica si la matriz es simétrica."""
        if not self.is_squared:
            return False
        return all(self.value[i][j] == self.value[j][i] for i in range(self.shape[0]) for j in range(self.shape[1]))

    @property
    def trace(self) -> Scalar:
        """Calcula la traza de la matriz."""
        if not self.is_squared:
            raise ValueError("La traza solo está definida para matrices cuadradas.")
        return Scalar(sum(self.value[i][i] for i in range(self.shape[0])))

    
    @property
    def is_squared(self) -> bool:
        n, m = self.shape
        return n == m
    
    def is_high_triang(self) -> bool:
        for i, row in enumerate(self):
            for j, e in enumerate(row):
                if j <= i and not Scalar(e).is_zero:
                    return False
        return True
    
    def det(self) -> Scalar:
        """Calcula el determinante de la matriz"""
        return MatrixMethods.det(self)

    def row_echelon_form(self,  return_base: bool = False) -> Union[Matrix, Tuple[Matrix, Matrix]]:
        """Devuelve una matriz similar con forma escalonada"""
        if return_base:
            augmented_matrix = MatrixMethods.row_echelon_form(self._augmented_matrix_I())
            return (Matrix([row[self.shape[0]:] for row in augmented_matrix]), 
                    Matrix([row[:self.shape[0]] for row in augmented_matrix]))
        return MatrixMethods.row_echelon_form(self)
    
    def reduced_row_echelon_form(self, return_base: bool = False) -> Matrix:
        """Devuelve una matriz similar con forma escalonada reducida"""
        if return_base:
            augmented_matrix = MatrixMethods.reduced_row_echelon_form(self._augmented_matrix_I())
            return Matrix([row[self.shape[0]:] for row in augmented_matrix])
        return MatrixMethods.reduced_row_echelon_form(self)

    def minor(self, i: int, j: int) -> Matrix:
        """Calcula la matriz menor eliminando la fila i y la columna j."""
        return Matrix([row[:j] + row[j+1:] for row in (self.value[:i] + self.value[i+1:])])

    def adjoint(self) -> Matrix:
        """Calcula la matriz adjunta."""
        return Matrix([[((-1) ** (i+j)) * self.minor(i, j).det().value 
            for j in range(self.shape[1])] 
            for i in range(self.shape[0])])

    def rank(self) -> int:
        """Calcula el rango de la matriz como número de filas no nulas tras triangularizar."""
        M = self.reduced_row_echelon_form(False)
        rango = 0
        for fila in M:
            if any(abs(x) > 1e-10 for x in fila):
                rango += 1
        return rango
    
    @classmethod
    def from_vecs(cls, vecs: Iterable[Vector]) -> Matrix:
        return cls([v.value for v in vecs]).T
    
    def hstack(self, other: Union[Matrix, Vector]) -> Matrix:
        """Apila horizontalmente (a la drecha) dos matrices."""
        from .vvector import Vector
        if isinstance(other, Vector):
            other = Matrix([other.value]).T
        if self.shape[0] != other.shape[0]:
            raise ValueError("Las matrices deben tener el mismo número de filas para apilarse horizontalmente.")
        return Matrix([row1 + row2 for row1, row2 in zip(self.value, other.value)])
    
    def vstack(self, other: Union[Matrix, Vector]) -> Matrix:
        """Apila verticalmente (debajo) dos matrices."""
        from .vvector import Vector
        if isinstance(other, Vector):
            other = Matrix([other.value])
        if self.shape[1] != other.shape[1]:
            raise ValueError("Las matrices deben tener el mismo número de columnas para apilarse verticalmente.")
        return Matrix(self.value + other.value)
    
    
    def _augmented_matrix_I(self) -> Matrix:
        """Devuelve la matriz aumentada [A|I]"""
        I = Matrix.eye(self.shape[0])
        return Matrix([row + I_row for row, I_row in zip(self.value, I.value)])
        
    def inv(self) -> Matrix:
        """Calcula la inversa de la matriz."""
        if self.rg != self.shape[0]:
            raise ValueError(f"La matriz no tiene inversa. El rango es {self.rg} y la forma es {self.shape[0]}")
        # Reducimos a la forma escalonada la matriz aumentada
        augmented_matrix = MatrixMethods.reduced_row_echelon_form(
            self._augmented_matrix_I()
            )
        # Extraemos la parte derecha de la matriz aumentada como la inversa
        return Matrix([row[self.shape[0]:] for row in augmented_matrix])
        
    def char_poly(self) -> Poly:
        """Devuelve el polinomio caracteristico"""
        # 1. Calculamos el determinante de (A - λI)
        # 2. Desarrollamos el determinante para obtener el polinomio característico
        # 3. Retornamos el polinomio característico
        from .symbolic_math.symbol import Symbol as Sym
        from .symbolic_math.term import Term
        from .symbolic_math.expression import Expression as Expr
        
        I = Matrix.eye(self.shape[0])
        A = Expr([Term(I, {Sym('x'):1}), Term(-self)])
        
        return Poly.from_coeffs([0])
        
        pass
    
    def eigenvalues(self) -> List[Scalar]:
        """Calcula los valores propios de la matriz."""
        raise NotImplementedError("Método no implementado.")
    
    def eigenvectors(self) -> List[Vector]:
        """Calcula los vectores propios de la matriz."""
        raise NotImplementedError("Método no implementado.")
    
    def diagonalize(self) -> Tuple[Matrix, Matrix]:
        """Diagonaliza la matriz."""
        # 1. Encontramos los valores propios
        # 2. Encontramos los vectores propios
        # 3. En el mismo orden:
        #       a) creamos una matriz diagonal de valores propios
        #       b) creamos otra matriz de cambio de base de vectores propios
        raise NotImplementedError("Método no implementado.")
    
    def append(self, other: Union[Matrix, Vector]) -> Matrix:
        """Apila verticalmente dos matrices o un Vector (columna) a la derecha"""
        if not isinstance(other, Matrix) and not isinstance(other, Vector): #type: ignore
            raise TypeError("El argumento debe ser una matriz o un vector.")
        if isinstance(other, Vector):
            other = Matrix([other.value])
        if self.shape[1] != other.shape[1]:
            raise ValueError("Las matrices deben tener el mismo número de columnas para apilarse verticalmente.")
        return Matrix(self.value + other.value)
    
    
    