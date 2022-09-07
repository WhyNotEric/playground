from py_ecc import optimized_bls12_381 as bls12_381
from py_ecc.optimized_bls12_381 import add, multiply, eq


from finitefield.finitefield import FiniteField
from finitefield.polynomial import polynomialsOver
from finitefield.euclidean import extendedEuclideanAlgorithm

from functools import reduce

Fp = FiniteField(52435875175126190479447740508185965837690552500527637822603658699938581184513, 1)
Poly = polynomialsOver(Fp)
Fp.__expr__ = lambda self: hex(self.n)[:15] + "..." if len(hex(self.n)) >= 15 else hex(self.n)

class SS_BLS12_381:

  def __init__(self, m1, m2):
    self.m1 = m1
    self.m2 = m2

  def in_group(self):
    return bls12_381.pairing(self.m2, bls12_381.G1) == bls12_381.pairing(bls12_381.G2, self.m1)
  
  order = bls12_381.curve_order

  def __add__(self, other):
    assert type(other) is SS_BLS12_381
    return SS_BLS12_381(add(self.m1, other.m1), add(self.m2, other.m2))
  
  def __mul__(self, x):
    assert type(x) in (int, Fp)
    if type(x) is Fp:
        x = x.n
    return SS_BLS12_381(multiply(self.m1, x), multiply(self.m2, x))
  
  def __rmul__(self, other):
    return self.__mul__(other)
  
  def __eq__(self, other):
    return eq(self.m1, other.m1) and eq(self.m2, other.m2)
  
  def pair(self, other):
    t1 = bls12_381.pairing(self.m2, other.m1)
    return t1
  
  def __repr__(self) -> str:
    return repr(self.m1)
  
SS_BLS12_381.G = SS_BLS12_381(bls12_381.G1, bls12_381.G2)
SS_BLS12_381.GT = SS_BLS12_381.G.pair(SS_BLS12_381.G)
Group = SS_BLS12_381

