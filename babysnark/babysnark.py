
from finitefield.finitefield import FiniteField
from finitefield.polynomial import polynomialsOver
from finitefield.modp import IntegersModP

Fp = FiniteField(53, 1)
Poly = polynomialsOver(Fp)

def _polydemo():
  p1 = Poly([1, 2, 3, 4, 5])
  print(p1)

if __name__ == "__main__":
  # integer module
  mod7 = IntegersModP(7)
  x = mod7(2)
  y = mod7(12)
  print(mod7, x, y)

  # poly demo
  _polydemo()