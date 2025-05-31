# ~/.ipython/profile_default/startup/00-latex_collections.py

from typing import Literal, Sequence, Any
from IPython import get_ipython

from .core import PrintingMode
from .printer_alg import LinAlgTextFormatter
from .printable import Printable

ip = get_ipython()

def seq_to_latex(seq: Sequence[Printable | Any], left_delim: str, right_delim: str):
    # 1) SOLO si hay al menos un elem. con _repr_latex_
    if not any(hasattr(item, '_repr_latex_') for item in seq):
        return None

    parts = []
    for item in seq:
        # Omitir None
        if item is None:
            continue

        # Caso Printable
        if hasattr(item, 'latex'):
            latex = item.latex()

        # Números
        elif isinstance(item, (int, float, complex)):
            latex = f"\\;{item}\\;"

        # Cadenas
        elif isinstance(item, str):
            safe = item.replace('{', '\\{').replace('}', '\\}')
            latex = f"\\;\\text{{{safe}}}\\;"

        else:
            # Cualquier otro tipo rompe el formato y sale al repr normal
            return None

        parts.append(latex)

    # Si tras filtrar sólo hubo None, volvemos al repr normal
    if not parts:
        return None

    body = ',\\quad'.join(parts)
    return f"${left_delim}{body}{right_delim}$"


def tuple_to_latex(tpl):
    return seq_to_latex(tpl, r"\left(", r"\right)")

def list_to_latex(lst):
    return seq_to_latex(lst,  r"\left[", r"\right]")

def set_to_latex(st):
    # Ordenamos por repr para salida consistente
    return seq_to_latex(sorted(st, key=lambda x: repr(x)), r"\left\{", r"\right\}")

if ip:
    # Registrar formateadores LaTeX
    fmt = ip.display_formatter.formatters['text/latex']
    fmt.for_type(tuple, tuple_to_latex)
    fmt.for_type(list,  list_to_latex)
    fmt.for_type(set,   set_to_latex)

def set_printing_mode(mode: Literal['Math', 'Physics']) -> None:
    if mode == 'Math': 
        LinAlgTextFormatter.set_printing_mode(PrintingMode.MATH)
    elif mode == 'Physics':
        LinAlgTextFormatter.set_printing_mode(PrintingMode.PHYSICS)
    else:
        raise ValueError(f'{mode} is not a valid argument. Use Literal["Math", "Physics"]')