import re
from typing import List, Optional, Tuple

from ..units.fundamental_unit import FundamentalUnit, UNIT_ORDER
from ..units import UnitDict, UnitAliasManager
from .helpers import to_superscript

class UnitTextFormater:
    """
    Utility class to print units in plain Python or LaTeX formats.

    - Provides `py_str` for console-friendly output with Unicode superscript.
    - Provides `latex_str` for LaTeX-ready representations.
    - Respects registered aliases via UnitAliasManager before falling back to individual units.
    """

    @classmethod
    def lookup_alias(cls, units: UnitDict) -> Optional[str]:
        """
        If a known alias exists for this combination of fundamental units, return it.
        """
        unit_set = frozenset(
            (unit, power)
            for unit, power in units.items()
            if unit != FundamentalUnit.ONE and power != 0
        )
        return UnitAliasManager.get_alias(unit_set)

    @classmethod
    def _sort_units(cls, units: UnitDict) -> List[Tuple[FundamentalUnit, float]]:
        """
        Order units by a predefined order and drop any with zero exponent.
        Special-case: if both DISTANCE and ANGLE present, drop ANGLE.
        """
        cleaned = {u: p for u, p in units.items() if p != 0}
        if FundamentalUnit.DISTANCE in cleaned and FundamentalUnit.ANGLE in cleaned:
            cleaned[FundamentalUnit.ANGLE] = 0
            cleaned = {u: p for u, p in cleaned.items() if p != 0}
        return sorted(
            cleaned.items(),
            key=lambda up: UNIT_ORDER.index(up[0]) if up[0] in UNIT_ORDER else float('inf')
        )

    @classmethod
    def py_str(cls, units: UnitDict) -> str:
        """
        Return a human-readable plain string, using Unicode superscripts.
        E.g. kg·m²·s⁻¹
        """
        if alias := cls.lookup_alias(units):
            return alias
        parts: List[str] = []
        for unit, power in cls._sort_units(units):
            if power == 1:
                parts.append(unit.value)
            else:
                exp = int(power) if float(power).is_integer() else power
                parts.append(f"{unit.value}{to_superscript(exp)}")
        return "·".join(parts) if parts else ""

    @classmethod
    def latex_str(cls, units: UnitDict) -> str:
        """
        Return a LaTeX-formatted string of units, e.g. \\text{kg} \\cdot \\text{m}^{2} / \\text{s}
        """
        if alias := cls.lookup_alias(units):
            return cls._from_alias(alias)
        parts = [cls._unit_to_latex(u, p) for u, p in cls._sort_units(units)]
        return " \\cdot ".join(parts) if parts else ""

    @classmethod
    def _from_alias(cls, alias: str) -> str:
        """
        Convert an alias string (e.g. 'kg/m**2') into LaTeX tokens.
        """
        normalized = re.sub(r"\*\*", "^", alias)
        num_str, denom_str = normalized.split('/', 1) if '/' in normalized else (normalized, None)
        num = cls._join_parts(num_str)
        if denom_str:
            denom = cls._join_parts(denom_str)
            return f"{num} / {denom}"
        return num

    @classmethod
    def _join_parts(cls, text: str) -> str:
        """
        Split on separators (·, *, whitespace) and format each token.
        """
        tokens = [t for t in re.split(r"[·*\s]+", text) if t]
        return " \\cdot ".join(cls._format_token(t) for t in tokens)

    @staticmethod
    def _format_token(tok: str) -> str:
        """
        Wrap base in \text{·} and exponentiate if '^' present.
        """
        if '^' in tok:
            base, exp = tok.split('^', 1)
            return f"\\text{{{base}}}^{{{exp}}}"
        return f"\\text{{{tok}}}"

    @classmethod
    def _unit_to_latex(cls, unit: FundamentalUnit, power: float) -> str:
        """
        Format a single unit and exponent for LaTeX.
        """
        if power == 1:
            return f"\\text{{{unit.value}}}"
        exp = int(power) if float(power).is_integer() else power
        return f"\\text{{{unit.value}}}^{{{exp}}}"
