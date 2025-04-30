# matrix.py  ---------------------------------------------------------------
# Implementación coherente con Scalar y Vector, basada en algebraic_core.py
# -------------------------------------------------------------------------
#  •  +  solo con otra Matrix
#  •  *  con Scalar | Matrix | Vector
#  •  /  solo con Scalar
#  •  Usa @overload para que mypy/pyright infieran el tipo resultante
#  •  Sin importaciones circulares en runtime (TYPE_CHECKING + imports
#     locales en los métodos).
# -------------------------------------------------------------------------

from __future__ import annotations

from typing import (
    Iterable, Iterator, List, Optional, Tuple, Union,
    overload, TYPE_CHECKING
)
from functools import cached_property

from .algebraic_core import (
    Algebraic, Addable, Multiplyable,
    ScalarLike, MatrixLike,
    AlgebraicOps, round_T_Scalar
)

if TYPE_CHECKING:                          # sólo para el type‑checker
    from .scalar import Scalar
    from .vector import Vector
    from .point import Point


# -------------------------------------------------------------------------
# 1  Pequeños helpers de validación ---------------------------------------
# -------------------------------------------------------------------------
def _same_shape(a: MatrixLike, b: MatrixLike) -> bool:
    return len(a) == len(b) and len(a[0]) == len(b[0])

def _dims(mat: MatrixLike) -> Tuple[int, int]:
    return len(mat), len(mat[0])

# -------------------------------------------------------------------------
# 2  Clase base utilitaria ------------------------------------------------
# -------------------------------------------------------------------------
class _MatrixCore(Algebraic[MatrixLike]):
    """Implementa utilidades y contratros básicos; no se exporta."""

    # ---------------- init y coherencia rectangular -----------------------
    def __init__(self, rows: Iterable[Iterable[ScalarLike]]) -> None:
        matrix = [list(r) for r in rows]          # deep‑copy
        if not matrix:
            raise ValueError("Una matriz no puede estar vacía.")
        row_len = len(matrix[0])
        if any(len(r) != row_len for r in matrix):
            raise ValueError("Todas las filas deben tener la misma longitud.")
        super().__init__(matrix)

        # ➊  Representación hashable para cache
        self._rows_tuple: tuple[tuple[ScalarLike, ...], ...] = tuple(
            tuple(r) for r in matrix
        )

    # Opcional, útil para dict / set
    def __hash__(self) -> int:
        return hash(self._rows_tuple)
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Matrix) and self._rows_tuple == other._rows_tuple

    # ---------------- propiedades básicas ---------------------------------
    @property
    def shape(self) -> Tuple[int, int]:
        return _dims(self._value)

    def is_zero(self) -> bool:
        return all(x == 0 for row in self._value for x in row)

    def is_identity(self) -> bool:
        n, m = self.shape
        if n != m:
            return False
        return all(
            self._value[i][j] == (1 if i == j else 0) for i in range(n) for j in range(m)
        )
        
    # ---------------- indexación / iter -----------------------------------
    def __getitem__(self, idx: int) -> Vector:
        from .vector import Vector
        return Vector(self._value[idx])

    def __len__(self) -> int:                    # filas
        return len(self._value)

    def __iter__(self) -> Iterator[List[ScalarLike]]:
        return iter(self._value)
    
    def __index__(self):
        return self.value


# -------------------------------------------------------------------------
# 3  Helppers de Operaciones Matriciales ----------------------------------
# -------------------------------------------------------------------------
class MatrixMethods:   
    @classmethod
    def det(cls, A: Matrix) -> Scalar:
        """Calcula el determinante de la matriz (solo para matrices cuadradas)."""
        from .scalar import Scalar
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


# -------------------------------------------------------------------------
# 3  Clase Matrix pública --------------------------------------------------
# -------------------------------------------------------------------------
class Matrix(
    _MatrixCore,
    Addable[MatrixLike],
    Multiplyable[MatrixLike],
):
    """Matriz densa de dimensión arbitraria."""
    
    # ---------- helpers internos ------------------------------------
    @cached_property
    def _ref(self) -> "Matrix":
        """Forma escalonada (Gauss) cacheada."""
        return MatrixMethods.row_echelon_form(self)

    @cached_property
    def _rref(self) -> "Matrix":
        """Forma escalonada reducida (Gauss‑Jordan) cacheada."""
        return MatrixMethods.reduced_row_echelon_form(self)

    # ---------------- representación -------------------------------------
    def __2str__(self) -> str:
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
    
    def __str__(self) -> str:
        from ..printing.printer_alg import LinAlgTextFormatter
        return LinAlgTextFormatter.matrix_str(self)          
    
    def _repr_latex_(self, name: Optional[str] = None) -> str:
        from ..printing.printer_alg import LinAlgTextFormatter
        return LinAlgTextFormatter.matrix_latex(self)   
    
    # ------------- suma ---------------------------------------------------
    @overload
    def __add__(self, other: Algebraic[MatrixLike]) -> Matrix: ... # type: ignore[override]

    def __add__(self, other):                          # type: ignore[override]
        if not isinstance(other, Matrix):
            raise NotImplemented
        if not _same_shape(self._value, other._value):
            raise ValueError("Las matrices deben tener la misma forma para sumarse.")
        return Matrix(AlgebraicOps.add_matrix_like(self._value, other._value))

    def __neg__(self) -> Matrix:
        return Matrix([[-x for x in row] for row in self._value])

    
# ------------- multiplicación ----------------------------------------
    @overload
    def __mul__(self, other: ScalarLike) -> Matrix: ...
    @overload
    def __mul__(self, other: Scalar)   -> Matrix: ...
    @overload
    def __mul__(self, other: Vector)   -> Vector: ...
    @overload
    def __mul__(self, other: Point)   -> Point: ...
    @overload
    def __mul__(self, other: Matrix)   -> Matrix: ...

    def __mul__(self, other):                           # type: ignore[override]
        from .scalar import Scalar
        from .vector import Vector
        from .point import Point

        # --- caso escalar literal --------------------------------------------
        if isinstance(other, ScalarLike):
            other = Scalar(other)

        # --- dispatch --------------------------------------------------------
        if isinstance(other, Scalar):
            return Matrix(AlgebraicOps.mul_matrix_scalar_like(self._value, other.value))
        if isinstance(other, Vector):
            return Vector(AlgebraicOps.mul_mat_vec_like(self._value, other.value))
        if isinstance(other, Point):
            return Point(AlgebraicOps.mul_mat_vec_like(self._value, other.value))
        if isinstance(other, Matrix):
            return Matrix(AlgebraicOps.mul_mat_mat_like(self._value, other._value))

        return NotImplemented

    def __rmul__(self, other: ScalarLike) -> Matrix:
        return self * other


    # ------------- división  (solo / escalar) ----------------------------
    @overload
    def __truediv__(self, other: ScalarLike) -> Matrix: ...
    @overload
    def __truediv__(self, other: Scalar)     -> Matrix: ...

    def __truediv__(self, other):                      # type: ignore[override]
        from .scalar import Scalar
        if isinstance(other, ScalarLike):
            other = Scalar(other)
        if not isinstance(other, Scalar):
            raise TypeError("Una matriz sólo se puede dividir por un escalar.")
        return Matrix(AlgebraicOps.div_matrix_scalar_like(self._value, other.value))

    # (no hay __rtruediv__)
    
    # ------------- potencia  (solo / escalar) ----------------------------
    @overload
    def __pow__(self, exp: ScalarLike)      -> Matrix: ...
    @overload
    def __pow__(self, exp: Scalar)          -> Matrix: ...
    
    def __pow__(self, exp)                  -> Matrix:  # type: ignore[override]
        # Si exp no es un entero menor de 10 -> diagonalizar la matriz 
        # y elevar los terminos de la diagonal. Luego volver a la base 
        # original.
        return NotImplemented
    
    # ---------------------------------------------------------------------
    # 4  Operaciones matriciales clásicas ----------------------------------
    # ---------------------------------------------------------------------
    
    # ---------- API pública reaprovecha la caché --------------------
    def row_echelon_form(
        self, *, return_base: bool = False
    ) -> Union["Matrix", Tuple["Matrix", "Matrix"]]:
        if return_base:
            aug = MatrixMethods.row_echelon_form(self._augmented_matrix_I())
            return (
                Matrix([row[self.shape[0]:] for row in aug]),
                Matrix([row[: self.shape[0]] for row in aug]),
            )
        return self._ref

    def reduced_row_echelon_form(
        self, *, return_base: bool = False
    ) -> Matrix:
        if return_base:
            return self.inv()
        return self._rref

    @property
    def T(self) -> Matrix:
        return MatrixMethods.transpose(self)

    @property
    def rg(self) -> int:
        """Retorna el rango de la matriz."""
        return self.rank()
        
    def rank(self) -> int:
        """Calcula el rango de la matriz como número de filas no nulas tras triangularizar."""
        return sum(any(abs(x) > 1e-10 for x in row) for row in self._rref)  # RREF cacheada


    def _to_upper_triangular_similarity(self) -> Tuple['Matrix','Matrix']:
        """
        Devuelve (B, P) tales que B = P^-1 * A * P,
        B triangular superior y P triangular superior unitario.
        """
        # Copiamos datos
        A = [row[:] for row in self._value]
        n, m = self.shape
        if n != m:
            raise ValueError("Sólo definido para matrices cuadradas.")
        # Inicializamos P = I_n as floats to allow arithmetic with float or complex values
        P: MatrixLike = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

        for i in range(n):
            # Si el pivote es cero, saltamos (o podrías buscar otro no nulo)
            if A[i][i] == 0:
                continue

            # Eliminamos todo debajo de la diagonal en columna i
            for j in range(i+1, n):
                if A[j][i] != 0:
                    # factor para eliminación
                    k = A[j][i] / A[i][i]
                    # 1) fila_j := fila_j - k * fila_i
                    for c in range(n):
                        A[j][c] -= k * A[i][c]
                    # 2) columna_j := columna_j + k * columna_i
                    for r in range(n):
                        A[r][j] += k * A[r][i]
                    # 3) acumulamos en P la misma operación de columnas
                    for r in range(n):
                        P[r][j] += k * P[r][i]

        return Matrix(A), Matrix(P)

    def det(self) -> Scalar:
        # Obtenemos B,P en forma triangular
        B, _ = self._to_upper_triangular_similarity()
        # El determinante de A = determinante de B (similaridad)
        # y B es triangular => prod(diagonal)
        prod = 1
        for i in range(self.shape[0]):
            prod *= B.value[i][i]
        from .scalar import Scalar
        return Scalar(prod)

    


    @classmethod
    def eye(cls, n: int) -> Matrix:
        return cls([[1 if i == j else 0 for j in range(n)] for i in range(n)])
        
    def row(self, n: int) -> Vector:
        return self[n]
    
    def col(self, n: int) -> Vector:
        from .vector import Vector
        return Vector([row[n] for row in self.value])
    
    def __round__(self, n: int = 2) -> Matrix:
        """Redondea los elementos de la matriz a n decimales."""
        return Matrix([[round_T_Scalar(elem, n) for elem in row] for row in self.value])
    
    @property
    def is_orthogonal(self) -> bool:
        """Verifica si la matriz es ortogonal."""
        if not self.is_squared:
            return False
        return (self.T * self).is_identity()

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
                if j <= i and not Scalar(e).is_zero():
                    return False
        return True
    


    def minor(self, i: int, j: int) -> Matrix:
        """Calcula la matriz menor eliminando la fila i y la columna j."""
        return Matrix([row[:j] + row[j+1:] for row in (self.value[:i] + self.value[i+1:])])

    def adjoint(self) -> Matrix:
        """Calcula la matriz adjunta."""
        return Matrix([[((-1) ** (i+j)) * self.minor(i, j).det().value 
            for j in range(self.shape[1])] 
            for i in range(self.shape[0])])

    @classmethod
    def from_vecs(cls, vecs: Iterable[Vector]) -> Matrix:
        """Sets imput vectors in the cols of the matrix"""
        vec_list = list(vecs)
        if not vec_list:
            raise ValueError("Debe proporcionar al menos un vector.")
        n = len(vec_list[0])
        if any(len(vec) != n for vec in vec_list):
            raise ValueError("Todos los vectores deben tener la misma longitud.")
        rows = [[vec[i] for vec in vec_list] for i in range(n)]
        return cls(rows)

    def hstack(self, other: Union[Matrix, Vector]) -> Matrix:
        """Apila horizontalmente (a la drecha) dos matrices."""
        from .vector import Vector
        if isinstance(other, Vector):
            other = Matrix([other.value]).T
        if self.shape[0] != other.shape[0]:
            raise ValueError("Las matrices deben tener el mismo número de filas para apilarse horizontalmente.")
        return Matrix([row1 + row2 for row1, row2 in zip(self.value, other.value)])
    
    def vstack(self, other: Union[Matrix, Vector]) -> Matrix:
        """Apila verticalmente (debajo) dos matrices."""
        from .vector import Vector
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
        if self.rank() != self.shape[0]:
            raise ValueError("La matriz no es invertible.")
        n = self.shape[0]
        aug = self._rref  # ya incluye [A | I] tratada
        return Matrix([row[n:] for row in aug])
        
    def char_poly(self):
        """Devuelve el polinomio caracteristico"""
        # 1. Calculamos el determinante de (A - λI)
        # 2. Desarrollamos el determinante para obtener el polinomio característico
        # 3. Retornamos el polinomio característico
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