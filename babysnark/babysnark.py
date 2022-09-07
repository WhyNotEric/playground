from finitefield.finitefield import FiniteField
from finitefield.polynomial import polynomialsOver
from finitefield.modp import IntegersModP
from ssbls12 import Fp, Poly, Group
G = Group.G
GT = Group.GT

ROOTS = [Fp(i) for i in range(128)]

def vanishing_poly(S):
  p = Poly([Fp(1)])
  for s in S:
    p *= Poly([-s, Fp(1)])
  return p


import numpy as np
import random

def random_fp():
  return Fp(random.randint(0, Fp.p-1))

def random_matrix(m, n):
  return np.array([[random_fp() for _ in range(n)]] for _ in range(m))

def generate_solved_instance(m, n):
  a = np.array([random_fp() for _ in range(n)])
  U = random_matrix(m, n)

  Ua2 = U.dot(a) * U.dot(a)

  for i in range(m):
    U[i,:] /= Ua2[i].sqrt()
  
  assert((U.dot(a) * U.dot(a) == 1).all())
  return U, a

U, a = generate_solved_instance(10, 12)


def evaluate_in_exponent(powers_of_tau, poly):
  print('P.degree', poly.degree())
  print('taus:', len(powers_of_tau))
  assert poly.degree()+1 < len(powers_of_tau)
  return sum([powers_of_tau[i] * poly.coefficients[i] for i in range(poly.degree()+1)], G*0)

def babysnark_setup(U, n_stmt):
  (m, n) = U.shape
  assert n_stmt < n

  global ROOTS
  if len(ROOTS) < m:
    ROOTS = tuple(range(m))
  
  Us = [Poly.interpolate(ROOTS[:m], U[:, k]) for k in range(n)]

  global tau, beta, gamma
  tau = random_fp()
  beta = random_fp()
  gamma = random_fp()

  # CRS elements
  CRS = [G * (tau ** i) for i in range(m+1)] + \
        [G * gamma, G * (beta * gamma)] + \
        [G * (beta * Ui(tau)) for Ui in Us[n_stmt:]]



if __name__ == "__main__":

  Fp = FiniteField(53, 1)
  Poly = polynomialsOver(Fp)

  def _polydemo():
    p1 = Poly([1, 2, 3, 4, 5])
    print(p1)

  # integer module
  mod7 = IntegersModP(7)
  x = mod7(2)
  y = mod7(12)
  print(mod7, x, y)

  # poly demo
  _polydemo()

