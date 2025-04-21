import sys
from typing import List, Optional, Set, Union, Dict, Tuple
import re
from fractions import Fraction
from math import lcm

from .vvector import Vector
from .mmatrix import Matrix

from .alg_types import T_Scalar, T_Vector, T_Matrix

def vector_to_integer_coords(vec_float: Union[T_Vector, Vector]) -> T_Vector:
    """
    Convierte un vector de floats en un vector con coeficientes enteros,
    escalando según el mcm de denominadores.
    """
    # 1) Convertir a fracciones
    fracs = [Fraction(f).limit_denominator(100000) for f in vec_float]

    # 2) Calcular M = mcm de los denominadores
    denoms = [f.denominator for f in fracs]
    M = 1
    for d in denoms:
        M = lcm(M, d)

    # 3) Multiplicar cada fracción por M
    return [int(M * f) for f in fracs]

class LinearSistem:
    """
    Representa un sistema de ecuaciones lineales de la forma A·X = B.
    Incluye detección de sistemas con solución única, infinitas soluciones
    o sin solución (incompatibles), y soporta el parseo de ecuaciones
    desde strings.
    """

    def __init__(
        self, 
        value: Union[Matrix, T_Matrix],     # Matriz de coeficientes A
        B: Union[Vector, T_Vector],         # Vector de términos independientes B
        repr_mode: str = "Answers"
    ):
        """
        Parámetros:
        -----------
        value: Matrix
            Matriz de coeficientes (A).
        B: Vector
            Vector de términos independientes (B).
        repr_mode: str
            - "Answers": Representación estándar (posibles soluciones).
            - "Linear-Equation-Sistem" o "LES": Muestra cada ecuación.
            - "Matrix-Sistem" o "MS": Visualiza como un sistema matricial.
            - "Augmented_Matrix" o "AM": Matriz aumentada.
        """
        # Matriz de coeficientes
        self._value = value if isinstance(value, Matrix) else Matrix(value)
        # Vector términos independientes
        self.B = B if isinstance(B, Vector) else Vector(B)
        # Modo de representación
        self.repr_mode = repr_mode

    @property
    def value(self):
        return self._value

    @property
    def shape(self) -> Tuple[int, int]:
        """
        Retorna (n, m) = (# filas, # columnas) de la matriz A.
        """
        return self._value.shape  # Ajustar según tu implementación de Matrix

    def __add__(self, other: "LinearSistem") -> "LinearSistem":
        """
        Suma de sistemas lineales (suma término a término). 
        Se asume que tienen la misma dimensión.
        """
        # Suponiendo que Matrix y Vector soportan la operación +
        return LinearSistem(
            self._value.vstack(other._value),
            self.B.value + other.B.value,
            repr_mode=self.repr_mode
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
        pivot_cols: List[T_Scalar] = []
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
        x_part = [0.0] * m
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
            x_dir = [0.0] * m
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
        Genera la representación en LaTeX según el modo seleccionado:
          - "Linear-Equation-Sistem" o "LES": muestra ecuaciones fila a fila.
          - "Answers" o "A": muestra, de modo simple, x_i = b_i.
          - "Matrix-Sistem" o "MS": sistema matricial [A|B].
          - "Augmented_Matrix" o "AM": matriz aumentada.
        """
        n, m = self.shape
        latex_output = ""
        mode = self.repr_mode

        if mode in ("Linear-Equation-Sistem", "LES"):
            latex_output += "\\begin{aligned}\n"
            for i in range(n):
                # Generar término a término: a_ij * x_j
                eq_terms: List[str] = []
                for j in range(m):
                    coef_ij = self._value[i][j]
                    eq_terms.append(f"{coef_ij}x_{{{j+1}}}")
                left_part = " + ".join(eq_terms)
                latex_output += f"{left_part} &= {self.B[i]} \\\\\n"
            latex_output += "\\end{aligned}"

        elif mode in ("Answers", "A"):
            # Suponiendo que B[i] ya son las soluciones y que se interpretan
            # como x_i. Esto es muy simplista, pero depende de tu convención.
            latex_output += "\\begin{aligned}\n"
            for i in range(n):
                latex_output += f"x_{{{i+1}}} = {self.B[i]} \\\\\n"
            latex_output += "\\end{aligned}"

        elif mode in ("Matrix-Sistem", "MS", "Augmented_Matrix", "AM"):
            # Son casi iguales, salvo que quizás quieras más detalle en "AM"
            latex_output += "\\left( \\begin{array}{"
            latex_output += "c" * m + " | c}\n"
            for i in range(n):
                fila_str = " & ".join(str(self._value[i][j]) for j in range(m))
                latex_output += f"{fila_str} & {self.B[i]} \\\\\n"
            latex_output += "\\end{array} \\right)"

        return f"${latex_output}$"

    @staticmethod
    def parse_equations(equations: List[str]) -> "LinearSistem":
        """
        Crea un objeto LinearSistem a partir de una lista de ecuaciones en formato string.
        Ejemplos de ecuaciones:
          "2*x + y = 3"
          "x - 5*y + 3*z = 7"
        
        NOTA: Este parser es básico y no cubre casos avanzados como 
              paréntesis anidados, exponenciales, etc. 
              Se asume que las ecuaciones vienen bien formadas, 
              con '+' y '-' como separadores principales.

        Retorna:
          LinearSistem con la matriz de coeficientes A y vector B.
        """
        # 1) Extraer todas las ecuaciones dividiéndolas en parte izquierda y derecha
        # 2) Identificar todas las variables involucradas para ordenarlas en columnas
        # 3) Construir las filas de la matriz A y el vector B

        # --- Paso 1: separar en "izquierda" y "derecha" ---
        left_right_pairs: List[Tuple[str, str]] = []
        for eq in equations:
            if "=" not in eq:
                raise ValueError(f"Ecuación inválida, falta '=': {eq}")
            left, right = eq.split("=")
            left, right = left.strip(), right.strip()
            left_right_pairs.append((left, right))

        # --- Paso 2: identificar variables (buscamos secuencias tipo x, y, z, t, etc.) ---
        #     Podríamos usar una expresión regular para capturar algo tipo:
        #         ([a-zA-Z_]\w*)   -> nombres de variable
        #     o un approach más manual. Aquí haremos algo básico.
        variable_set: Set[str] = set()
        var_pattern = re.compile(r'([a-zA-Z_]\w*)')  # ejemplo: x, y, var_1, etc.
        
        for left, right in left_right_pairs:
            # Buscar todas las variables en la izquierda y en la derecha
            vars_left = var_pattern.findall(left)
            vars_right = var_pattern.findall(right)
            for v in vars_left + vars_right:
                variable_set.add(v)

        # Ordenamos las variables alfabéticamente (o según convenga)
        variables = sorted(variable_set)

        # --- Paso 3: construir A y B ---
        #     Para cada ecuación, analizamos la parte izquierda (left)
        #     y movemos todo a la forma standard: (coef_1)*x_1 + ... = valor_derecha
        #     De la parte derecha, sacamos un valor (que puede tener variables, ojo).
        #     En un parser simple, asumiremos que la parte derecha es un número
        #     o una suma/resta de variables también.
        #     Para generalidad, parsearemos la parte derecha igual que la izquierda
        #     y luego moveremos todo a la izquierda.

        def parse_side(expr: str) -> Dict[str, float]:
            """
            Convierte una expresión tipo "2*x - 3*y + 4" en un dict:
            {
              'x': 2.0,
              'y': -3.0,
              '_const': 4.0
            }
            """
            # Sustituimos los signos '-' por '+-' para poder hacer split más fácil
            expr = expr.replace("-", "+-")
            # Dividimos por '+'
            terms = expr.split("+")
            result: Dict[str, T_Scalar] = {}
            result["_const"] = 0.0

            # Expresión regular para capturar un posible factor numérico
            # delante de la variable. Ej: "2*x", "-x", "3.5*y", etc.
            factor_var_pat = re.compile(r'^([+-]?\d*\.?\d*)\*?([a-zA-Z_]\w*)?$')

            for t in terms:
                t = t.strip()
                if t == "":
                    continue
                # Intentar hacer match
                match = factor_var_pat.match(t)
                if match:
                    factor_str, var_str = match.groups()
                    if factor_str in ("", "+", "-"):
                        # Significa 1 o -1
                        if factor_str.startswith("-"):
                            factor = -1.0
                        else:
                            factor = 1.0
                    else:
                        factor = float(factor_str)

                    if var_str is None or var_str == "":
                        # Significa término constante
                        result["_const"] += factor
                    else:
                        # Sumar en el diccionario
                        result[var_str] = result.get(var_str, 0.0) + factor
                else:
                    # Si no hace match, podría ser un término numérico suelto
                    # p.e. "3.5"
                    try:
                        val = float(t)
                        result["_const"] += val
                    except ValueError:
                        raise ValueError(f"Término inválido al parsear: '{t}'")
            return result

        # Construimos las filas de la forma A y B
        A: T_Matrix = []
        B: T_Vector = []

        for left, right in left_right_pairs:
            left_dict = parse_side(left)
            right_dict = parse_side(right)
            # Pasamos todo (right) al lado izquierdo: left - right = 0
            # => (left_dict[var] - right_dict[var]) * var + ... = 0
            for var in variables:
                left_dict[var] = left_dict.get(var, 0.0) - right_dict.get(var, 0.0)
            left_dict["_const"] = left_dict["_const"] - right_dict["_const"]

            # A: coeficientes de las variables en orden
            rowA: List[T_Scalar] = []
            for var in variables:
                rowA.append(left_dict.get(var, 0.0))

            # B: -_const (para que quede rowA * x = -const)
            #  Queremos left_dict[var]*x + ... = -left_dict["_const"]
            #  => A * X = B, con B = -_const.
            A.append(rowA)
            B.append(-left_dict["_const"])

        # Creamos la Matrix(A) y Vector(B) en tu librería
        from .mmatrix import Matrix
        from .vvector import Vector
        matA = Matrix(A)
        vecB = Vector(B)

        return LinearSistem(matA, vecB, repr_mode="Linear-Equation-Sistem")

