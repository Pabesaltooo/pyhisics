from matplotlib import pyplot as plt
import sympy as sp
import numpy as np
import pandas as pd
from typing import Dict, Union, Optional, Tuple, Callable
from ..quantity import Quantity
from ..measure import DirectMeasure

class Plotter:
    """
    Clase para graficar ecuaciones físicas en 2D.

    - Se recibe la ecuación completa (ej: "T = 2 * pi * sqrt(L/g)")
    - Se especifica la variable independiente (ej: 'L')
    - Se provee opcionalmente un diccionario con valores para los demás parámetros;
      si no se da, se asignan valores por defecto:
         - 0 si la parte derecha es una suma
         - 1 en caso contrario.
    - La parte izquierda (variable dependiente) se conserva para etiquetar la gráfica.
    """
    
    def __init__(self, expresion: str, variable: str, 
                 values: Optional[Dict[str, Union[Quantity, DirectMeasure, float, int]]] = None) -> None:
        """
        Inicializa la ecuación y define los valores de los parámetros.

        Parámetros:
            expresion: Ecuación en forma de cadena, ej. "T = 2*pi*sqrt(L/g)".
            variable: Nombre de la variable independiente, ej. "L".
            values: Diccionario opcional con valores para las demás variables.
                    Si no se provee, se asignan valores por defecto:
                      - 0 si la parte derecha es suma
                      - 1 en caso contrario.
        """
        # Diccionario para forzar que la variable independiente se trate como símbolo
        local_dict = {variable: sp.symbols(variable)}
        
        try:
            lhs, rhs = expresion.split("=")
        except ValueError:
            raise ValueError("La expresión debe contener exactamente un '=' para separar LHS y RHS.")
        
        self.dependent_var = sp.sympify(lhs.strip(), locals=local_dict)
        self.rhs = sp.sympify(rhs.strip(), locals=local_dict)
        
        self.indep_variable = variable  # ej: 'L'
        ind_sym = sp.symbols(self.indep_variable)
        
        free_syms = self.rhs.free_symbols
        subs_dict: Dict[sp.Symbol, float] = {}
        provided = {} if values is None else values
        
        for sym in free_syms:
            if sym == ind_sym:
                continue
            if sym.name in provided:
                val = provided[sym.name]
            else:
                default = 0 if self.rhs.is_Add else 1
                val = default
            if isinstance(val, (Quantity, DirectMeasure)):
                num_val = val.value
            else:
                num_val = float(val)
            subs_dict[sym] = num_val
        
        self.subs_dict = subs_dict

    def evaluate(self, x_values: np.ndarray) -> np.ndarray:
        """
        Evalúa la parte derecha de la ecuación para los valores dados de la variable independiente.

        Parámetros:
            x_values: Arreglo numpy con los valores de la variable independiente.

        Retorna:
            Arreglo numpy con los valores evaluados (Y) de la función, 
            con la misma cantidad de elementos que x_values.
        """
        ind_sym = sp.symbols(self.indep_variable)
        expr_evaluated = self.rhs.subs(self.subs_dict)
        f = sp.lambdify(ind_sym, expr_evaluated, 'numpy')
        return f(x_values)

    def plot(self, x_range: Tuple[float, float], num_points: int = 100) -> None:
        """
        Genera y muestra el gráfico de la función evaluada en función de la variable independiente.

        Parámetros:
            x_range: Tupla (mínimo, máximo) para la variable independiente.
            num_points: Número de puntos para evaluar la función.
        """
        x_values = np.linspace(x_range[0], x_range[1], num_points)
        y_values = self.evaluate(x_values)

        plt.figure(figsize=(8, 5))
        plt.plot(x_values, y_values, label=f"{self.dependent_var} = {self.rhs.subs(self.subs_dict)}", color='b')
        plt.xlabel(self.indep_variable)
        plt.ylabel(str(self.dependent_var))
        plt.title(f"Gráfico de {self.dependent_var} en función de {self.indep_variable}")
        plt.grid(True)
        plt.legend()
        plt.show()

    def linearize(self, x_range: Tuple[float, float], num_points: int = 100,
                   transformations: Optional[Dict[str, Callable[[np.ndarray], Optional[np.ndarray]]]] = None
                   ) -> pd.DataFrame:
        """
        Busca una transformación que linearice la relación entre la variable independiente y la dependiente.
        Para cada transformación candidata se ajusta una recta y se calcula el coeficiente de determinación (R²).
        Se selecciona la transformación que maximice R², se muestra un gráfico con los datos transformados y
        la recta de ajuste, y se devuelve un DataFrame con los parámetros del ajuste lineal.
        
        Además de los parámetros numéricos, se calculan las expresiones simbólicas de la pendiente y la intersección.
        La pendiente (Pendiente) y la intersección (Interseccion) indican, de forma numérica, la contribución
        de la variable independiente y el término constante. Los campos Pendiente_Simbolica e Interseccion_Simbolica
        contienen las expresiones simbólicas.
        
        Parámetros:
            x_range: Tupla (mínimo, máximo) para la variable independiente.
            num_points: Número de puntos para evaluar la función.
            transformations: Diccionario de transformaciones candidatas. Las claves son nombres y los valores son
                             funciones que reciben un array de numpy y retornan otro array (o None si no es aplicable).
                             Si es None se usan las transformaciones por defecto:
                             - "identity": sin transformación
                             - "square": al cuadrado
                             - "sqrt": raíz cuadrada (si los datos son no negativos)
                             - "log": logaritmo natural (si los datos son positivos)
                             - "inverse": inverso (si los datos son distintos de 0)
                             
        Retorna:
            DataFrame de pandas con una fila que contiene:
              - Transformacion: Nombre de la transformación seleccionada.
              - Pendiente: Valor numérico de la pendiente.
              - Pendiente_Simbolica: Expresión simbólica de la pendiente.
              - Interseccion: Valor numérico de la intersección (y₀).
              - Interseccion_Simbolica: Expresión simbólica de la intersección.
              - R2: Coeficiente de determinación del ajuste.
              - Ecuacion: Representación textual de la ecuación de la recta.
        """
        # Transformaciones numéricas por defecto
        if transformations is None:
            transformations = {
                "identity": lambda y: y,
                "square": lambda y: y**2,
                "sqrt": lambda y: np.sqrt(y) if np.all(y >= 0) else None,
                "log": lambda y: np.log(y) if np.all(y > 0) else None,
                "inverse": lambda y: 1/y if np.all(y != 0) else None,
            }
        
        # Transformaciones simbólicas correspondientes
        sym_transformations: Dict[str, Callable[[sp.Expr], sp.Expr]] = {
            "identity": lambda expr: expr,
            "square": lambda expr: expr**2,
            "sqrt": lambda expr: sp.sqrt(expr),
            "log": lambda expr: sp.log(expr),
            "inverse": lambda expr: 1/expr,
        }
        
        x_values = np.linspace(x_range[0], x_range[1], num_points)
        y_values = self.evaluate(x_values)
        
        best_r2 = -np.inf
        best_name: Optional[str] = None
        best_transformed: Optional[np.ndarray] = None
        best_fit: Optional[Tuple[float, float]] = None
        
        # Guarda resultados de cada transformación
        results = []
        
        for name, func in transformations.items():
            try:
                y_transformed = func(y_values)
                if y_transformed is None:
                    continue
            except Exception:
                continue
            
            # Ajuste lineal numérico: y = m*x + b
            m, b = np.polyfit(x_values, y_transformed, 1)
            y_fit = m * x_values + b
            
            # Calcular R²
            ss_res = np.sum((y_transformed - y_fit)**2)
            ss_tot = np.sum((y_transformed - np.mean(y_transformed))**2)
            r2 = 1 - ss_res/ss_tot if ss_tot != 0 else 0
            
            results.append({
                "Transformacion": name,
                "Pendiente": m,
                "Interseccion": b,
                "R2": r2,
                "Ecuacion": f"y = {m:.3f} x + {b:.3f}"
            })
            
            if r2 > best_r2:
                best_r2 = r2
                best_name = name
                best_transformed = y_transformed
                best_fit = (m, b)
        
        if best_name is None or best_transformed is None or best_fit is None:
            print("No se encontró una transformación adecuada para linearizar la relación.")
            return pd.DataFrame()
        
        # Cálculo simbólico usando la transformación elegida:
        # Se aplica la transformación simbólica a la parte derecha (con los valores sustituidos)
        sym_expr = sym_transformations[best_name](self.rhs.subs(self.subs_dict))
        x_sym = sp.symbols(self.indep_variable)
        # Intentamos expresar la función transformada como un polinomio lineal en x_sym
        try:
            poly = sp.Poly(sym_expr, x_sym)
        except sp.PolynomialError:
            poly = None
        
        if poly is not None and poly.degree() == 1:
            coeffs = poly.all_coeffs()
            m_sym = coeffs[0]
            b_sym = coeffs[1] if len(coeffs) > 1 else 0
        else:
            m_sym, b_sym = sp.nan, sp.nan  # No se pudo obtener la linealidad simbólica
        
        # Graficar los datos transformados y la recta de ajuste numérica
        plt.figure(figsize=(8, 5))
        plt.plot(x_values, best_transformed, 'o', label=f"Datos transformados ({best_name})")
        m_num, b_num = best_fit
        plt.plot(x_values, m_num*x_values + b_num, 'r-', 
                 label=f"Ajuste lineal: y = {m_num:.3f} x + {b_num:.3f}\nR² = {best_r2:.3f}")
        plt.xlabel(self.indep_variable)
        plt.ylabel(f"Transf({str(self.dependent_var)})")
        plt.title(f"Linearización usando transformación '{best_name}'")
        plt.grid(True)
        plt.legend()
        plt.show()
        
        # Preparar DataFrame con la información
        df = pd.DataFrame([{
            "Transformacion": best_name,
            "Pendiente": m_num,
            "Pendiente_Simbolica": str(m_sym),
            "Interseccion": b_num,
            "Interseccion_Simbolica": str(b_sym),
            "R2": best_r2,
            "Ecuacion": f"y = {m_num:.3f} x + {b_num:.3f}"
        }])
        
        return df
