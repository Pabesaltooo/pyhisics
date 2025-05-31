import sys
from typing import List, Optional, Set, Union, Dict, Tuple
import re
from math import lcm
from functools  import reduce

from pyhsics.printing.printable import Printable
from pyhsics.linalg.core.complex_fraction import ComplexFraction
from pyhsics.linalg.core.algebraic_core import VectorLike, MatrixLike
from pyhsics.linalg.structures import Vector, Matrix

from pyhsics.printing.core import LINEAR_SYS_FORMATTING_MODES as MODES


def vector_to_integer_coords(vec_float: Union[Vector,VectorLike]):
    """
    Devuelve una lista de enteros que representan el vector original
    una vez escalado por el MCM global.

    • Si un elemento era real → se añade UN entero
    • Si era complejo        → se añaden DOS: (Re, Im)
    """
    # 1) Fracciones exactas
    fracs = [ComplexFraction(v).limit_denominator(100_000) for v in vec_float]

    # 2) MCM de todos los denominadores
    global_M = reduce(lcm, (f.denominator for f in fracs), 1)

    # 3) Escalar y extraer enteros
    int_coords: List[int] = []
    for f in fracs:
        scale = global_M // f.denominator      # entero exacto
        num   = f.numerator * scale            # sigue siendo complejo ℤ+ℤ·j
        if num.imag:                           # coordenada compleja
            int_coords.extend([int(num.real), int(num.imag)])
        else:                                  # coordenada real
            int_coords.append(int(num.real))

    return int_coords

class LinearSystem(Printable):
    """
    Representa un sistema de ecuaciones lineales de la forma A·X = B.
    Incluye detección de sistemas con solución única, infinitas soluciones
    o sin solución (incompatibles), y soporta el parseo de ecuaciones
    desde strings.
    """
    
    from ...printing.printer_lin_sys import LinSysFormatter
    latex_formatter = LinSysFormatter()

    def __init__(
        self, 
        value: Union[Matrix, MatrixLike],     # Matriz de coeficientes A
        B: Union[Vector, VectorLike], *,        # Vector de términos independientes B
        repr_mode: MODES = "ANSW"
    ):
        """
        Parámetros:
        -----------
        value: Matrix
            Matriz de coeficientes (A).
        B: Vector
            Vector de términos independientes (B).
        repr_mode: Literal['Answers','LES', 'MS', 'AM']
            - "Answers": Representación estándar (posibles soluciones).
            - "Linear-Equation-Sistem" o "LES": Muestra cada ecuación.
            - "Matrix-Sistem" o "MS": Visualiza como un sistema matricial.
            - "Augmented_Matrix" o "AM": Matriz aumentada.
        """
        self._value = value if isinstance(value, Matrix) else Matrix(value)
        self.B = B if isinstance(B, Vector) else Vector(B)
        
        self.latex_formatter.set_repr_mode(repr_mode)

    def set_repr_mode(self, mode: MODES) -> None:
        """
        Cambia el modo de representación del sistema lineal.
        """
        if mode not in {'ANSW', 'LES', 'MAT-SYS', 'AUG-MAT', 'PARAM'}:
            raise ValueError(f"Modo de representación no válido: {mode}")
        self.latex_formatter.set_repr_mode(mode)

    @property
    def value(self):
        return self._value

    @property
    def shape(self) -> Tuple[int, int]:
        """
        Retorna (n, m) = (# filas, # columnas) de la matriz A.
        """
        return self._value.shape  # Ajustar según tu implementación de Matrix

    def __add__(self, other: "LinearSystem") -> "LinearSystem":
        """
        Suma de sistemas lineales (suma término a término). 
        Se asume que tienen la misma dimensión.
        """
        # Suponiendo que Matrix y Vector soportan la operación +
        return LinearSystem(
            self._value.vstack(other._value),
            self.B.value + other.B.value,
        )


    def solve(self) -> Union[Vector,List[Vector], None]:
        """
        Resuelve el sistema Ax = b mediante eliminación de Gauss (o RREF).
        
        Maneja:
        - Sistema compatible con solución única.
        - Sistema compatible con infinitas soluciones.
        - Sistema incompatible (sin solución).
        
        Retorna:
        - Un `Vector` con la solución única, si existe solución única.
        - Un diccionario explicando que hay infinitas soluciones, con la
            solución particular y la base de direcciones libres, si hay
            infinitas soluciones.
        - `None` si el sistema es incompatible (o lanza ValueError).
        """
        n, m = self._value.shape
        b = self.B

        if len(b) != n:
            raise ValueError(
                "El tamaño del vector b no coincide con el número de filas de A."
            )

        # 1. Formar la matriz aumentada [A|b]
        M_aug = self._value.hstack(b)

        # 2. Realizar reducción a Fila-Escala (RREF)
        M_rref = M_aug.reduced_row_echelon_form()

        # 3. Analizar el rango de A y el rango de la aumentada.
        rankA = self._value.rg           # rango(A)
        rankAug = M_rref.rg              # rango([A|b]) calculado sobre la RREF

        # El número de variables es m
        # Casos:
        #   a) rank(A) < rank(A|b) => No hay solución (incompatible)
        #   b) rank(A) = rank(A|b) = m => Solución única
        #   c) rank(A) = rank(A|b) < m => Infinitas soluciones

        # Caso (a): Incompatible
        if rankAug > rankA:
            try:
                raise ValueError("Sistema incompatible (no tiene solución).")
            except ValueError as e:
                # Puedes usar return None o relanzar la excepción; según tu diseño.
                print(f'Error: {e}', file=sys.stderr)
                return None

        # Caso (b): Solución única
        if rankA == rankAug == m:
            # En la RREF, las primeras m columnas (0..m-1) deben formar
            # la identidad, y la última columna (col -1) es la solución particular.
            return M_rref.col(-1)  # Devuelve un Vector con la solución
        
        # Caso (c): Infinitas soluciones
        # rank(A) = rankAug < m
        # Calculamos la solución particular y los vectores libres.
        pivot_cols: List[int] = []
        row_i = 0
        # Identificamos las columnas pivote en la RREF (salvo la última columna)
        for col_j in range(m):
            if row_i < rankA:
                # Si el elemento en la fila row_i, col_j es != 0 (asumiendo RREF),
                # esa columna es pivote.
                if abs(M_rref[row_i][col_j]) > 1e-14:
                    pivot_cols.append(col_j)
                    row_i += 1

        # El resto de columnas (de 0..m-1) que no sean pivote, son variables libres
        free_cols = [j for j in range(m) if j not in pivot_cols]

        # Construimos la solución particular (poniendo a 0 las variables libres)
        x_part = [0.0 + 0.0j] * m
        # Para cada fila pivote, en la RREF tenemos que X[pivot_col] = b_i
        # menos la contribución de las (posibles) variables libres. Pero
        # al poner las libres = 0, se simplifica a x_part[pivot_col] = M_rref[i][-1].
        for i, pivot_col in enumerate(pivot_cols):
            x_part[pivot_col] = M_rref[i][-1]

        # Construimos los vectores dirección, uno por cada variable libre.
        direction_vectors: Set[Vector] = set()
        for free_col in free_cols:
            # Creamos un vector base, que corresponde a "poner 1 en la variable libre
            # 'free_col' y 0 en el resto de libres".
            x_dir = [0.0 + 0.0j] * m
            x_dir[free_col] = 1.0

            # Ajustamos las variables pivote según la ecuación de su fila:
            # pivot = b - sum(...) pero en RREF la fila i se ve:
            #    [0 ... 1 (pivot_col) ... coef(other free cols) ... | val]
            # => X[pivot_col] = val - sum_{j in free_cols}(coef[j]*X[j])
            # Como aquí X[free_col] = 1, y el resto de libres = 0,
            # nos queda que X[pivot_col] = -coef[free_col].
            for i, pivot_col in enumerate(pivot_cols):
                coef_free = M_rref[i][free_col]
                # En la RREF, la columna pivot_col debe ser 1 en esa fila,
                # y el coeficiente de la variable libre 'free_col' se encuentra
                # en M_rref[i][free_col].
                x_dir[pivot_col] = -coef_free
            x_dir = vector_to_integer_coords(x_dir)
            direction_vectors.add(Vector(x_dir))

        # Retornamos un diccionario con la información de infinitas soluciones
        return list(direction_vectors)
        
    def _repr_latex_(self, name: Optional[str] = None) -> str:
        """
        Genera la representación en LaTeX según el modo seleccionado.
        """
        return self.latex_formatter(self, name=name)

    @staticmethod
    def parse_equations(equations: List[str]) -> "LinearSystem":
        """
        Parsea ecuaciones lineales sin depender de Sympy.
        Variables pueden ser x0, x1, y, z, t, u, etc.
        """
        if not equations:
            raise ValueError("Se requiere al menos una ecuación.")

        # 1) Separar lados
        pairs: List[Tuple[str, str]] = []
        for eq in equations:
            if '=' not in eq:
                raise ValueError(f"Ecuación inválida, falta '=': '{eq}'")
            left, right = eq.split('=', 1)
            pairs.append((left.strip(), right.strip()))

        # 2) Obtener variables con regex ([A-Za-z]\w*)
        var_pat = re.compile(r'([A-Za-z]\w*)')
        var_set: Set[str] = set()
        for l, r in pairs:
            var_set |= set(var_pat.findall(l))
            var_set |= set(var_pat.findall(r))
        if not var_set:
            raise ValueError("No se encontraron variables en las ecuaciones.")
        variables = sorted(var_set)

        # 3) Definir parser de un lado a diccionario var->coef y "_const"
        def parse_side(expr: str) -> Dict[str, float]:
            expr = expr.replace('-', '+-')
            terms = [t for t in expr.replace(' ', '').split('+') if t]
            data: Dict[str, float] = {v: 0.0 for v in variables}
            data['_const'] = 0.0
            term_pat = re.compile(r'^([+-]?\d*\.?\d*)(?:\*?([A-Za-z]\w*))?$')
            for term in terms:
                m = term_pat.match(term)
                if not m:
                    raise ValueError(f"Término inválido: '{term}'")
                coef_str, var_str = m.groups()
                coef = float(coef_str) if coef_str not in ('', '+', '-') else (1.0 if coef_str != '-' else -1.0)
                if var_str:
                    data[var_str] = data.get(var_str, 0.0) + coef
                else:
                    data['_const'] += coef
            return data

        # 4) Construir matrices
        A: List[List[float]] = []
        B: List[float] = []
        for left, right in pairs:
            left_data = parse_side(left)
            right_data = parse_side(right)
            # mover right al left: left - right = 0
            row: List[float] = []
            for v in variables:
                coef = left_data.get(v, 0.0) - right_data.get(v, 0.0)
                row.append(coef)
            const = right_data['_const'] - left_data['_const']
            A.append(row)
            B.append(const)

        return LinearSystem(
            Matrix(A), 
            Vector(B)
        )

    def __str__(self) -> str:
        return f"Linear System:\nA = {self.value}\nB = {self.B}\n"