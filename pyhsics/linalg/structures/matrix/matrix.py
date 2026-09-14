"""Full featured dense matrix implementation."""

from __future__ import annotations
from functools import cached_property
from typing import Iterable, List, Literal, Optional, Self, SupportsIndex, Tuple, Union, overload

from pyhsics.linalg.core.algebraic_core import Addable, Algebraic, AlgebraicOps, MatrixLike, Multiplyable, round_T_Scalar, ScalarLike
from pyhsics.linalg.structures.point import Point
from pyhsics.linalg.structures.scalar import Scalar
from pyhsics.linalg.structures.vector import Vector

from pyhsics.linalg.structures.matrix.matrix_core import MatrixCore


def _same_shape(a: MatrixLike, b: MatrixLike) -> bool:
    return len(a) == len(b) and len(a[0]) == len(b[0])



class Matrix(
    MatrixCore,
    Addable[MatrixLike],
    Multiplyable[MatrixLike],
):
    """Matriz densa de dimensión arbitraria."""
    
    def __eq__(self, other: object) -> bool:
        from .matrix import Matrix
        if isinstance(other, Matrix):
            return self._rows_tuple == other._rows_tuple
        return False
    
    def __hash__(self) -> int:
        """Hash de la matriz."""
        return hash(tuple(tuple(row) for row in self._value))

    # ---------- helpers internos ------------------------------------
    @cached_property
    def _ref(self) -> "Matrix":
        """Forma escalonada (Gauss) cacheada."""
        from pyhsics.linalg.structures.matrix.matrix_methods import MatrixMethods
        return MatrixMethods.row_echelon_form(self)

    @cached_property
    def _rref(self) -> "Matrix":
        """Forma escalonada reducida (Gauss‑Jordan) cacheada."""
        from pyhsics.linalg.structures.matrix.matrix_methods import MatrixMethods
        return MatrixMethods.reduced_row_echelon_form(self)

    # ---------------- representación -------------------------------------   
    def __str__(self) -> str:
        from pyhsics.printing.printer_alg import LinAlgTextFormatter
        return LinAlgTextFormatter.matrix_str(self)

    def _repr_latex_(self, name: Optional[str] = None) -> str:
        from pyhsics.printing.printer_alg import LinAlgTextFormatter
        return LinAlgTextFormatter.matrix_latex(self, name)

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
        from ..scalar import Scalar
        from ..vector import Vector
        from ..point import Point

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
        from ..scalar import Scalar
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
    @overload
    def row_echelon_form(self, *, return_base: Literal[False] = False) -> Matrix: ...
    @overload
    def row_echelon_form(self, *, return_base: Literal[True]) -> Tuple[Matrix, Matrix]: ...

    def row_echelon_form(
        self, *, return_base: bool = False
    ) -> Union[Matrix, Tuple[Matrix, Matrix]]:
        """Devuelve la matriz reducida o una tupla (P, B) donde P^-1 B P = A"""
        from pyhsics.linalg.structures.matrix.matrix_methods import MatrixMethods
        if return_base:
            aug = MatrixMethods.row_echelon_form(self._augmented_matrix_I())
            return (
                Matrix([row[self.shape[0]:] for row in aug]),
                Matrix([row[:self.shape[0]] for row in aug]),
            )
        return self._ref

    @overload
    def reduced_row_echelon_form(self, *, return_base: Literal[False] = False) -> Matrix: ...
    @overload
    def reduced_row_echelon_form(self, *, return_base: Literal[True]) -> Tuple[Matrix, Matrix]: ...

    def reduced_row_echelon_form(
        self, *, return_base: bool = False
    ) -> Union[Matrix, Tuple[Matrix, Matrix]]:
        """Devuelve la matriz reducida o una tupla (P, B) donde P^-1 B P = A"""
        from pyhsics.linalg.structures.matrix.matrix_methods import MatrixMethods
        if return_base:
            aug = MatrixMethods.reduced_row_echelon_form(self._augmented_matrix_I())
            return (
                Matrix([row[self.shape[0]:] for row in aug]),
                Matrix([row[:self.shape[0]] for row in aug]),
            )
        return self._rref

    @property
    def T(self) -> Matrix:
        from pyhsics.linalg.structures.matrix.matrix_methods import MatrixMethods
        return MatrixMethods.transpose(self)

    @property
    def rg(self) -> int:
        """Retorna el rango de la matriz."""
        return self.rank()

    def rank(self) -> int:
        """Calcula el rango de la matriz como número de filas no nulas tras triangularizar."""
        return sum(any(abs(x) > 1e-10 for x in row) for row in self._rref)

    # TODO: Implementar esto en LinearMap
    def ker(self) -> Union[Vector, List[Vector], None]:
        from ...solvers.linear_system import LinearSystem
        from ..vector import Vector
        return LinearSystem(self, Vector.zeros(self.shape[0])).solve()

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
        from ..scalar import Scalar
        return Scalar(prod)

    @classmethod
    def eye(cls, n: int) -> Matrix:
        return cls([[1 if i == j else 0 for j in range(n)] for i in range(n)])

    def row(self, n: int) -> Vector:
        return self[n]

    def col(self, n: SupportsIndex) -> Vector:
        from ..vector import Vector
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
        from ..scalar import Scalar
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
    def from_vecs(cls, vecs: Iterable[Vector]) -> Self:
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
        from ..vector import Vector
        if isinstance(other, Vector):
            other = Matrix([other.value]).T
        if self.shape[0] != other.shape[0]:
            raise ValueError("Las matrices deben tener el mismo número de filas para apilarse horizontalmente.")
        return Matrix([row1 + row2 for row1, row2 in zip(self.value, other.value)])

    def vstack(self, other: Union[Matrix, Vector]) -> Matrix:
        """Apila verticalmente (debajo) dos matrices."""
        from ..vector import Vector
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
        from pyhsics.linalg.structures.matrix.matrix_methods import MatrixMethods
        aug = MatrixMethods.reduced_row_echelon_form(self._augmented_matrix_I())
        return Matrix([row[self.shape[0]:] for row in aug])

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

    def elemental_col_transformation(
        self,
        col1: Tuple[int, ScalarLike],
        col2: Tuple[int, ScalarLike]
    ) -> Matrix:
        """
        Perform an elementary column operation:

        new_column[col1_idx] = scale1 * old_column[col1_idx] + scale2 * old_column[col2_idx]

        Parameters
        ----------
        col1 : Tuple[int, Scalar]
            (col1_idx, scale1)
        col2 : Tuple[int, Scalar]
            (col2_idx, scale2)

        Returns
        -------
        Matrix
            A new Matrix with the updated column.

        Example
        -------
        >>> M = Matrix([[1,2,3],[4,5,6],[7,8,9]])
        >>> M2 = M.elemental_col_transformation((0, 2), (1, -1))
        # This computes: new col 0 = 2*col0 + (-1)*col1
        """
        col1_idx, scale1 = col1
        col2_idx, scale2 = col2

        # Validaciones básicas
        if not (isinstance(col1_idx, int) and isinstance(col2_idx, int)): # type: ignore
            raise TypeError("Column indices must be integers")

        # Copiamos la matriz para no mutar la original
        new_vals: list[list[ScalarLike]] = [row.copy() for row in self.value]

        # Aplicamos la operación fila por fila
        for i, row in enumerate(self.value):
            new_vals[i][col1_idx] = scale1 * row[col1_idx] + scale2 * row[col2_idx]

        return Matrix(new_vals)

    def elemental_row_transformation(
        self,
        row1: Tuple[int, ScalarLike],
        row2: Tuple[int, ScalarLike]
    ) -> Matrix:
        """
        Perform an elementary row operation:

        new_row[row1_idx] = scale1 * old_row[row1_idx] + scale2 * old_row[row2_idx]

        Parameters
        ----------
        row1 : Tuple[int, Scalar]
            (row1_idx, scale1)
        row2 : Tuple[int, Scalar]
            (row2_idx, scale2)

        Returns
        -------
        Matrix
            A new Matrix with the updated row.

        Example
        -------
        >>> M = Matrix([[1,2,3],
                        [4,5,6],
                        [7,8,9]])
        >>> M2 = M.elemental_row_transformation((0, 2), (1, -1))
        # This computes: new row 0 = 2*row0 + (-1)*row1
        """
        row1_idx, scale1 = row1
        row2_idx, scale2 = row2

        # Validaciones básicas
        if not (isinstance(row1_idx, int) and isinstance(row2_idx, int)): # type: ignore
            raise TypeError("Row indices must be integers")

        # Copiamos la matriz para no mutar la original
        new_vals: list[list[ScalarLike]] = [row.copy() for row in self.value]

        # Número de columnas para iterar
        num_cols = len(self.value[0])

        # Aplicamos la operación columna por columna sobre la fila row1_idx
        for j in range(num_cols):
            new_vals[row1_idx][j] = (
                scale1 * self.value[row1_idx][j]
                + scale2 * self.value[row2_idx][j]
            )

        return Matrix(new_vals)