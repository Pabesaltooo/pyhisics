from __future__ import annotations
from typing import Union, Optional, Dict, List

from ..algebraic_core import Algebraic, ScalarLike

from .symbolic_operator import SymPrintable
from .symbol import Symbol


# ----------------------------------------------------------
# 2) Definición de Term (un solo término de la forma coef * Π(símbolo^exponente))
# ----------------------------------------------------------
class Term(SymPrintable):
    """
    Un término es un coeficiente (numérico, o algo “algebraico”)
    multiplicado por un conjunto de símbolos con sus exponentes.
    Ej:  3 * x^2 * y^1
    """
    __slots__ = ("coefficient", "symbols_exponents")
    
    def __init__(self, coefficient: Union[Algebraic, ScalarLike], 
                 symbols_exponents: Optional[Dict[Symbol, ScalarLike]] = None):
        if symbols_exponents is None:
            symbols_exponents = {}
        if isinstance(coefficient, ScalarLike):
            from ..scalar import Scalar
            coefficient = Scalar(coefficient)

        self.coefficient = coefficient
        self.symbols_exponents = dict(symbols_exponents)  # copia
    
    def _repr_latex_(self, name: Optional[str] = None) -> str:        
        attoms: List[str] = []
        for sym, exp in self.symbols_exponents.items():
            if exp == 1:
                attoms.append(sym.latex())
            elif exp == 0:
                continue
            else:
                attoms.append(f'{sym.latex()}^{{{exp}}}')
        if self.coefficient.is_zero:
            return '$0$'
        if self.coefficient.is_identity:
            return f'${'\\,'.join(attoms)}$'
        if (-self.coefficient).is_identity:
            return f'$-{'\\,'.join(attoms)}$'
        return f"${self.coefficient.latex()} {' \\, '.join(attoms)}$"
    
    def is_zero(self) -> bool:
        return self.coefficient.is_zero
    
    def is_identity(self) -> bool:
        return self.coefficient.is_identity and all(exp == 0 for exp in self.symbols_exponents.values())
    
    def copy(self) -> Term:
        return Term(self.coefficient, self.symbols_exponents)

    def mul_symbol_power(self, symbol: Symbol, exponent: int) -> None:
        """
        Multiplica este término por `symbol^exponent`.
        Ajustamos la potencia dentro de `symbols_exponents`.
        """
        if exponent == 0:
            return  # no cambia nada
        old_exp = self.symbols_exponents.get(symbol, 0)
        new_exp = old_exp + exponent
        if new_exp == 0:
            # Se elimina si la potencia pasa a 0
            self.symbols_exponents.pop(symbol, None)
        else:
            self.symbols_exponents[symbol] = new_exp

    def __mul__(self, other: Term) -> Term:
        """
        Multiplica term * term => combinamos coeficientes y sumamos los exponentes.
        """
        if self.is_zero() or other.is_zero():
            return Term(0, {})
        
        new_coef = self.coefficient * other.coefficient
        new_syms = dict(self.symbols_exponents)
        # sumamos exponentes
        for sym, exp in other.symbols_exponents.items():
            new_syms[sym] = new_syms.get(sym, 0) + exp
            if new_syms[sym] == 0:
                new_syms.pop(sym, None)
        
        return Term(new_coef, new_syms)
    
    def __truediv__(self, other: Term) -> Term:
        if other.is_zero():
            raise ZeroDivisionError(f'No se puede dividir entre el tórmino {str(other)}, es 0.')
        
        new_coef = self.coefficient * other.coefficient
        new_syms = dict(self.symbols_exponents)
        # sumamos exponentes
        for sym, exp in other.symbols_exponents.items():
            new_syms[sym] = new_syms.get(sym, 0) - exp
            if new_syms[sym] == 0:
                new_syms.pop(sym, None)
        return Term(new_coef, new_syms)
        
           
    def __str__(self) -> str:
        from ...units.unit_printer import UnitPrinter
        superindice = UnitPrinter.superindice
        return f'{str(self.coefficient) if not self.coefficient.is_identity else ''}{''.join([str(sym) + superindice(exp) if exp != 1 else str(sym) for sym, exp in self.symbols_exponents.items()])}'

