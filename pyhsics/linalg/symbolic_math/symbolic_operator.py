from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List, Union, Optional, TYPE_CHECKING
from numbers import Real as PyReal, Complex as PyComplex
from IPython.display import display, Latex  # type: ignore

if TYPE_CHECKING:
    # Se asume que estas clases están implementadas en sus módulos respectivos.
    from .expression import Expression
    from .term import Term
    from .symbol import Symbol

# Se asume que en el módulo algebraic_core se define la interfaz básica para objetos algebraicos.
from ...linalg import Algebraic, ScalarLike

# --- Tipo que agrupa los objetos "expresables" ---
T_Expressable = Union[
    "Symbol",
    "Term",
    "Expression",
    "Pow",            # Más adelante se define Pow
    Algebraic[Any],
    ScalarLike,
    PyReal,
    PyComplex
]





class SymPrintable(ABC):    
    @abstractmethod
    def __str__(self) -> str:
        pass
    
    @abstractmethod
    def _repr_latex_(self, name: Optional[str] = None) -> str:
        pass
    
    def latex(self):
        return self._repr_latex_().replace('$', '')
    
    def __repr__(self) -> str:
        try:
            get_ipython() # type: ignore
            self.display_latex()
            return ''

        except NameError:
            return f'{self.__class__.__name__}({str(self)})'
    
    def display_latex(self, name: Optional[str] = None) -> None:
        display(Latex(self._repr_latex_()))


class SymbolicOperator:
    """
    Clase de métodos estáticos (tipo "helper")
    para realizar las operaciones aritméticas
    en el sistema simbólico.
    """

    @classmethod
    def to_expr(cls, obj: T_Expressable) -> "Expression":
        """
        Convierte cualquier tipo T_Expressable en Expression.
        """
        from .expression import Expression
        from .term import Term
        from .symbol import Symbol
        from ..scalar import Scalar  # asumiendo que es la clase para escalares

        # 1) Si es int/float => pásalo a Scalar => Term => Expression
        if isinstance(obj, ScalarLike):
            # convirte a Scalar
            scalar_obj = Scalar(obj)
            return Expression([Term(scalar_obj, {})])

        # 2) Si ya es un Scalar (o Algebraic) => Term => Expression
        #    (si "Algebraic" abarca Vector/Matrix, ten cuidado
        #     de si quieres tratarlos aquí)
        if isinstance(obj, Algebraic):
            # asumimos es "Algebraic" (o subclase) => meterlo en Term
            return Expression([Term(obj, {})])

        # 3) Si es un Symbol => Term => Expression
        if isinstance(obj, Symbol):
            # coef 1, symbols_exponents = {e: 1}
            from ..scalar import Scalar
            return Expression([Term(Scalar(1), {obj: 1})])

        # 4) Si es un Term => meterlo a Expression con 1 término
        if isinstance(obj, Term):
            return Expression([obj])

        # 5) Si es un Expression => ya está
        if isinstance(obj, Expression):
            return obj

        # 6) Si es un Coefficient (ej. base^exponente),
        #    lo metemos en un Term => Expression
        if isinstance(obj, Pow): # type: ignore
            return Expression([Term(obj, {})])

        raise TypeError(f"No se pudo convertir {obj} a Expression.")

    # ----------------------------------------------------------------
    #                         S U M A
    # ----------------------------------------------------------------
    @classmethod
    def add(cls, a: T_Expressable, b: T_Expressable) -> "Expression":
        """
        a + b => sumamos los términos de Expression(a) y Expression(b).
        """
        from .expression import Expression
        
        expr_a = cls.to_expr(a).simplify()
        expr_b = cls.to_expr(b).simplify()
        return Expression(expr_a.terms + expr_b.terms).simplify()

    @classmethod
    def sub(cls, a: T_Expressable, b: T_Expressable) -> "Expression":
        """
        a - b => a + (-b)
        """
        from .expression import Expression

        expr_a = cls.to_expr(a).simplify()
        expr_b = cls.to_expr(b).simplify()
        # negamos expr_b
        expr_b_neg = expr_b.__neg__()
        return Expression(expr_a.terms + expr_b_neg.terms).simplify()

    # ----------------------------------------------------------------
    #                   M U L T I P L I C A C I O N
    # ----------------------------------------------------------------
    @classmethod
    def mul(cls, a: T_Expressable, b: T_Expressable) -> "Expression":
        """
        a * b => producto cartesiano de los términos de expr_a y expr_b
        => new Expression => simplify.
        """
        from .expression import Expression
        
        expr_a = cls.to_expr(a).simplify()
        expr_b = cls.to_expr(b).simplify()

        new_terms: List[Term] = []
        for t1 in expr_a.terms:
            for t2 in expr_b.terms:
                # asumiendo t1.__mul__(t2) => Term
                new_terms.append(t1 * t2)

        return Expression(new_terms).simplify()

    # ----------------------------------------------------------------
    #                       D I V I S I O N
    # ----------------------------------------------------------------
    @classmethod
    def div(cls, a: T_Expressable, b: T_Expressable) -> "Expression":
        """
        a / b => producto cartesiano de los términos de expr_a
        con 1/(cada término de expr_b).
        
        Para la división de términos (Term.__truediv__) se puede:
          - Dividir coeficientes
          - Restar exponentes
        o, si no se puede, crear Coefficient/Expression sin simplificar mucho.
        """
        from .expression import Expression
        
        expr_a = cls.to_expr(a).simplify()
        expr_b = cls.to_expr(b).simplify()

        # Podríamos chequear si expr_b es zero => error
        # if expr_b.is_zero():
        #     raise ZeroDivisionError("División por expresión cero")

        new_terms: List[Term] = []
        for t1 in expr_a.terms:
            for t2 in expr_b.terms:
                # Supongamos t2 no es cero => t1 / t2 => Term
                # Necesitas Term.__truediv__(...) o algo similar
                div_term = t1 / t2  # asumiendo lo tienes implementado
                new_terms.append(div_term)

        return Expression(new_terms).simplify()

    # ----------------------------------------------------------------
    #                       P O T E N C I A
    # ----------------------------------------------------------------
    @classmethod
    def pow(cls, base: T_Expressable, exp: T_Expressable) -> Union["Expression", "Pow"]:
        """
        base^exp.
        - Si exp es un entero (ej. 2, 3, -1, etc.), podríamos
          hacer la expansión polinómica si base es 'Expression'.
        - Caso general => devolvemos un Coefficient(base, exp).
        """
        expr_base = cls.to_expr(base).simplify()
        expr_exp = cls.to_expr(exp).simplify()

        # 1) Chequeamos si expr_exp es un "entero" (p.ej. un Scalar con valor entero).
        if len(expr_exp.terms) == 1:
            # único término
            t = expr_exp.terms[0]
            # si no tiene símbolos y su coeficiente es, digamos, un Scalar entero
            if not t.symbols_exponents and hasattr(t.coefficient, "value"):
                val = t.coefficient.value  # p.ej. 2, 3, ...
                if isinstance(val, int):
                    # --> exponente entero
                    return cls._pow_by_integer(expr_base, val)
                # si era float => decidimos
                # si no => devolvemos Coefficient
        # 2) Caso general => devolvemos Coefficient sin expandir
        return Pow(expr_base, expr_exp)

    @classmethod
    def _pow_by_integer(cls, base_expr: "Expression", n: int) -> "Expression":
        """
        Eleva 'base_expr' (Expression) a la potencia entera n.
        - Si n >= 0 => multiplicamos base_expr consigo mismo n veces.
        - Si n <  0 => 1 / (base_expr^(|n|)).
        """
        from .expression import Expression
        from ..scalar import Scalar
        # Caso n=0 => 1
        if n == 0:
            return Expression([Term(Scalar(1), {})])  # => 1
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
            uno = Expression([Term(Scalar(1), {})])
            return cls.div(uno, pos_power)


class ExprOperable(ABC):
    def __add__(self, other: T_Expressable) -> Expression:
        return SymbolicOperator.add(self, other)
    
    def __mul__(self, other: T_Expressable) -> Expression:
        return SymbolicOperator.mul(self, other)
    
    def __sub__(self, other: T_Expressable) -> Expression:
        return SymbolicOperator.sub(self, other)
    
    def __radd__(self, other: T_Expressable) -> Expression:
        return SymbolicOperator.add(other, self)
    
    def __rmul__(self, other: T_Expressable) -> Expression:
        return SymbolicOperator.mul(other, self)
    
    def __rsub__(self, other: T_Expressable) -> Expression:
        return SymbolicOperator.sub(other, self) 
    
    def __pow__(self, other: T_Expressable) -> Union[Expression, Pow]:
        return SymbolicOperator.pow(self, other)
        


class Pow(ExprOperable, SymPrintable):
    """
    Clase que representa algo del estilo base^exponente.
    base y exponente pueden ser objetos Algebraic, Scalar, Expression, etc.
    """

    __slots__ = ("base", "exponent")

    def __init__(self, base: T_Expressable, exponent: Optional[T_Expressable]=None):
        """
        base: T_Expressable (Symbol, Expression, Scalar, etc.)
        exponent: T_Expressable (Symbol, Expression, Scalar, etc.)
                  Si es None, interpretamos exponent=1
        """
        if exponent is None:
            exponent = 1  # => base^1 = base

        # Convertimos a Expression, o lo que decidas, para uniformidad
        # (Podrías también guardarlo "tal cual", depende de tu diseño)
        self.base = SymbolicOperator.to_expr(base)       # Expression
        self.exponent = SymbolicOperator.to_expr(exponent)  # Expression

    def __str__(self) -> str:
        # Representación informal
        return f"({self.base})^({self.exponent})"

    def _repr_latex_(self, name: Optional[str] = None) -> str:
        return f"$\\left({self.base.latex()}\\right)^{{{self.exponent.latex()}}}$"

    @property
    def is_zero(self) -> bool:
        """
        Lógica: base^exponente es cero si base es cero y exponente>0,
        salvo caso exponente=0 (indeterminado), exponente<0 => inf...
        Tú decides cómo manejar estos bordes.
        """
        # Ejemplo super simple:
        # * Si self.base es Expression/Scalar con is_zero -> True
        # * Y exponent is_zero => base^0 = 1 => no es cero => False
        if self.exponent.is_zero():
            return False
        return self.base.is_zero()

    @property
    def is_identity(self) -> bool:
        """
        base^exponente = 1 si base=1 o exponente=0...
        """
        if self.exponent.is_zero():
            return True
        return self.base.is_identity()

    # -----------------------------------------
    #   Aritmética: +, -, *, /, etc.
    # -----------------------------------------
    def __add__(self, other: Union[Pow, Any]) -> Expression:
        """
        a^x + b^y, en general, NO se simplifica (salvo coincidencias).
        Así que devolvemos Expression que contiene 2 Términos
        (o delegamos en SymbolicOperator.add).
        """
        return SymbolicOperator.add(self, other)

    def __radd__(self, other: Any) -> Any:
        return SymbolicOperator.add(other, self)

    def __sub__(self, other: Any) -> Any:
        return SymbolicOperator.sub(self, other)

    def __rsub__(self, other: Any) -> Any:
        return SymbolicOperator.sub(other, self)

    def __mul__(self, other: Any) -> Any:
        """
        (a^x) * (b^y).
        Si a == b, => a^(x+y).
        Si no, devolvemos Expression con el producto sin simplificar
        (o delegamos a SymbolicOperator.mul).
        """

        # 1) Si other es Coefficient:
        if isinstance(other, Pow):
            # Ver si la base es la misma (dependiendo de cómo compares Expression).
            # Suponiendo que .base es "la misma" si .terms son idénticos:
            if self.base == other.base:
                # a^x * a^y => a^(x+y)
                new_exponent = SymbolicOperator.add(self.exponent, other.exponent)
                return Pow(self.base, new_exponent)
            else:
                # Distintas bases => devuelves Expression sin simplificar
                return SymbolicOperator.mul(self, other)
        else:
            # 2) Si other no es Coefficient => delega
            return SymbolicOperator.mul(self, other)

    def __rmul__(self, other: Any) -> Any:
        return SymbolicOperator.mul(other, self)

    def __truediv__(self, other: Any) -> Any:
        """
        (a^x) / (b^y).
        Si a == b => a^(x-y).
        Caso general => Expression.
        """
        if isinstance(other, Pow):
            if self.base == other.base:
                # a^x / a^y => a^(x-y)
                new_exponent = SymbolicOperator.sub(self.exponent, other.exponent)
                return Pow(self.base, new_exponent)
            else:
                # Distintas bases => sin simplificar
                return SymbolicOperator.div(self, other)
        else:
            return SymbolicOperator.div(self, other)

    def __rtruediv__(self, other: Any) -> Any:
        """
        other / (a^x).
        Si other es Coefficient con la misma base => a^(y-x).
        """
        if isinstance(other, Pow):
            if self.base == other.base:
                new_exponent = SymbolicOperator.sub(other.exponent, self.exponent)
                return Pow(self.base, new_exponent)
            else:
                return SymbolicOperator.div(other, self)
        else:
            return SymbolicOperator.div(other, self)

    # Opcionalmente podrías implementar __pow__ para (a^x)^k => a^(x*k), etc.
    def __pow__(self, other: Any) -> Any:
        """
        (a^x)^y => a^(x*y).
        Caso general => expression, etc.
        """
        # a^x ^ y => a^(x*y)
        new_exponent = SymbolicOperator.mul(self.exponent, other)
        return Pow(self.base, new_exponent)
