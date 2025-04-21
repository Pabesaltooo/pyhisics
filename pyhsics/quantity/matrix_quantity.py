from dataclasses import dataclass
from typing import Union

from ..linalg import Matrix, T_Matrix

from ..units import Unit
from .utils_quantity import process_unit_and_value
from .quantity_quantity import Quantity
from .scalar_quantity import ScalarQuantity

@dataclass(frozen=True, slots=True)
class MatrixQuantity(Quantity):
    """
    Representa una magnitud matricial: Matrix + unidad (fundamental o compuesta).
    Todas las entradas de la matriz comparten la misma unidad.
    """
    _value: Matrix
    
    @property
    def value(self) -> Matrix:
        return self._value

    def __init__(self, value: Union[Matrix, T_Matrix], unit: Union[str, Unit] = '1') -> None:
        new_val, new_unit = process_unit_and_value(value, unit)
        if not isinstance(new_val, Matrix):
            raise TypeError("El valor debe ser de tipo Matrix o convertible a Matrix.")
        object.__setattr__(self, "_value", new_val)
        object.__setattr__(self, "_units", new_unit)

    def transpose(self) -> 'MatrixQuantity':
        """
        Retorna la transpuesta de la matriz, manteniendo la misma unidad.
        """
        return MatrixQuantity(self.value.T, self.units)

    def determinant(self) -> ScalarQuantity:
        """
        Calcula el determinante de la matriz y lo retorna como ScalarQuantity.
        La unidad del determinante se eleva a la cantidad de filas (o columnas) de la matriz.
        """
        det = self.value.det()
        # Se asume que la unidad se comporta de manera exponencial según el tamaño de la matriz.
        return ScalarQuantity(det, self.units ** self.value.shape[0])

    def __str__(self) -> str:
        return f"{self.value} ({self.units})"
        
    def __repr__(self) -> str:
        try:
            get_ipython() # type: ignore
            self.display_latex()
            return ''
        except NameError:
            return f"MatrixQuantity(matrix={self.value}, unit={self.units})"
