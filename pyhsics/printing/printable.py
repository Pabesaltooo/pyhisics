from abc import ABC, abstractmethod
from typing import Optional
from IPython.display import Latex, display  # type: ignore

class Printable(ABC):
    """
    Interfaz para objetos representables.
    
    Proporciona un protocolo para:
      - Representación en cadena de texto (`__str__`) para entornos de consola.
      - Representación en LaTeX (`_repr_latex_`) para notebooks Jupyter, retornando un string 
        que debe comenzar y terminar con '$'.
      
    Métodos implementados:
      - latex() : Devuelve la representación en LaTeX sin los delimitadores '$'.
      - __repr__() : Devuelve una cadena descriptiva.
      - display_latex() : Muestra la representación en LaTeX del objeto usando IPython.display.
    """
    
    @abstractmethod
    def __str__(self) -> str:
        """
        Retorna la representación del objeto como cadena de texto.
        
        Returns:
            str: Representación en texto del objeto.
        """
        pass
    
    @abstractmethod
    def _repr_latex_(self) -> str:
        """
        Retorna la representación del objeto en LaTeX.
        El string debe comenzar y terminar con '$'.
        
        Returns:
            str: Representación en LaTeX.
        """
        pass
    
    def latex(self) -> str:
        """
        Devuelve la representación en LaTeX del objeto sin los delimitadores '$'.
        
        Returns:
            str: Representación en LaTeX limpia.
        """
        return self._repr_latex_().replace('$', '')
    
    def __repr__(self) -> str:
        """
        Método de representación del objeto.
        
        Devuelve una cadena formada por el nombre de la clase y la representación estándar (obtenida mediante __str__).
        
        Returns:
            str: Representación del objeto para entornos no interactivos.
        """
        return f'{self.__class__.__name__}({str(self)})'
    
    def display_latex(self, name: Optional[str] = None) -> None:
        """
        Muestra la representación en LaTeX del objeto en un entorno Jupyter.
        
        Args:
            name (Optional[str]): (Opcional) Nombre identificador para el objeto mostrado. Actualmente
                                    no influye en la representación pero se deja para posibles extensiones.
        """
        display(Latex(self._repr_latex_()))
