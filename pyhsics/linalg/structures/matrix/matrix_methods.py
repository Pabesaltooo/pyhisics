"""Standalone matrix algorithms used by :class:`Matrix`."""

from pyhsics.linalg.structures import Scalar, Matrix

class MatrixMethods:
    @classmethod
    def det(cls, A: Matrix) -> Scalar:
        """Calcula el determinante de la matriz (solo para matrices cuadradas)."""
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