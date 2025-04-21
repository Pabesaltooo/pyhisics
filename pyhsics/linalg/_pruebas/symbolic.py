from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterable, List, Mapping, Optional, Tuple, Union
from .exceptions import *
from .printable import Printable # Obliga a implementar _repr_latex_ y __str__ (tiene implementado por defecto __repr__, latex(), display_latex())
from .number import Number, InAlgebraicGroup, T_Numeric # Number es un Wrapper de int, complex, float...


class Basic(ABC):
    @property
    def args(self) -> Tuple[Basic, ...]:
        """Tupla inmutable de sub‑expresiones canónicas."""
        return ()
    
    def __hash__(self) -> int:
        return hash( (self.__class__, self._hashable_content()))

    def __eq__(self, other: object) -> bool:
        return (type(self) is type(other) and
            self._hashable_content == other._hashable_content)

    def _hashable_content(self) -> Tuple:
        """"""
        return self.args
    
    # -------------------- API simbólica mínima --------------------
    def simplify(self):
        """Devuelve versión simplificada (llama a _eval_simplify)."""
        simp = self._eval_simplify()
        return simp if simp is not None else self

    # métodos _eval_* devuelven None cuando no aplican
    def _eval_simplify(self):  # noqa: D401
        return None

    # -------------------- utilidades varias --------------------
    def to_expression(self):  # compatibilidad con tu interfaz anterior
        return self

class Add:
    pass

class Mul:
    __slots__ = ("_coeff", "_factors")
    
    def __new__(cls, *factors: ExprOperable):
        # --------------------------------------------------------------------------------
        # 1) Aplanar (Mul(a, Mul(b,c)) → a, b, c) y convertir todo a Expr
        # --------------------------------------------------------------------------------
        flat: List[Expr] = []
        for f in factors:
            e = _as_expr(f)
            if isinstance(e, Mul):
                flat.extend(e._factors)
                if not e._coeff.is_identity():
                    flat.append(e._coeff)
            else:
                flat.append(e)

        # --------------------------------------------------------------------------------
        # 2) Separar coeficiente numérico de los factores simbólicos
        # --------------------------------------------------------------------------------
        coeff = Number(1)
        symbolic: List[Expr] = []
        for f in flat:
            if isinstance(f, Number):
                coeff *= f  # type: ignore[operator]
            else:
                symbolic.append(f)

        # Si el coeficiente es 0 → toda la expresión es 0
        if coeff.is_zero():
            return coeff.to_expression()

        # --------------------------------------------------------------------------------
        # 3) Orden canónico (por __hash__)
        # --------------------------------------------------------------------------------
        symbolic = sorted(symbolic, key=hash)

        obj = super().__new__(cls)
        object.__setattr__(obj, "_coeff", coeff)
        object.__setattr__(obj, "_factors", tuple(symbolic))
        return obj

    #
    

class Pow:
    pass

def _as_expr(a: ExprOperable) -> Expr:
    ...

ExprOperable = Union[Number, T_Numeric, Basic]

class Expr(Basic, InAlgebraicGroup):
    # --------------- operadores infix ---------------
    def __add__(self, other: ExprOperable) -> "Add":  # type: ignore[override]
        return Add(self, _as_expr(other))
    __radd__ = __add__
    def __sub__(self, other: ExprOperable) -> "Add":  # type: ignore[override]
        return Add(self, (-_as_expr(other)))
    def __rsub__(self, other: ExprOperable) -> "Add":  # type: ignore[override]
        return Add(_as_expr(other), (-self))
    def __mul__(self, other: ExprOperable) -> "Mul":  # type: ignore[override]
        return Mul(self, _as_expr(other))
    __rmul__ = __mul__
    def __truediv__(self, other: ExprOperable) -> "Mul":  # type: ignore[override]
        return Mul(self, (_as_expr(other)).inv())
    def __rtruediv__(self, other: ExprOperable) -> "Mul":  # type: ignore[override]
        return Mul(_as_expr(other), self.inv())
    def __pow__(self, other: ExprOperable):  # type: ignore[override]
        return Pow(self, _as_expr(other))
    def __neg__(self):  # type: ignore[override]
        return Mul(Number(-1), self)

    def neg(self):  # noqa: D401
        return -self
    def inv(self):  # noqa: D401
        return Pow(self, _as_expr(-1))

@dataclass(frozen=True, slots=True)
class Symbol(Expr, Printable):
    """Representa un símbolo base (escalares, vectores, matrices, etc.)."""

    name: str
    _is_zero: bool = field(default=False, repr=False)
    _is_identity: bool = field(default=False, repr=False)
    _is_positive: bool = field(default=False, repr=False)
    _is_negative: bool = field(default=False, repr=False)
    _is_real: bool = field(default=False, repr=False)
    _is_complex: bool = field(default=False, repr=False)

    def _hashable_content(self):
        return (self.name,)

    # --- Printable interface ----
    def _repr_latex_(self) -> str:
        return f"${self.name}$"
    def __str__(self) -> str:
        return self.name

    # --- Algebraic helpers ----
    def to_expression(self) -> Expression:
        return Expression([_Term(Number(1), {self: Number(1)})])
    def is_zero(self) -> bool:
        return self._is_zero
    def is_identity(self) -> bool:
        return self._is_identity
    def neg(self) -> Expression:
        return Expression([_Term(Number(-1), {self: Number(1)})])
    def inv(self) -> Expression:
        return Expression([_Term(Number(1), {self: Number(-1)})])

@dataclass(frozen=True, slots=True)
class _Term(Basic, InAlgebraicGroup, Printable):
    """
    Representa un término: coeficiente * ∏ símbolo^exponente
    """

    coeff: Number
    sym_dict: Mapping[Symbol, Number] = field(default_factory=dict)

    def _hashable_content(self):
        return (self.coeff, tuple(sorted(self.sym_dict.items(), key=lambda kv: kv[0].name)))

    @property
    def args(self):
        return self._hashable_content()

    # ------------- Operaciones internas -------------
    def __mul__(self, other: _Term) -> _Term:
        new_coeff = self.coeff * other.coeff
        new_dict: Dict[Symbol, Number] = dict(self.sym_dict)
        for sym, exp in other.sym_dict.items():
            new_dict[sym] = new_dict.get(sym, Number(0)) + exp
        return _Term(new_coeff, new_dict)
    def __truediv__(self, other: _Term) -> _Term:
        if other.coeff.is_zero():
            raise ZeroDivisionError("División por cero en coeficiente.")
        new_coeff = self.coeff / other.coeff
        new_dict: Dict[Symbol, Number] = dict(self.sym_dict)
        for sym, exp in other.sym_dict.items():
            new_dict[sym] = new_dict.get(sym, Number(0)) - exp
        return _Term(new_coeff, new_dict)
    def __neg__(self) -> _Term:
        return _Term(self.coeff.neg(), self.sym_dict)

    # ------------- Printable -------------
    def _fmt_coeff(self) -> str:
        if self.coeff.is_identity():
            return "" # 1·x → x
        if (self.coeff.neg()).is_identity():
            return "-" # -1·x → -x
        return self.coeff.latex()
    def _repr_latex_(self) -> str:
        if self.coeff.is_zero():
            return "${0}$"
        if not self.sym_dict:
            return f'${{{self.coeff.latex()}}}$'

        coef = self._fmt_coeff()
        symbols = " \\, ".join(
            f"{{{{{sym.latex()}}}^{{{exp.value}}}}}" if not exp.is_identity() else {{{sym.latex()}}}
            for sym, exp in self.sym_dict.items()
        )
        return f"${coef}\\,{symbols}$"
    def __str__(self) -> str:
        if self.coeff.is_zero():
            return "0"
        if not self.sym_dict:
            return str(self.coeff)

        coef = self._fmt_coeff()
        symbols = "·".join(
            f"{sym}^{exp}" if not exp.is_identity() else f"{sym}"
            for sym, exp in self.sym_dict.items()
        )
        return f"{coef}{symbols}"
    
    # --- Algebraic helpers ----
    def is_zero(self) -> bool:
        return self.coeff.is_zero()
    def is_identity(self) -> bool:
        return self.coeff.is_identity() and all(exp.is_zero() for exp in self.sym_dict.values())
    def neg(self) -> _Term:
        return -self
    def inv(self) -> _Term:
        inv_dict = {sym: -exp for sym, exp in self.sym_dict.items()}
        return _Term(self.coeff.inv(), inv_dict)
    def to_expression(self) -> Expression:
        return Expression([self])
    
class Expression(Expr, Printable):
    """Colección ordenada de :class:`_Term`."""
    __slots__ = ("terms",)

    def __init__(self, terms: Optional[Union[Iterable[_Term], Number, T_Numeric, _Term, Symbol]]=None):
        if terms is None:
            terms = _Term(0)
        elif isinstance(terms, Symbol):
            terms = _Term(1, {terms: 1})
        elif isinstance(terms, T_Numeric):
            terms = _Term(terms)
        elif isinstance(terms, Number):
            terms = _Term(terms)
        self.terms = [terms] if isinstance(terms, _Term) else list(terms)
      
    # ------------- Simplificación -------------
    def simplify(self) -> Expression:
        numeric_sum = Number(0)
        grouped: Dict[FrozenSet[Tuple[Symbol, Number]], Number] = {}

        for term in self.terms:
            if not term.sym_dict:
                numeric_sum += term.coeff
                continue

            key = frozenset(term.sym_dict.items())
            grouped[key] = grouped.get(key, Number(0)) + term.coeff

        new_terms: List[_Term] = []
        if not numeric_sum.is_zero():
            new_terms.append(_Term(numeric_sum))

        for key, coeff in grouped.items():
            if not coeff.is_zero():
                new_terms.append(_Term(coeff, dict(key)))

        if not new_terms:
            new_terms.append(_Term(Number(0)))

        return Expression(new_terms)
        
    # ------------- Printable -------------
    def _repr_latex_(self) -> str:
        return f'${' + '.join(t.latex() for t in self.terms).replace('+ -', '- ')}$'
    def __str__(self) -> str:
        return ' + '.join(str(t) for t in self.terms).replace('+ -', '- ')
    
    # ------------- Algebraic helpers -------------
    def to_expression(self) -> Expression:
        return self
    def is_zero(self) -> bool:
        return all(t.is_zero() for t in self.terms)
    def is_identity(self) -> bool:
        return len(self.terms) == 1 and self.terms[0].is_identity()
    def neg(self) -> Expression:
        return Expression(-t for t in self.terms)
    def inv(self) -> Pow:
        return Pow(self, Expression(-1))
    
    def __hash__(self) -> int:
        return hash(tuple(sorted(self.terms, key=hash)))

class Pow(Expr, Printable):
    __slots__ = ("base", "exp")

    def __init__(self, base: ExprOperable, exponent: ExprOperable):
        self.base = SymbolicOperator.to_expr(base)
        self.exp = SymbolicOperator.to_expr(exponent)

    # ------------- Printable -------------
    def _repr_latex_(self) -> str:
        return f"$\\left({self.base}\\right)^{{{self.exp}}}$"
    def __str__(self) -> str:
        return f"({self.base})^({self.exp})"

    # ------------- Algebraic helpers -------------
    def is_zero(self) -> bool:
        return self.base.is_zero() and not self.exp.is_zero()
    def is_identity(self) -> bool:
        return self.exp.is_zero() or self.base.is_identity()
    def neg(self) -> Pow:
        return Pow(self.base.neg(), self.exp)
    def inv(self) -> Pow:
        # La inversa de x^n es 1/(x^n)
        return Pow(self.base, self.exp.neg())

    def to_expression(self) -> Expression:
        # Aquí podría ir una implementación más sofisticada para convertir
        # la potencia en una expresión si se necesitan simplificaciones
        return Expression([self])

    def simplify(self) -> Union[Expression, Pow]:
        # Simplificar la potencia:
        # Si la base es 0 y el exponente no es 0, la respuesta es 0
        if self.base.is_zero() and not self.exp.is_zero():
            return Expression([_Term(0)])

        # Si el exponente es 0, la expresión es igual a 1
        if self.exp.is_zero():
            return Expression([_Term(1)])

        # Si la base es 1, la expresión es igual a 1
        if self.base.is_identity():
            return Expression([_Term(1)])

        # Si la base es negativa y el exponente es fraccionario, tendríamos que manejar casos
        # complejos, pero por simplicidad, no implementamos eso aquí.
        
        # En cualquier otro caso, no se puede simplificar más
        return self

class SymbolicOperator:
    """
    Clase de métodos estáticos (tipo "helper")
    para realizar las operaciones aritméticas
    en el sistema simbólico.
    """
    @classmethod
    def to_expr(cls, obj: ExprOperable) -> Expression:
        """
        Convierte cualquier tipo T_Expressable en Expression.
        """
        if isinstance(obj, Basic):
            return obj.to_expression()
        elif isinstance(obj, (int, float, complex)): # type: ignore
            return Expression([_Term(obj)])
        elif isinstance(obj, Number): # type: ignore
            return Expression([_Term(obj)])
        
        raise TypeError(f"No se pudo convertir {obj} a Expression.")

    # ----------------------------------------------------------------
    #                         S U M A
    # ----------------------------------------------------------------
    @classmethod
    def add(cls, a: ExprOperable, b: ExprOperable) -> Expression:
        """
        a + b => sumamos los términos de Expression(a) y Expression(b).
        """        
        expr_a = cls.to_expr(a)
        expr_b = cls.to_expr(b)
        return Expression(expr_a.terms + expr_b.terms).simplify()

    @classmethod
    def sub(cls, a: ExprOperable, b: ExprOperable) -> "Expression":
        """
        a - b => a + (-b)
        """
        expr_a = cls.to_expr(a).simplify()
        expr_b = cls.to_expr(b).simplify()
        return Expression(expr_a.terms + [t.neg() for t in expr_b.terms]).simplify()

    # ----------------------------------------------------------------
    #                   M U L T I P L I C A C I O N
    # ----------------------------------------------------------------
    @classmethod 
    def mul(cls, a: ExprOperable, b: ExprOperable) -> Expression:
        """
        a * b => producto cartesiano de los términos de expr_a y expr_b
        => new Expression => simplify.
        Optimiza multiplicaciones con números complejos.
        """
        expr_a = cls.to_expr(a).simplify()
        expr_b = cls.to_expr(b).simplify()

        # Handle multiplication by pure numeric terms more efficiently
        if len(expr_a.terms) == 1 and not expr_a.terms[0].sym_dict:
            return Expression(_Term(expr_a.terms[0].coeff * t.coeff, t.sym_dict) 
                            for t in expr_b.terms).simplify()
        elif len(expr_b.terms) == 1 and not expr_b.terms[0].sym_dict:
            return Expression(_Term(t.coeff * expr_b.terms[0].coeff, t.sym_dict) 
                            for t in expr_a.terms).simplify()

        return Expression(t1*t2 for t2 in expr_b.terms 
                        for t1 in expr_a.terms).simplify()

    # ----------------------------------------------------------------
    #                       D I V I S I O N
    # ----------------------------------------------------------------
    @classmethod
    def div(cls, a: ExprOperable, b: ExprOperable) -> Expression:
        """
        a / b => producto cartesiano de los términos de expr_a
        con 1/(cada término de expr_b).
        Simplifica divisiones de números complejos cuando es posible.
        """
        expr_a = cls.to_expr(a).simplify()
        expr_b = cls.to_expr(b).simplify()
        
        # Handle division by pure numeric terms more efficiently
        if len(expr_b.terms) == 1 and not expr_b.terms[0].sym_dict:
            b_coeff = expr_b.terms[0].coeff
            if b_coeff.is_zero():
                raise ZeroDivisionError("División por expresión cero")
            
            # Divide each term by the numeric coefficient
            return Expression(_Term(t.coeff / b_coeff, t.sym_dict) 
                            for t in expr_a.terms).simplify()
        
        if expr_b.is_zero():
            raise ZeroDivisionError("División por expresión cero")
            
        return Expression(t1/t2 for t2 in expr_b.terms 
                        for t1 in expr_a.terms).simplify()

    # ----------------------------------------------------------------
    #                       P O T E N C I A
    # ----------------------------------------------------------------
    @classmethod
    def pow(cls, base: ExprOperable, exp: ExprOperable) -> Union[Expression, Pow]:
        """
        base^exp.
        - Si exp es un entero (ej. 2, 3, -1, etc.), podríamos
          hacer la expansión polinómica si base es 'Expression'.
        - Caso general => devolvemos un Coefficient(base, exp).
        """
        expr_base = cls.to_expr(base)
        expr_exp = cls.to_expr(exp)

        if len(expr_exp.terms) == 1:
            # único término
            t = expr_exp.terms[0]
            # si no tiene símbolos
            if not t.sym_dict:
                val = t.coeff.value
                if isinstance(val, int):
                    return cls._pow_by_integer(expr_base, val)
        # 2) Caso general => devolvemos Coefficient sin expandir
        return Pow(expr_base, expr_exp)

    @classmethod
    def _pow_by_integer(cls, base_expr: Expression, n: int) -> Expression:
        """
        Eleva 'base_expr' (Expression) a la potencia entera n.
        - Si n >= 0 => multiplicamos base_expr consigo mismo n veces.
        - Si n <  0 => 1 / (base_expr^(|n|)).
        """
        # Caso n=0 => 1
        if n == 0:
            return Expression([_Term(1)])  # => 1
        if n > 0:
            # repetimos multiplicación
            result = base_expr
            for _ in range(n - 1):
                result = cls.mul(result, base_expr)
            return result.simplify()
        else:
            # n < 0 => 1 / base_expr^(|n|)
            pos = abs(n)
            pos_power = cls._pow_by_integer(base_expr, pos)
            return cls.div(Expression(1), pos_power)
