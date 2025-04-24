"""
Módulo parser para unidades.

Provee la conversión de cadenas de texto en objetos de unidades a través de prefijos SI y unidades personalizadas.
"""

from typing import Optional, Dict, Any, Callable, Union

from .fundamental_unit import FundamentalUnit
from .basic_typing import UnitDict, RealLike
from .prefixed_unit import PrefixedUnit
from .alias_manager import UnitAliasManager




# Diccionario de prefijos SI (clave: prefijo, valor: factor numérico)
PREFIXES_MAP: Dict[str, float] = {
    "Y": 1e24,
    "Z": 1e21,
    "E": 1e18,
    "P": 1e15,
    "T": 1e12,
    "G": 1e9,
    "M": 1e6,  # Mega
    "k": 1e3,
    "h": 1e2,
    "da": 1e1,
    "d": 1e-1,
    "c": 1e-2,
    "m": 1e-3,
    "µ": 1e-6,
    "u": 1e-6,  # Alternativa para micro
    "n": 1e-9,
    "p": 1e-12,
    "f": 1e-15,
    "a": 1e-18,
    "z": 1e-21,
    "y": 1e-24,
}

from math import pi

CUSTOM_UNITS: Dict[str, PrefixedUnit] = {
    "ºC":   PrefixedUnit(1,         {FundamentalUnit.TEMPERATURE: 1}),  # Celsius
    "ºF":   PrefixedUnit(1,         {FundamentalUnit.TEMPERATURE: 1}),  # Fahrenheit
    "day":  PrefixedUnit(86400,     {FundamentalUnit.TIME: 1}),
    "week": PrefixedUnit(604800,    {FundamentalUnit.TIME: 1}),
    "month":PrefixedUnit(2629800,   {FundamentalUnit.TIME: 1}),
    "year": PrefixedUnit(31557600,  {FundamentalUnit.TIME: 1}), 
    "h":    PrefixedUnit(3600,      {FundamentalUnit.TIME: 1}),
    "min":  PrefixedUnit(60,        {FundamentalUnit.TIME: 1}),
    "º":    PrefixedUnit(pi/180,    {FundamentalUnit.ANGLE: 1}),
    "g":    PrefixedUnit(1e-3,      {FundamentalUnit.MASS: 1}),
    "ton":  PrefixedUnit(1e3,       {FundamentalUnit.MASS: 1}),
    "L":    PrefixedUnit(0.001,     {FundamentalUnit.DISTANCE: 3}),
    
    "atm":  PrefixedUnit(101325,          UnitAliasManager.get_units_dict('Pa')),
    "bar":  PrefixedUnit(1e5,             UnitAliasManager.get_units_dict('Pa')), 
    "eV":   PrefixedUnit(1.60217662e-19,  UnitAliasManager.get_units_dict('J')),
    "cal": PrefixedUnit(4.18,             UnitAliasManager.get_units_dict('J'))
}

applications = ['sqrt', 'log', 'exp', 'sin', 'cos']

def function_tokenizer(ident: str) -> Union['UnitToken', None]:
    for app in applications:
        if ident.lower() == app:
                return UnitToken(UnitToken.OP, app)
    return None
    
class UnitParseError(Exception):
    """Excepción para errores en el parsing de unidades."""
    pass

class UnitToken:
    NUMBER = "NUMBER"
    IDENT = "IDENT"      # Identificador (unidad o alias)
    OP = "OP"            # Operador: *, /, **, sqrt, +, -
    LPAREN = "LPAREN"    # (
    RPAREN = "RPAREN"    # )
    LBRACK = "LBRACK"    # [
    RBRACK = "RBRACK"    # ]
    END = "END"          # Fin de la cadena

    def __init__(self, type_: str, value: Optional[str] = None) -> None:
        self.type: str = type_
        self.value: Optional[str] = value

    def __repr__(self) -> str:
        return f"UnitToken({self.type}, {self.value})"

class UnitLexer:
    def __init__(self, text: str) -> None:
        # Eliminamos espacios para simplificar el lexer
        self.text: str = text.replace(" ", "")
        self.pos: int = 0
        self.length: int = len(self.text)

    def next_token(self) -> UnitToken:
        if self.pos >= self.length:
            return UnitToken(UnitToken.END)
        ch: str = self.text[self.pos]
        # Números (coeficientes o exponentes)
        if ch.isdigit() or ch == '.':
            num_str: str = ""
            while self.pos < self.length and (self.text[self.pos].isdigit() or self.text[self.pos] == '.'):
                num_str += self.text[self.pos]
                self.pos += 1
            return UnitToken(UnitToken.NUMBER, num_str)
        # Identificadores: secuencia de letras (unidad o alias)
        if ch.isalpha():
            ident: str = ""
            while self.pos < self.length and self.text[self.pos].isalpha():
                ident += self.text[self.pos]
                self.pos += 1
            if rv := function_tokenizer(ident):
                return rv
            return UnitToken(UnitToken.IDENT, ident)
        # Operadores: se reconoce ** como operador especial
        if ch == '*':
            self.pos += 1
            if self.pos < self.length and self.text[self.pos] == '*':
                self.pos += 1
                return UnitToken(UnitToken.OP, '**')
            return UnitToken(UnitToken.OP, '*')
        if ch == '/':
            self.pos += 1
            return UnitToken(UnitToken.OP, '/')
        # Paréntesis y corchetes
        if ch == '(':
            self.pos += 1
            return UnitToken(UnitToken.LPAREN, '(')
        if ch == ')':
            self.pos += 1
            return UnitToken(UnitToken.RPAREN, ')')
        if ch == '[':
            self.pos += 1
            return UnitToken(UnitToken.LBRACK, '[')
        if ch == ']':
            self.pos += 1
            return UnitToken(UnitToken.RBRACK, ']')
        # Operadores '+' o '-' (por ejemplo, para exponentes)
        if ch in "+-":
            self.pos += 1
            return UnitToken(UnitToken.OP, ch)
        raise UnitParseError(f"Carácter inesperado '{ch}' en la posición {self.pos}.")



def resolve_prefixed_identifier(ident: str, mapping: Dict[str, Any]) -> Optional[PrefixedUnit]:
    """
    Intenta separar un prefijo en el identificador y resolver la unidad correspondiente en 'mapping'.
    Retorna una PrefixedUnit si tiene éxito, o None en caso contrario.
    
    Ejemplo:
        Si ident es 'km' y mapping contiene {'m': FundamentalUnits.M}, retorna PrefixedUnit(1e3, {FundamentalUnits.M: 1})
    """
    for prefix in sorted(PREFIXES_MAP.keys(), key=lambda x: -len(x)):
        if prefix and ident.startswith(prefix):
            remainder = ident[len(prefix):]
            if remainder in mapping:
                return PrefixedUnit(PREFIXES_MAP[prefix], {mapping[remainder]: 1})
            if remainder in CUSTOM_UNITS:
                custom_unit = CUSTOM_UNITS[remainder]
                return PrefixedUnit(PREFIXES_MAP[prefix] * custom_unit.prefix, custom_unit.unit_dict)
    return None

class UnitParser:
    """
    Parser para interpretar expresiones de unidades con soporte para prefijos.
    
    Gramática:
        expr     = term { ('*' | '/') term }
        term     = factor [ '**' exponent ]
        factor   = IDENT | group | NUMBER
        group    = '(' expr ')' | '[' expr ']'
        exponent = [ '+' | '-' ] NUMBER
    
    Ejemplo:
        "ug * km/(ms**2)" se parsea a una instancia de PrefixedUnit que representa la composición
        correspondiente a microgramos * kilómetros / (milisegundos^2).
    """
    def __init__(self, text: str, mapping: Dict[str, Any],
                 alias_resolver: Callable[[str], PrefixedUnit]) -> None:
        self.lexer = UnitLexer(text)
        self.current_token: UnitToken = self.lexer.next_token()
        self.mapping: Dict[str, Any] = mapping  # Ejemplo: {'m': FundamentalUnits.M, ...}
        self.alias_resolver: Callable[[str], PrefixedUnit] = alias_resolver

    def eat(self, token_type: str, value: Optional[str] = None) -> None:
        if self.current_token.type == token_type and (value is None or self.current_token.value == value):
            self.current_token = self.lexer.next_token()
        else:
            raise UnitParseError(f"Se esperaba token {token_type} {value} pero se encontró {self.current_token}")

    def parse(self) -> PrefixedUnit:
        result = self.expr()
        if self.current_token.type != UnitToken.END:
            raise UnitParseError("No se terminó de parsear la expresión.")
        return result

    def expr(self) -> PrefixedUnit:
        term_unit = self.term()  # Llamada única para obtener el primer término
        mult, comp = term_unit.prefix, term_unit.unit_dict
        while self.current_token.type == UnitToken.OP and self.current_token.value in ['*', '/']:
            op = self.current_token.value
            self.eat(UnitToken.OP)
            next_term = self.term()
            if op == '*':
                mult *= next_term.prefix
                comp: UnitDict = self.merge(comp, next_term.unit_dict, factor=1)
            elif op == '/':
                mult /= next_term.prefix
                comp = self.merge(comp, next_term.unit_dict, factor=-1)
        return PrefixedUnit(mult, comp)

    def term(self) -> PrefixedUnit:
        factor_unit = self.factor()  # Llamada única para obtener el factor
        mult, comp = factor_unit.prefix, factor_unit.unit_dict
        if self.current_token.type == UnitToken.OP and self.current_token.value == '**':
            self.eat(UnitToken.OP, '**')
            exp = self.exponent()
            mult = mult ** exp
            comp = {unit: power * exp for unit, power in comp.items()}
        return PrefixedUnit(mult, comp)

    def factor(self) -> PrefixedUnit:
        if self.current_token.type == UnitToken.LPAREN:
            self.eat(UnitToken.LPAREN)
            result = self.expr()
            self.eat(UnitToken.RPAREN)
            return result
        elif self.current_token.type == UnitToken.LBRACK:
            self.eat(UnitToken.LBRACK)
            result = self.expr()
            self.eat(UnitToken.RBRACK)
            return result
        elif self.current_token.type == UnitToken.IDENT:
            ident = self.current_token.value
            if isinstance(ident, type(None)):
                raise ValueError
            self.eat(UnitToken.IDENT)
            # Primero se verifica en CUSTOM_UNITS
            if ident in CUSTOM_UNITS:
                return CUSTOM_UNITS[ident]
            # Se intenta resolver el identificador con prefijo en el mapping
            resolved = resolve_prefixed_identifier(ident, self.mapping)
            if resolved is not None:
                return resolved
            # Si no se resolvió, se busca directamente en el mapping
            if ident in self.mapping:
                return PrefixedUnit(1.0, {self.mapping[ident]: 1})
            # Si aún no se encuentra, se intenta resolver como alias
            return self.alias_resolver(ident)
        elif self.current_token.type == UnitToken.NUMBER:
            # Los números solos se interpretan como coeficientes sin unidades
            num_str = self.current_token.value
            if not num_str:
                raise ValueError
            self.eat(UnitToken.NUMBER)
            try:
                return PrefixedUnit(float(num_str), {})
            except Exception:
                raise UnitParseError("Número inválido.")
        raise UnitParseError(f"Token inesperado {self.current_token}")

    def exponent(self) -> RealLike:
        sign = 1
        if self.current_token.type == UnitToken.OP and self.current_token.value in ['+', '-']:
            if self.current_token.value == '-':
                sign = -1
            self.eat(UnitToken.OP)
        if self.current_token.type != UnitToken.NUMBER:
            raise UnitParseError("Se esperaba un número para el exponente.")
        exp_str = self.current_token.value
        self.eat(UnitToken.NUMBER)
        try:
            if isinstance(exp_str, str):
                exp = float(exp_str) if '.' in exp_str else float(exp_str)
                return sign * exp
        except Exception:
            raise UnitParseError("Exponente inválido.")
        return 1
        

    @staticmethod
    def merge(dict1: UnitDict, dict2: UnitDict, factor: int = 1) -> UnitDict:
        """Combina dos composiciones, sumando exponentes (multiplicando los de dict2 por factor)."""
        result = dict(dict1)
        for key, exp in dict2.items():
            result[key] = result.get(key, 0) + exp * factor
        return result

def alias_resolver(alias: str) -> PrefixedUnit:
    """
    Resuelve un alias a su correspondiente PrefixedUnit.
    Busca en UnitAliasManager y considera la posibilidad de un prefijo en el alias.
    
    Ejemplo:
        Si alias es "km" y 'm' está en el mapping de FundamentalUnits, retorna PrefixedUnit(1e3, {FundamentalUnits.M: 1})
    """
    from .unit_composition import UnitComposition
    # Intentar extraer un prefijo en el alias
    for prefix in sorted(PREFIXES_MAP.keys(), key=lambda x: -len(x)):
        if alias.startswith(prefix):
            remainder = alias[len(prefix):]
            for key, alias_list in UnitAliasManager.aliases().items():
                if remainder in alias_list:
                    return PrefixedUnit(PREFIXES_MAP[prefix], UnitComposition(dict(key)))
    # Si no se encontró prefijo, buscar el alias completo
    for key, alias_list in UnitAliasManager.aliases().items():
        if alias in alias_list:
            return PrefixedUnit(1.0, UnitComposition(dict(key)))
    raise UnitParseError(f"Alias de unidad '{alias}' no encontrado.")

if __name__ == '__main__':
    # Ejemplo de uso del parser
    from .unit_composition import FundamentalUnit

    # Ejemplo: "C**2 * s**4 * kg **-1 * m ** -3"
    text = "C**2 * s**4 * kg **-1 * m ** -3"
    mapping = {unit.value: unit for unit in FundamentalUnit}
    parser = UnitParser(text, mapping, alias_resolver)
    result = parser.parse()
    print(result)
