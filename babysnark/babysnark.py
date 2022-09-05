
from finitefield.modp import IntegersModP

if __name__ == "__main__":
  mod7 = IntegersModP(7)
  x = mod7(2)
  y = mod7(12)
  print(mod7, x, y)