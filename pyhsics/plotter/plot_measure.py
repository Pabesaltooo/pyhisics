from dataclasses import dataclass, field
from typing import Dict, List
import matplotlib.pyplot as plt

from ..measure.base_measure import MeasureBaseClass

# Ejemplo de una posible clase BaseMeasure:
# class BaseMeasure:
#     def __init__(self, value, error, name=""):
#         self.value = value
#         self.error = error
#         self.name = name

@dataclass(frozen=True)
class MeasurePlotter:
    """
    Clase responsable de graficar una sola medida (BaseMeasure) en un eje unidimensional,
    incluyendo su valor central y su rango de error.
    """
    measure: "MeasureBaseClass"       
    _flags: Dict[str, bool] = field(default_factory=dict, init=False, repr=False)
    
    def config(self, flag: str, mode: bool) -> None:
        """
        Configura flags adicionales para el plot, almacenándolos en un diccionario interno.
        """
        object.__setattr__(self, '_flags', {**self._flags, flag: mode})
        
    def export_data(self) -> Dict[str, float]:
        """
        Exporta los datos de la medida en un diccionario:
          - 'left':   valor - error
          - 'center': valor central
          - 'right':  valor + error
        """
        value = float(self.measure.value)
        error = float(self.measure.error)
        return {
            'left':   value - error,
            'center': value,
            'right':  value + error
        }

@dataclass
class MultiMeasurePlotter:
    """
    Clase que agrupa varios MeasurePlotter para dibujarlos en un mismo
    gráfico unidimensional. Puede alternar automáticamente el offset (arriba/abajo de y=0)
    si enable_offset=True, o dibujar todas las medidas en la línea y=0 si enable_offset=False.
    """
    plotters: List[MeasurePlotter]
    
    # Flag para activar/desactivar el offset vertical
    enable_offset: bool = True
    
    @classmethod
    def from_measures(cls, measures: List["MeasureBaseClass"], enable_offset: bool = True) -> "MultiMeasurePlotter":
        """
        Crea una instancia de MultiMeasurePlotter a partir de una lista de medidas
        (BaseMeasure). Cada medida se envuelve en un MeasurePlotter.
        
        :param measures: lista de instancias BaseMeasure
        :param enable_offset: si True, se aplicará el offset vertical alternado
        """
        plotters = [MeasurePlotter(measure=m) for m in measures]
        return cls(plotters=plotters, enable_offset=enable_offset)
    
    def _alternating_offset(self, i: int, step: float) -> float:
        """
        Devuelve un offset vertical que alterna por encima/abajo de y=0:
           i=0 -> 0       (en y=0)
           i=1 -> +step   (arriba)
           i=2 -> -step   (abajo)
           i=3 -> +2*step
           i=4 -> -2*step
           etc.
        """
        if i == 0:
            return 0.0
        half = (i + 1) // 2  # cuántos "escalones" de step
        sign = 1 if i % 2 == 1 else -1
        return half * step * sign
    
    def plot(self) -> None:
        """
        Dibuja todas las medidas sobre un mismo eje horizontal. Si enable_offset=True,
        se alternan arriba/abajo de la línea y=0. Si enable_offset=False, se dibujan
        todas en y=0.
        
        - Línea negra gruesa en y=0
        - Cuadrícula activada
        - Leyenda con el nombre de cada medida
        """
        
        # CONFIGURACIÓN BÁSICA: colores, marcadores, etc.
        colors = ['blue', 'green', 'red', 'purple', 'orange', 'brown', 'gray']
        markers = ['o', 'x', 's', 'D', '^', 'v', 'P']
        offset_step = 1.0  # separación vertical para cada “escalón”
        
        # Cálculo de límites globales (min y max en X)
        data_list = [p.export_data() for p in self.plotters]
        global_left = min(d['left'] for d in data_list)
        global_right = max(d['right'] for d in data_list)
        x_range = (global_right - global_left)
        x_margin = 0.1 * x_range if x_range != 0 else 1.0
        
        # Si offset está habilitado, calculamos offsets alternados; de lo contrario, todos en 0
        if self.enable_offset:
            offsets = [self._alternating_offset(i, offset_step) for i in range(len(self.plotters))]
        else:
            offsets = [0.0] * len(self.plotters)  # Todos en y=0
        
        # Definimos un margen vertical para que no queden pegadas las líneas
        y_min = min(offsets) - offset_step
        y_max = max(offsets) + offset_step
        
        # Creamos la figura
        fig, ax = plt.subplots(figsize=(9, 3))
        
        # Línea de referencia negra y gruesa en y=0 (extendida con x_margin)
        ax.hlines(
            y=0,
            xmin=global_left - x_margin,
            xmax=global_right + x_margin,
            color='black',
            linewidth=3
        )
        
        # Para la leyenda
        handles, labels = [], []
        
        # Dibujamos cada medida
        for i, plotter in enumerate(self.plotters):
            data = plotter.export_data()
            left, center, right = data['left'], data['center'], data['right']
            
            color = colors[i % len(colors)]
            marker = markers[i % len(markers)]
            
            # Offset vertical
            y_offset = offsets[i]
            
            # Nombre de la medida
            measure_label = getattr(plotter.measure, 'name', f"Medida {i+1}")
            
            # Una sola línea con tres puntos (para que la leyenda sea un único handle)
            line, = ax.plot(
                [left, center, right],
                [y_offset, y_offset, y_offset],
                color=color,
                linewidth=5,
                alpha=0.7,
                marker=marker,
                markevery=[1],   # marcador solo en el valor central
                markersize=9,
                label=measure_label
            )
            
            # Una sola línea con tres puntos (para que la leyenda sea un único handle)
            contorno, = ax.plot(
                [left, center, right],
                [y_offset, y_offset, y_offset],
                color=color,
                linewidth=20,
                alpha=0.1,
            )
            
            # Guardamos para la leyenda
            handles.append(line)
            labels.append(measure_label)
            
            # Ajuste del texto para evitar superposición
            if y_offset > 0:
                text_y = y_offset + 0.25
            elif y_offset < 0:
                text_y = y_offset - 0.35
            else:
                text_y = y_offset + 0.25  # si y=0, lo ponemos un poco arriba
            
            va = 'bottom' if offset_step >= 0 else 'top'
            # Ponemos el texto en left, center y right
            ax.text(left,   text_y, f"{left:.2f}",   ha='right', va=va, color=color)
            ax.text(center, text_y, f"{center:.2f}", ha='center', va='center', color=color)
            ax.text(right,  text_y, f"{right:.2f}",  ha='left', va=va, color=color)
        
        # Ajuste de ejes
        ax.set_xlim(global_left - x_margin, global_right + x_margin)
        ax.set_ylim(y_min, y_max)
        
        # Activamos la cuadrícula
        ax.grid(True, linestyle='--', alpha=0.9)
        
        # Leyenda
        ax.legend(handles, labels, loc='upper right')
        
        # Ocultamos ejes
        ax.axis('off')
        
        plt.tight_layout()
        plt.show()
