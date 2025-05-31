from enum import Enum
from typing import Literal

LINEAR_SYS_FORMATTING_MODES = Literal['ANSW','LES', 'MAT-SYS', 'AUG-MAT', 'PARAM']

class LinSysFormattingModes(Enum):
    answers = 'ANSW'
    linear_equation_system ='LES'
    matrix_system = 'MAT-SYS'
    augmented_matrix = 'AUG-MAT'
    parametric = 'PARAM'
    

class PrintingMode(Enum):
    MATH = 'MATH' # Si esto esta activo los vectores se muestran en columna (1,1,2), y los numeros aprox 0 -> 0
    PHYSICS = 'PHYSICS' # Si esto esta activo los vectores se muestran como 1i + 1j + 2k (Se definira al crear la clase y se podra cambiar desde un Jupyter. Por defecto `MATH`)

class BasicPrinter:
    """
    Base class for all printers.
    Provides basic functionality for printing scalars, vectors, and matrices.
    """
    printing_mode = PrintingMode.MATH  # Default printing mode

    @classmethod
    def set_printing_mode(cls, mode: PrintingMode):
        """Set the printing mode for the printer."""
        cls.printing_mode = mode