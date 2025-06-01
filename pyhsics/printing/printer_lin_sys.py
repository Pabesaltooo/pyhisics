from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from dataclasses import dataclass


from pyhsics.printing.core import LINEAR_SYS_FORMATTING_MODES as MODES
from pyhsics.printing.core import BasicPrinter
from pyhsics.linalg.structures import Scalar, Vector
if TYPE_CHECKING:
    from pyhsics.linalg.solvers.linear_system import LinearSystem


class LinSysFormatter(BasicPrinter):
    """
    Printer for linear systems.
    """
    
    repr_mode: MODES = 'ANSW'
        
    def set_repr_mode(self, mode: MODES) -> None:
        """
        Cambia el modo de representación del sistema lineal.
        """
        if mode not in {'ANSW', 'LES', 'MAT-SYS', 'AUG-MAT', 'PARAM'}:
            raise ValueError(f"Modo de representación no válido: {mode}")
        self.repr_mode = mode
        
    
    def __call__(self, sys: LinearSystem, name: Optional[str] = None) -> str:
        mode_map = {
            'ANSW': self.as_solutions,
            'PARAM': self.parametric_solution,
            'LES': self.as_linear_equations,
            'MAT-SYS': self.as_matrix_system,
            'AUG-MAT': self.as_augmented_matrix,
        }
        try:
            body = mode_map[self.repr_mode](sys)
        except KeyError:
            raise ValueError(f"Modo de representación no válido: {self.repr_mode}")

        if name:
            return rf"${name} = {body}$"
        return f"${body}$"

    @staticmethod
    def _format_term(coef: 'Scalar', var_idx: int, first: bool) -> str:
        sign = '' if coef > 0 and first else ('-' if coef < 0 else '+')
        abs_coef = abs(coef)
        coef_str = '' if abs_coef == 1 else str(abs_coef.latex())
        return f"{sign}{coef_str}x_{{{var_idx}}}"

    @classmethod
    def as_augmented_matrix(cls, sys: LinearSystem) -> str:
        n, m = sys.shape
        cols = 'c' * m + '|c'
        rows: List[str] = []
        for i in range(n):
            coeffs = [Scalar(sys.value[i][j]).latex() for j in range(m)]
            coeffs.append(Scalar(sys.B[i]).latex())
            rows.append(' & '.join(coeffs))
        body = (
            r"\left(\begin{array}{" + cols + r"} " + 
            r" \\ ".join(rows) + 
            r" \end{array}\right)"
        )
        return body
    
    @classmethod
    def as_matrix_system(cls, sys: LinearSystem) -> str:
        m = sys.shape[1]
        vecX = r"\begin{pmatrix}" + r" \\ ".join(f"x_{{{j+1}}}" for j in range(m)) + r"\end{pmatrix}"
        return f"{sys.value.latex()} {vecX} = {sys.B.latex()}"


    @classmethod
    def as_linear_equations(cls, sys: LinearSystem) -> str:
        n, m = sys.shape
        lines: List[str] = []
        for i in range(n):
            terms: List[str] = []
            for j in range(m):
                coef = Scalar(sys.value[i][j])
                if coef == 0:
                    continue
                terms.append(cls._format_term(coef, j + 1, first=not terms))
            lhs = '0' if not terms else ' '.join(terms)
            rhs = Scalar(sys.B[i]).latex()
            lines.append(f"& {lhs} & = & {rhs}")
        return r"\begin{aligned}" + r" \\ ".join(lines) + r"\end{aligned}"
    
    @classmethod
    def as_solutions(cls, sys: LinearSystem) -> str:
        sol = sys.solve()
        if isinstance(sol, Vector):
            lines = [f"x_{{{i+1}}} = {Scalar(val).latex()}" for i, val in enumerate(sol)]
            return r"\begin{cases}" + r" \\ ".join(lines) + r"\end{cases}"

        if isinstance(sol, list):
            return cls.parametric_solution(sys)

        return r"\emptyset"
    
    @classmethod
    def parametric_solution(cls, sys: LinearSystem) -> str:
        A = sys.value
        B = sys.B
        aug = A.hstack(B)
        rref_mat = aug.reduced_row_echelon_form()
        _, m = A.shape
        eqs: List[str] = []

        for row in rref_mat.value:
            coefs, const = row[:-1], row[-1]
            if not any(c != 0 for c in coefs) and const == 0:
                continue
            terms: List[str] = []
            for j, c in enumerate(coefs):
                scalar_c = Scalar(c)
                if scalar_c == 0:
                    continue
                terms.append(cls._format_term(scalar_c, j+1, first=not terms))
            rhs = Scalar(const).latex()
            eqs.append(f"{' '.join(terms)} = {rhs}")

        if not eqs:
            return rf"\mathbb{{R}}^{{{m}}}"

        vars_tex = r" \\ ".join(f"x_{{{i+1}}}" for i in range(m))
        eqs_tex = r" \\ ".join(eqs)

        return (
            r"\displaystyle \left \{ \begin{pmatrix}" + vars_tex +
            r"\end{pmatrix} \in \mathbb{R}^{" + str(m) + r"} \; \Bigg | \; \begin{cases}" +
            eqs_tex + r"\end{cases} \right \}"
        )