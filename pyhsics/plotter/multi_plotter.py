from matplotlib import pyplot as plt
import numpy as np
from typing import Union, Dict, Iterable, Optional, Tuple
from .plotter import Plotter  # Ajusta la importación según la ubicación de Plotter

class MultiPlotter:
    """
    Clase para graficar múltiples ecuaciones en un único plot.
    
    Puede recibir como entrada:
      - Un diccionario de la forma {str: Plotter} para etiquetar cada curva.
      - Una colección (lista o set) de objetos Plotter, en cuyo caso se usará el etiquetado por defecto.
    """
    def __init__(self, plotters: Union[Dict[str, Plotter], Iterable[Plotter]]) -> None:
        """
        Inicializa el objeto MultiPlotter.
        
        Parámetros:
            plotters: Puede ser un diccionario {str: Plotter} o una colección (lista o set) de Plotter.
        """
        if isinstance(plotters, dict):
            if not plotters:
                raise ValueError("El diccionario de plotters no puede estar vacío.")
            self.plotters_dict: Dict[str, Plotter] = plotters
            self.plotters_list: Optional[list[Plotter]] = None
        else:
            plotters_list = list(plotters)
            if not plotters_list:
                raise ValueError("La colección de plotters no puede estar vacía.")
            self.plotters_list = plotters_list
            self.plotters_dict = None

    def plot(self, x_range: Tuple[float, float], num_points: int = 100) -> None:
        """
        Genera y muestra el gráfico combinando todas las funciones de los Plotter.
        
        Parámetros:
            x_range: Tupla (mínimo, máximo) para la variable independiente.
            num_points: Número de puntos para evaluar cada función.
        """
        x_values: np.ndarray = np.linspace(x_range[0], x_range[1], num_points)
        plt.figure(figsize=(8, 5))
        
        if self.plotters_dict is not None:
            # Itera sobre el diccionario, usando las claves como etiquetas personalizadas.
            for label, plotter in self.plotters_dict.items():
                y_values: np.ndarray = plotter.evaluate(x_values)
                plt.plot(x_values, y_values, label=label)
        else:
            # Itera sobre la lista de plotters, usando el etiquetado por defecto definido en cada objeto Plotter.
            for plotter in self.plotters_list:  # type: ignore
                y_values: np.ndarray = plotter.evaluate(x_values)
                label = f"{plotter.dependent_var} = {plotter.rhs.subs(plotter.subs_dict)}"
                plt.plot(x_values, y_values, label=label)
        
        # Se utiliza la variable independiente del primer Plotter para etiquetar el eje X.
        if self.plotters_dict is not None:
            any_plotter: Plotter = next(iter(self.plotters_dict.values()))
        else:
            any_plotter = self.plotters_list[0]  # type: ignore
        
        plt.xlabel(any_plotter.indep_variable)
        plt.ylabel(str(any_plotter.dependent_var))
        plt.title("Gráficas combinadas")
        plt.grid(True)
        plt.legend()
        plt.show()
