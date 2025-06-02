from typing import Optional, overload
from ..linalg import Scalar, ScalarLike
from ..quantity import ScalarQuantity
import math
import cmath

def _is_complex(x) -> bool:
    return isinstance(x, complex) or (
        isinstance(x, Scalar) and isinstance(x.value, complex)
    ) or (
        isinstance(x, ScalarQuantity) and isinstance(x.value.value, complex)
    )

# --- TRIGONOMETRICAS ---

@overload
def sin(x: ScalarLike) -> ScalarLike: ...
@overload
def sin(x: Scalar) -> Scalar: ...
@overload
def sin(x: ScalarQuantity) -> ScalarQuantity: ...

def sin(x):
    func = cmath.sin if _is_complex(x) else math.sin
    if isinstance(x, ScalarLike):
        return func(x)
    if isinstance(x, Scalar):
        return Scalar(func(x.value))
    if isinstance(x, ScalarQuantity):
        if x.units.is_one():
            return ScalarQuantity(func(x.value.value), x.units)
        raise ValueError("sin() solo se puede aplicar a cantidades adimensionales")

@overload
def cos(x: ScalarLike) -> ScalarLike: ...
@overload
def cos(x: Scalar) -> Scalar: ...
@overload
def cos(x: ScalarQuantity) -> ScalarQuantity: ...

def cos(x):
    func = cmath.cos if _is_complex(x) else math.cos
    if isinstance(x, ScalarLike):
        return func(x)
    if isinstance(x, Scalar):
        return Scalar(func(x.value))
    if isinstance(x, ScalarQuantity):
        if x.units.is_one():
            return ScalarQuantity(func(x.value.value), x.units)
        raise ValueError("cos() solo se puede aplicar a cantidades adimensionales")

@overload
def tan(x: ScalarLike) -> ScalarLike: ...
@overload
def tan(x: Scalar) -> Scalar: ...
@overload
def tan(x: ScalarQuantity) -> ScalarQuantity: ...

def tan(x):
    func = cmath.tan if _is_complex(x) else math.tan
    if isinstance(x, ScalarLike):
        return func(x)
    if isinstance(x, Scalar):
        return Scalar(func(x.value))
    if isinstance(x, ScalarQuantity):
        if x.units.is_one():
            return ScalarQuantity(func(x.value.value), x.units)
        raise ValueError("tan() solo se puede aplicar a cantidades adimensionales")

@overload
def asin(x: ScalarLike) -> ScalarLike: ...
@overload
def asin(x: Scalar) -> Scalar: ...
@overload
def asin(x: ScalarQuantity) -> ScalarQuantity: ...

def asin(x):
    func = cmath.asin if _is_complex(x) else math.asin
    if isinstance(x, ScalarLike):
        return func(x)
    if isinstance(x, Scalar):
        return Scalar(func(x.value))
    if isinstance(x, ScalarQuantity):
        if x.units.is_one():
            return ScalarQuantity(func(x.value.value), unit='rad')
        raise ValueError("asin() solo se puede aplicar a cantidades adimensionales")

@overload
def acos(x: ScalarLike) -> ScalarLike: ...
@overload
def acos(x: Scalar) -> Scalar: ...
@overload
def acos(x: ScalarQuantity) -> ScalarQuantity: ...

def acos(x):
    func = cmath.acos if _is_complex(x) else math.acos
    if isinstance(x, ScalarLike):
        return func(x)
    if isinstance(x, Scalar):
        return Scalar(func(x.value))
    if isinstance(x, ScalarQuantity):
        if x.units.is_one():
            return ScalarQuantity(func(x.value.value),  unit='rad')
        raise ValueError("acos() solo se puede aplicar a cantidades adimensionales")

@overload
def atan(x: ScalarLike) -> ScalarLike: ...
@overload
def atan(x: Scalar) -> Scalar: ...
@overload
def atan(x: ScalarQuantity) -> ScalarQuantity: ...

def atan(x):
    func = cmath.atan if _is_complex(x) else math.atan
    if isinstance(x, ScalarLike):
        return func(x)
    if isinstance(x, Scalar):
        return Scalar(func(x.value))
    if isinstance(x, ScalarQuantity):
        if x.units.is_one():
            return ScalarQuantity(func(x.value.value), unit='rad')
        raise ValueError("atan() solo se puede aplicar a cantidades adimensionales")

# --- FUNCIONES LOGARÍTMICAS Y EXPONENCIALES ---

@overload
def sqrt(x: ScalarLike) -> ScalarLike: ...
@overload
def sqrt(x: Scalar) -> Scalar: ...
@overload
def sqrt(x: ScalarQuantity) -> ScalarQuantity: ...

def sqrt(x):
    func: function = cmath.sqrt if _is_complex(x) else math.sqrt
    if isinstance(x, ScalarLike):
        return func(x)
    if isinstance(x, Scalar):
        return Scalar(func(x.value))
    if isinstance(x, ScalarQuantity):
        return ScalarQuantity(func(x.value.value), x.units ** 0.5)



@overload
def log(x: ScalarLike, *, base: Optional[ScalarLike] = None) -> ScalarLike: ...
@overload
def log(x: Scalar, *, base: Optional[ScalarLike] = None) -> Scalar: ...
@overload
def log(x: ScalarQuantity, *, base: Optional[ScalarLike] = None) -> ScalarQuantity: ...

def log(x, *, base: Optional[ScalarLike] = None):
    func = cmath.log if _is_complex(x) else math.log
    def apply_log(value: ScalarLike):
        return func(value) if base is None else func(value, base)

    if isinstance(x, ScalarLike):
        return apply_log(x)
    if isinstance(x, Scalar):
        return Scalar(apply_log(x.value))
    if isinstance(x, ScalarQuantity):
        if not x.units.is_one():
            raise ValueError("log() solo se puede aplicar a cantidades adimensionales")
        return ScalarQuantity(apply_log(x.value.value), x.units)
    raise TypeError(f"log() no está definido para tipo {type(x)}")

@overload
def log10(x: ScalarLike) -> ScalarLike: ...
@overload
def log10(x: Scalar) -> Scalar: ...
@overload
def log10(x: ScalarQuantity) -> ScalarQuantity: ...

def log10(x):
    func = cmath.log10 if _is_complex(x) else math.log10
    if isinstance(x, ScalarLike):
        return func(x)
    if isinstance(x, Scalar):
        return Scalar(func(x.value))
    if isinstance(x, ScalarQuantity):
        if x.units.is_one():
            return ScalarQuantity(func(x.value.value), x.units)
        raise ValueError("log10() solo se puede aplicar a cantidades adimensionales")

@overload
def exp(x: ScalarLike) -> ScalarLike: ...
@overload
def exp(x: Scalar) -> Scalar: ...
@overload
def exp(x: ScalarQuantity) -> ScalarQuantity: ...

def exp(x):
    func = cmath.exp if _is_complex(x) else math.exp
    if isinstance(x, ScalarLike):
        return func(x)
    if isinstance(x, Scalar):
        return Scalar(func(x.value))
    if isinstance(x, ScalarQuantity):
        if x.units.is_one():
            return ScalarQuantity(func(x.value.value), x.units)
        raise ValueError("exp() solo se puede aplicar a cantidades adimensionales")
