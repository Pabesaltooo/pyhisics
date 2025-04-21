from pyhsics.linalg._pruebas.symbolic import *

a = (Number(2) + 4.0j)/1j*1j

b = Symbol('b')
d = Symbol('d')
c = b**(2j)

print((((a * b * c * d + a*d) ** b) ** (a*1j  + 3))._repr_latex_())