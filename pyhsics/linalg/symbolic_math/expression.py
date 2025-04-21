from __future__ import annotations
from typing import Tuple, Optional, List, Dict

from ..alg_types import T_Scalar, Algebraic

from .symbolic_operator import ExprOperable, SymPrintable
from .symbol import Symbol
from .term import Term



def canonical_key(term: Term) -> Tuple[Tuple[Symbol, T_Scalar], ...]:
        """
        Dado un 'Term', retorna una tupla inmutable que represente
        la parte simbólica de manera única y ordenada.
        Por ejemplo, si term.symbols_exponents = {x: 2, y: 1},
        la clave podría ser (("x",2),("y",1)) si x.name = "x" y y.name="y".
        """
        items_sorted = sorted(
            term.symbols_exponents.items(),
            key=lambda kv: (kv[0].name, kv[0].kind)
        )
        return tuple((sym, exp) for (sym, exp) in items_sorted)

# ----------------------------------------------------------
# 3) Definición de Expression (una suma de Términos)
# ----------------------------------------------------------
class Expression(SymPrintable, ExprOperable):
    """
    Expresión = suma de Terms.
    Internamente podemos almacenar una lista o un dict
    (p.ej. dict que asocia un "frozen" de symbol->exponent con la coefficient).
    Para simplificar, usamos lista de Terms y los combinamos cuando se requiera.
    """
    __slots__ = ("terms",'is_positive', 'is_abs')

    def __init__(self, terms: Optional[List[Term]] = None):
        if terms is None:
            terms = []
        self.terms = terms
        
        # Podríamos hacer una “simplificación” inicial.



    def _repr_latex_(self, name: str | None = None) -> str:
        if not self.terms:
            return '$$'
        rv = str(self.terms[0])
        for term in self.terms[1:]:
            if '-' in str(term) :
                rv += ' - ' + term.latex().strip('-')
            else:
                rv += ' + ' + term.latex()
        return "$"+ rv + "$"
    

    def __str__(self):        
        if not self.terms:
            return "0"
        return " + ".join(str(t) for t in self.terms if not t.is_zero())
    
    
    def copy(self) -> Expression:
        return Expression([t.copy() for t in self.terms])

    def simplify(self) -> Expression:
        """
        Combina términos que tengan la misma parte simbólica.
        El “truco” es agrupar por la tupla (Symbol->exponent) inmutable.
        """
        accum: Dict[Tuple[Tuple[Symbol, T_Scalar], ...], Algebraic] = {}
        
        for term in self.terms:
            if term.is_zero():
                continue
            key = canonical_key(term)
            if key in accum:
                accum[key] = accum[key] + term.coefficient
            else:
                accum[key] = term.coefficient

        
        new_terms: List[Term] = []
        for key, coef in accum.items():
            if coef.is_zero:
                continue
            symbols_exponents = dict(key)
            new_terms.append(Term(coef, symbols_exponents))
            
        return Expression(new_terms)
    
    def __neg__(self) -> Expression:
        new_terms: List[Term] = []
        for t in self.terms:
            new_terms.append(Term(-t.coefficient, t.symbols_exponents))
        return Expression(new_terms)


    def is_zero(self) -> bool:
        return all(t.is_zero() for t in self.terms)

    def is_identity(self) -> bool:
        return all(t.is_identity() for t in self.terms)
    
    def __abs__(self) -> Expression:
        return self