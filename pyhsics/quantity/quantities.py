from __future__ import annotations
from typing import Iterator, Type, TypeVar, Any, List, Optional
import ast

from pyhsics.linalg import ScalarLike
from pyhsics.quantity.core_quantity import Quantity
from pyhsics.quantity.scalar_quantity import ScalarQuantity
from pyhsics.quantity.vector_quantity import VectorQuantity

T = TypeVar('T', bound=Quantity[Any])

def _split_outside_brackets(s: str) -> List[str]:
    """Divide la cadena `s` en comas que no están dentro de corchetes."""
    parts: List[str] = []
    depth = 0
    start = 0
    for i, ch in enumerate(s):
        if ch == '[':
            depth += 1
        elif ch == ']':
            if depth > 0:
                depth -= 1
        elif (ch == ',') and depth == 0:
            parts.append(s[start:i])
            start = i + 1
    parts.append(s[start:])
    return parts

def quantities(names: str, *, cls: Type[T] = ScalarQuantity) -> Iterator[T]:
    """
    Parsea una cadena de cantidades separadas por comas y devuelve:
      - Una única instancia de `Quantity` (o subclase, si se pasó `cls`) 
        si en la cadena solo hay UNA cantidad.
      - Un iterador de instancias de `Quantity` (o subclase) si hay MÁS de una.

    Cada “cantidad” puede tener las formas:
      - "<valor> <unidad>" (con unidad opcional). Ejemplo: "10 kg" o "5".
      - "<vector> <unidad>" si el valor comienza y termina con corchetes. Ejemplo: "[1, 2, 3] m/s".

    Si no se especifica unidad, se crea la cantidad como adimensional.

    Ejemplos de uso:
        >>> quantities("11 m")
        Quantity(11.0, "m")

        >>> quantities("11")
        Quantity(11.0)

        >>> it = quantities("10 kg, [1,2,3] m/s, 5 N, 7")
        >>> list(it)
        [Quantity(10.0, "kg"), Quantity([1.0, 2.0, 3.0], "m/s"), Quantity(5.0, "N"), Quantity(7.0)]

        >>> quantities("2.5", cls=ScalarQuantity)
        ScalarQuantity(2.5)

        >>> quantities("[1,2,3] m/s", cls=ScalarQuantity)
        Traceback (most recent call last):
            ...
        ValueError: No se puede crear ScalarQuantity a partir de un valor vectorial.

        >>> quantities("7", cls=VectorQuantity)
        Traceback (most recent call last):
            ...
        ValueError: No se puede crear VectorQuantity a partir de un valor escalar.

    Parámetros
    ----------
    names : str
        Cadena con una o varias “cantidades” separadas por comas. Cada
        elemento puede seguir el patrón "<valor> <unidad>" o solo "<valor>".
        No deben haber comas dentro de la parte de valor vectorial.
    cls : Type[T], opcional
        Clase a instanciar para cada cantidad. Por defecto `Quantity`.
        Puede pasarse `ScalarQuantity` o `VectorQuantity` (o cualquier
        subtipo de `Quantity[Any]`). Si se intenta crear `ScalarQuantity` de
        un vector, o `VectorQuantity` de un escalar, se lanza `ValueError`.

    Devuelve
    -------
    Union[T, Iterator[T]]
        - Si sólo hay una cantidad en `names`, se devuelve directamente esa
          instancia de tipo `T`.
        - Si hay varias, se devuelve un iterador que genera instancias de
          tipo `T`.

    Excepciones
    ----------
    ValueError
        - Si alguna parte no sigue el formato válido.
        - Si el valor escalar no se puede convertir a float.
        - Si el valor vectorial no es una lista/tupla de números válida.
        - Si `cls` es `ScalarQuantity` y se pasa un vector.
        - Si `cls` es `VectorQuantity` y se pasa un escalar.
    """
    
    for part in _split_outside_brackets(names):
        token = part.strip()
        if not token:
            continue

        value_unit = token.split(None, 1)
        if len(value_unit) == 1:
            val_str = value_unit[0]
            unit: Optional[str] = None
        else:
            val_str, unit = value_unit
        value = (
            parse_vector(cls, val_str) if val_str.startswith('[') and val_str.endswith(']') 
            else parse_scalar(cls, val_str))

        yield cls(value, unit) if unit is not None else cls(value)


def parse_scalar(cls: type, val_str: str) -> ScalarLike:
    try:
        scalar = float(val_str)
    except ValueError:
        raise ValueError(f"Valor escalar inválido: '{val_str}'.")
    value = scalar
    if cls is VectorQuantity:
        raise ValueError("No se puede crear VectorQuantity a partir de un valor escalar.")
    return value

def parse_vector(cls: type, val_str: str) -> List[ScalarLike]:
    try:
        raw = ast.literal_eval(val_str)
    except (SyntaxError, ValueError):
        raise ValueError(f"Valor vectorial inválido: '{val_str}'.")
    if not isinstance(raw, (list, tuple)):
        raise ValueError(f"Valor vectorial inválido: '{val_str}'.")
    lista_floats: List[ScalarLike] = []
    for elem in raw:
        try:
            lista_floats.append(float(elem))
        except (TypeError, ValueError):
            raise ValueError(f"Valor vectorial inválido: '{val_str}'.")
    if cls is ScalarQuantity:
                raise ValueError("No se puede crear ScalarQuantity a partir de un valor vectorial.")
    return lista_floats
