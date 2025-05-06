from dataclasses import dataclass, field
from math import pi, e
from .scalar_quantity import ScalarQuantity

@dataclass(slots=True, frozen=True)
class Constants:
    """
    Contiene las constantes físicas más usuales con sus correspondientes
    unidades en el SI.
    """
    e0: ScalarQuantity = field(default_factory=lambda: ScalarQuantity(
        float('8.854187817e-12'),
        'F/m = F/m'
    ))
    """
    Permisividad eléctrica del vacío (ε₀) en F/m.
    Fuente: CODATA 2018.
    """
    
    mu0: ScalarQuantity = field(default_factory=lambda: ScalarQuantity(
        4 * pi * 1e-7,
        'N/A^2 = N/A**2'
    ))
    """
    Permeabilidad magnética en el vacío (μ₀) en N/A².
    """
    
    c: ScalarQuantity = field(default_factory=lambda: ScalarQuantity(
        float('299792458'),
        'm/s = m/s'
    ))
    """
    Velocidad de la luz en el vacío (c) en m/s.
    """
    
    PI: ScalarQuantity = field(default_factory=lambda: ScalarQuantity(pi, '1'))
    """
    Número Pi.
    """
    
    E: ScalarQuantity = field(default_factory=lambda: ScalarQuantity(e, '1'))
    """
    Número e.
    """
    
    e_: ScalarQuantity = field(default_factory=lambda: ScalarQuantity(float('1.60217662e-19'), 'C'))
    """
    Carga elemental (e) en coulomb.
    """
    
    me_: ScalarQuantity = field(default_factory=lambda: ScalarQuantity(float('9.10938356e-31'), 'kg'))
    """
    Masa del electrón (mₑ) en kg.
    """
    
    mp_: ScalarQuantity = field(default_factory=lambda: ScalarQuantity(float('1.6726219e-27'), 'kg'))
    """
    Masa del protón (mₚ) en kg.
    """
    
    mn_: ScalarQuantity = field(default_factory=lambda: ScalarQuantity(
        float('1.674927471e-27'),
        'kg'
    ))
    """
    Masa del neutrón (mₙ) en kg.
    """
    
    G: ScalarQuantity = field(default_factory=lambda: ScalarQuantity(
        float('6.67430e-11'),
        'N·m^2/kg^2 = N*m**2/kg**2'
    ))
    """
    Constante gravitacional universal (G) en N·m²/kg².
    """
    
    h: ScalarQuantity = field(default_factory=lambda: ScalarQuantity(
        float('6.62607015e-34'),
        'J*s=J*s'
    ))
    """
    Constante de Planck (h) en J·s.
    """
    
    Na: ScalarQuantity = field(default_factory=lambda: ScalarQuantity(
        float('6.02214076e23'),
        '1/mol = 1/mol'
    ))
    """
    Número de Avogadro.
    """
    
    kB: ScalarQuantity = field(default_factory=lambda: ScalarQuantity(
        float('1.380649e-23'),
        'J/K=J/K'
    ))
    """
    Constante de Boltzmann en J/K.
    """
    
    R: ScalarQuantity = field(default_factory=lambda: ScalarQuantity(
        float('8.314462618'),
        'J/(mol*K)= J/(mol*K)'
    ))
    """
    Constante de los gases en J/(mol*K).
    """
    
    sigma: ScalarQuantity = field(default_factory=lambda: ScalarQuantity(
        float('5.670374419e-8'),
        'W/(m**2*K**4)'
    ))
    """
    Constante de Stefan-Boltzmann en W/(m²K⁴).
    """
    
    alpha: ScalarQuantity = field(default_factory=lambda: ScalarQuantity(
        float('7.2973525693e-3'),
        '1'
    ))
    """
    Constante de estructura fina.
    """
    
    phi0: ScalarQuantity = field(default_factory=lambda: ScalarQuantity(
        float('2.067833848e-15'),
        'Wb = T*m**2'
    ))
    """
    Cuanto de flujo magnético en Weber (Wb).
    """

    @classmethod
    def as_dict(cls) -> dict[str, ScalarQuantity]:
        """
        Retorna un diccionario con todas las constantes definidas.
        """
        return {key: getattr(cls, key) for key in cls.__dataclass_fields__.keys()}
    
    def __getitem__(self, key: str) -> ScalarQuantity:
        """
        Permite acceder a las constantes mediante indexación como un diccionario.
        """
        dt = self.as_dict()
        if key in dt:
            return dt[key]
        raise KeyError(f"Constante desconocida: {key}")
    
    def __contains__(self, key: str) -> bool:
        """
        Permite verificar si una constante está definida.
        """
        return key in self.as_dict()
    
    def __repr__(self) -> str:
        return "\n".join(f"{key} -> {value}" for key, value in self.as_dict().items())
