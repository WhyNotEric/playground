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
  
    return np.array([[random_fp() for _ in range(n)] for _ in range(m)])

def generate_solved_instance(m, n):
  a = np.array([random_fp() for _ in range(n)])
  U = random_matrix(m, n)

  # Normalize U to satisfy constraints
  Ua2 = U.dot(a) * U.dot(a)
  for i in range(m):
      U[i,:] /= Ua2[i].sqrt()

  assert((U.dot(a) * U.dot(a) == 1).all())
  return U, a

# U, a = generate_solved_instance(10, 12)
# print(U)

def evaluate_in_exponent(powers_of_tau, poly):
  print('P.degree:', poly.degree())
  print('taus:', len(powers_of_tau))
  assert poly.degree()+1 < len(powers_of_tau)
  return sum([powers_of_tau[i] * poly.coefficients[i] for i in
              range(poly.degree()+1)], G*0)

def babysnark_setup(U, n_stmt):
  (m, n) = U.shape
  assert n_stmt < n

  # Generate roots for each gate
  global ROOTS
  if len(ROOTS) < m:
      ROOTS = tuple(range(m))

  # Generate polynomials u from columns of U
  Us = [Poly.interpolate(ROOTS[:m], U[:,k]) for k in range(n)]

  # Trapdoors
  global tau, beta, gamma
  tau   = random_fp()
  beta  = random_fp()
  gamma = random_fp()

  # CRS elements
  CRS = [G * (tau ** i) for i in range(m+1)] + \
        [G * gamma, G * (beta * gamma)] + \
        [G * (beta * Ui(tau)) for Ui in Us[n_stmt:]]

  # Precomputation
  # Note: This is not considered part of the trusted setup, since it
  # could be computed direcftly from the G * (tau **i) terms.

  # Compute the target poly term
  t = vanishing_poly(ROOTS[:m])
  T = G * t(tau)

  # Evaluate the Ui's corresponding to statement values
  Uis = [G * Ui(tau) for Ui in Us]
  precomp = Uis, T

  return CRS, precomp

def babysnark_prover(U, n_stmt, CRS, precomp, a):
  (m,n) = U.shape
  assert n == len(a)
  assert len(CRS) == (m + 1) + 2 + (n - n_stmt)
  assert len(ROOTS) >= m

  taus = CRS[:m+1]
  bUis = CRS[-(n-n_stmt):]

  Uis, T = precomp

  t = vanishing_poly(ROOTS[:m])

  Us = [Poly.interpolate(ROOTS[:m], U[:,k]) for k in range(n)]

  v = Poly([])

  for k in range(n):
    v += Us[k] * a[k]
  
  p = v * v - 1
  h = p / t

  H = evaluate_in_exponent(taus, h)
  Vw = sum([Uis[k] * a[k] for k in range(n_stmt, n)], G*0)
  Bw = sum([bUis[k-n_stmt] * a[k] for k in range(n_stmt, n)], G*0)

  return H, Bw, Vw

def babysnark_verifier(U, CRS, precomp, a_stmt, pi):
  (m, n) = U.shape
  (H, Bw, Vw) = pi
  assert len(ROOTS) >= m
  n_stmt = len(a_stmt)

  taus = CRS[:m+1]
  gamma = CRS[m+1]
  gammabeta = CRS[m+2]
  bUis = CRS[-(n-n_stmt)]

  Uis, T = precomp
  # Compute Vs and V = Vs + Vw
  Vs = sum([Uis[k] * a_stmt[k] for k in range(n_stmt)], G * 0)
  V = Vs + Vw

  # Check 1
  print('Checking (1)')
  assert Bw.pair(gamma) == Vw.pair(gammabeta)

  # Check 2
  print('Checking (2)')
  # print('GT', GT)
  # print('V:', V)
  # print('H.pair(T) * GT:', H.pair(T) * GT)
  # print('V.pair(V):', V.pair(V))
  assert H.pair(T) * GT == V.pair(V)

  return True


if __name__ == "__main__":

  # Fp = FiniteField(53, 1)
  # Poly = polynomialsOver(Fp)

  # def _polydemo():
  #   p1 = Poly([1, 2, 3, 4, 5])
  #   # print(p1)

  # # integer module
  # mod7 = IntegersModP(7)
  # x = mod7(2)
  # y = mod7(12)
  # print(mod7, x, y)

  # # poly demo
  # _polydemo()


  print("Generating a Square Span Program instance")
  n_stmt = 4
  m,n = (16, 6)
  U, a = generate_solved_instance(m, n)
  a_stmt = a[:n_stmt]
  print('U:', repr(U))
  print('a_stmt:', a_stmt)
  print('nonzero in U:', np.sum(U == Fp(0)))
  print('m x n:', m * n)

  print("Computing Setup...")
  CRS, precomp = babysnark_setup(U, n_stmt)
  print("CRS length:", len(CRS))

  print("Proving...")
  H, Bw, Vw = babysnark_prover(U, n_stmt, CRS, precomp, a)

  print("Verifying....")
  babysnark_verifier(U, CRS, precomp, a[:n_stmt], (H, Bw, Vw))



