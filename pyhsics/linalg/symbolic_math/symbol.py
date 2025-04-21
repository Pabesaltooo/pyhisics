from __future__ import annotations
from typing import Iterable, List, TYPE_CHECKING, Optional, Union

from .symbolic_operator import ExprOperable, SymPrintable

if TYPE_CHECKING:
    from .expression import Expression


class Kinds:
    """
    Tipos de variables simbólicas.
    """
    Scalar = "Scalar"
    Vector = "Vector"
    Matrix = "Matrix"
    Polynomial = "Poly"
    Function = "Function"


class Symbol(SymPrintable, ExprOperable):
    """
    Representa una variable simbólica. Puede tener un '`kind`'
    (Scalar, Vector, Matrix...) para validaciones de suma.
    """
    __slots__ = ("name", "kind")
    
    def __init__(self, name: str, kind: str = Kinds.Scalar):
        self.name = name
        self.kind = kind  # p.ej. "Scalar", "Matrix", "Vector", etc.
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Symbol):
            return False
        return (self.name == other.name) and (self.kind == other.kind)
    
    def __hash__(self) -> int:
        return hash((self.name, self.kind))
    
    def __str__(self):
        return self.name
    
    def _repr_latex_(self, name: str | None = None) -> str:
        if name is None:
            name = self.name
        if self.kind == Kinds.Vector:
            return f"$\\vec{{{name}}}$"
        return f"${name}$"
    
    def __neg__(self) -> Expression:
        from .term import Term
        from .expression import Expression
        return Expression([Term(-1, {self: 1})])

class Symbols:
    def __init__(self, syms: List[Symbol]):
        self.syms = syms

    def __iter__(self) -> Symbols:
        self._iter_index = 0  # Initialize the iteration index
        return self

    def __next__(self) -> Symbol:
        if self._iter_index < len(self.syms):
            result = self.syms[self._iter_index]
            self._iter_index += 1
            return result
        else:
            raise StopIteration

    def __getitem__(self, index: int) -> Symbol:
        return self.syms[index]

    def __len__(self) -> int:
        return len(self.syms)

    def __call__(self, index: int) -> Symbol:
        return self.syms[index]
    
    def to_single(self) -> Union[Symbol, Symbols]:
        if len(self.syms) == 1:
            return self.syms[0]
        return self


def symbols(syms: str, kind: str = 'Scalar') -> Symbols:
    return Symbols([Symbol(s, kind) for s in syms.split()])

