from fractions import Fraction
from math import lcm, gcd
from typing import Union


NumberLike = Union[int, float, complex, Fraction]

class ComplexFraction:
    """
    num / den,  con:
        • num: complex con partes enteras (ℤ + ℤ·j)
        • den: int > 0

    Esto permite:
        • Acceder a .denominator  →  ENTERO
        • Reescalar por el MCM y obtener partes reales/imag enteras
    """
    _num: complex
    _den: int
    __slots__ = ("_num", "_den")

    # -----------------------------------------------------------------------
    def __init__(self, x: NumberLike):
        # -------------------- caso complejo --------------------------------
        if isinstance(x, complex):
            re = Fraction(x.real).limit_denominator()   # a / br
            im = Fraction(x.imag).limit_denominator()   # c / bi
            den = lcm(re.denominator, im.denominator)   # mcm(br, bi)

            re_num = re.numerator * (den // re.denominator)
            im_num = im.numerator * (den // im.denominator)

            self._num = complex(re_num, im_num)
            self._den = den

        # -------------------- caso real / racional -------------------------
        else:
            fr  = Fraction(x).limit_denominator()
            self._num = complex(fr.numerator, 0)
            self._den = fr.denominator

        # Simplificación gcd global
        re_i = int(self._num.real)
        im_i = int(self._num.imag)
        g    = gcd(abs(re_i), gcd(abs(im_i), self._den))
        if g > 1:
            self._num = complex(re_i // g, im_i // g)
            self._den //= g
        
        self._den = int(self._den)

    # ---------------------- API estilo Fraction ----------------------------
    @property
    def numerator(self):
        """Devuelve un complejo con partes enteras."""
        return self._num

    @property
    def denominator(self) -> int:
        """Entero positivo: ideal para un MCM global."""
        return self._den

    def limit_denominator(self, max_den:int=1_000_000):
        """Igual interfaz que Fraction; aquí ya solemos estar ‘limitados’."""
        if self._den <= max_den:
            return self
        # Re‑exprésalo con denominador ≤ max_den
        re = Fraction(int(self._num.real), self._den).limit_denominator(max_den)
        im = Fraction(int(self._num.imag), self._den).limit_denominator(max_den)
        return ComplexFraction(complex(re, im))

    # ---------------------- operadores mínimos -----------------------------
    def __rmul__(self, k: int):
        if isinstance(k, int): # type: ignore
            return ComplexFraction(complex(self._num.real * k,
                                           self._num.imag * k) / self._den)
        raise TypeError

    def __complex__(self):
        return self._num / self._den

    def __int__(self):
        """Sólo si la parte imaginaria es 0."""
        if self._num.imag:
            raise TypeError("No se puede convertir un número complejo a int")
        return int(self._num.real // self._den)

    def __repr__(self):
        return f"ComplexFraction({self._num}/{self._den})"
