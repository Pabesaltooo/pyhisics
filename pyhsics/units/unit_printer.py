from dataclasses import dataclass
from typing import List, Optional, Tuple
from .fundamental_unit import FundamentalUnit, UNIT_ORDER  # Asumimos que tienes esto definido
from .alias_manager import UnitAliasManager  # Asumimos que tienes esto definido
from .basic_typing import UnitDict
import re

@dataclass
class UnitPrinter:
    @classmethod
    def lookup_alias(cls, units: UnitDict) -> Optional[str]:
        # Buscar alias en el UnitAliasManager
        unit_set = frozenset((unit, power) for unit, power in units.items() if unit != FundamentalUnit.ONE)
        alias = UnitAliasManager.get_alias(unit_set)
        if alias:
            return alias
        
    @classmethod
    def superindice(cls, numero: float) -> str:
        """Convierte un número en su representación de superíndice Unicode, incluyendo decimales."""
        # si el numero es 1.0 o -5.0 lo convierte a 1 o -5.
        superindices = str.maketrans("0123456789-.", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻·")  # Punto medio `·` para el punto decimal
        return str(numero).translate(superindices)

    @classmethod
    def _sort_units(cls, units: UnitDict) -> List[Tuple[FundamentalUnit, float]]:
        """Ordena las unidades y limpia las unidades con exponente 0."""
        cleaned_units = {unit: power for unit, power in units.items() if power != 0}
        
        # Si existe 'M' (distancia) y 'RAD' (ángulo), suprimimos la representación de ANGLE.
        if FundamentalUnit.DISTANCE in cleaned_units and FundamentalUnit.ANGLE in cleaned_units:
            cleaned_units[FundamentalUnit.ANGLE] = 0
            cleaned_units = {unit: power for unit, power in cleaned_units.items() if power != 0}
                
        # Ordenar las unidades según UNIT_ORDER
        sorted_units = sorted(
            cleaned_units.items(),
            key=lambda x: UNIT_ORDER.index(x[0]) if x[0] in UNIT_ORDER else 999
        )
        
        return sorted_units

    @classmethod
    def py_str(cls, units: UnitDict) -> str:
        """Devuelve una representación de la unidad en texto."""
        sorted_units = cls._sort_units(units)
        parts: List[str] = []
        
        alias = cls.lookup_alias(units)
        if alias:
            return alias
        
        for unit, power in sorted_units:
            if power == 1:
                parts.append(unit.value)
            else:
                power = int(power) if abs(power).is_integer() else power
                parts.append(f"{unit.value}{cls.superindice(power)}")
        
        return "·".join(parts) if parts else "1"


    @classmethod
    def latex_str(cls, units: "UnitDict") -> str:
        """Devuelve la representación en LaTeX de las unidades."""
        sorted_units = cls._sort_units(units)
        parts: List[str] = []

        alias = cls.lookup_alias(units)
        if alias:
            # Procesar alias como "kg / m^2" o "m^3"
            def latexify_alias(alias_str: str) -> str:
                # Separar numerador y denominador si existe "/"
                if '/' in alias_str:
                    num, denom = [s.strip() for s in alias_str.split('/', 1)]
                else:
                    num, denom = alias_str.strip(), None

                def latexify_part(part: str) -> str:
                    # Procesa "kg", "m^3", etc.
                    if '^' in part:
                        base, exp = [s.strip() for s in part.split('^', 1)]
                        return f"\\text{{{base}}}^{{{exp}}}"
                    else:
                        return f"\\text{{{part}}}"

                # Separadores posibles: ·, *, **
                # Reemplaza '**' por '^' para facilitar el parsing
                num = re.sub(r'\*\*', '^', num)
                if denom:
                    denom = re.sub(r'\*\*', '^', denom)

                # Divide por ·, *, o espacios
                split_pattern = r'[·*]'
                num_parts = [p.strip() for p in re.split(split_pattern, num) if p.strip()]
                num_latex = " \\cdot ".join([latexify_part(p) for p in num_parts])

                if denom:
                    denom_parts = [p.strip() for p in re.split(split_pattern, denom) if p.strip()]
                    denom_latex = " \\cdot ".join([latexify_part(p) for p in denom_parts])
                    return f"{num_latex} / {denom_latex}"
                else:
                    return num_latex

            return latexify_alias(alias)

        for unit, power in sorted_units:
            if power == 1:
                parts.append("\\text{" + unit.value + "}")
            else:
                power = int(power) if abs(power).is_integer() else power
                part = "\\text{" + unit.value + "}^{" + str(power) + "}"
                parts.append(part)  # Superíndice en LaTeX
        
        latex_units = " \\cdot ".join(parts) if parts else ""
        return latex_units.replace("·", " \\cdot ")  # Convertir el "·" a "\\cdot" en LaTeX
