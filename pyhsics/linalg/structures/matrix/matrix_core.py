"""Internal helpers for the :class:`~pyhsics.linalg.structures.Matrix` class."""

from typing import Iterable, Iterator, List, Tuple

from pyhsics.linalg.core.algebraic_core import Algebraic, MatrixLike, ScalarLike
from pyhsics.linalg.structures import Vector

def _dims(mat: MatrixLike) -> Tuple[int, int]:
    """Filas, Columnas"""
    return len(mat), len(mat[0])


class MatrixCore(Algebraic[MatrixLike]):
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

    # ---------------- propiedades básicas ---------------------------------
    @property
    def shape(self) -> Tuple[int, int]:
        """-> (n,m)    Filas, Columnas"""
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
        from pyhsics.linalg.structures.vector import Vector
        return Vector(self._value[idx])

    def __len__(self) -> int:                    # filas
        return len(self._value)

    def __iter__(self) -> Iterator[List[ScalarLike]]:
        return iter(self._value)

    def __index__(self):
        return self.value
