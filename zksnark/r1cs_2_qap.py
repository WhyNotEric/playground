# Polynomials are stored as arrays, where the ith element in
# the array is the ith degree coefficient
# [1, 2, 3, 4] == 1 * x**0 + 2 * x**1 + 3 * x**2 ...

from audioop import mul


def multiply_ploys(a, b):
  output = [0] * (len(a) + len(b) - 1)
  for i in range(len(a)):
    for j in range(len(b)):
      output[i + j] += a[i] * b[j]
  return output

def add_ploys(a, b, subtract=False):
  output = [0] * max(len(a), len(b))
  for i in range(len(a)):
    output[i] += a[i]
  for i in range(len(b)):
    output[i] += b[i] * (-1 if subtract else 1)
  return output

def subtract_ploys(a, b):
  return add_ploys(a, b, subtract=True)

def div_ploys(a, b):
  output = [0] * (len(a) - len(b) + 1)
  remainder = a
  while len(remainder) >= len(b):
    leading_fac = remainder[-1] / b[-1]
    pos = len(remainder) - len(b)
    output[pos] = leading_fac
    remainder = subtract_ploys(remainder, multiply_ploys(b, [0] * pos + [leading_fac]))[:-1]
  return output, remainder

# evaluate a ployminal at x point
def eval_ploy(ploy, x):
  return sum([ploy[i] * x**i for i in range(len(ploy))])

# Make a polynomial which is zero at {1, 2 ... total_pts}, except
# for `point_loc` where the value is `height`
def mk_singleton(point_loc, height, total_pts):
  fac = 1
  for i in range(1, total_pts + 1):
    if i != point_loc:
      fac *= point_loc - i
  
  output = [height * 1.0 / fac]

  for i in range(1, total_pts + 1):
    if i != point_loc:
      output = multiply_ploys(output, [-i, 1])
  
  return output


def lagrange_interp(vec):
  output = []
  for i in range(len(vec)):
    output = add_ploys(output, mk_singleton(i+1, vec[i], len(vec)))
  
  for i in range(len(vec)):
    assert abs(eval_ploy(output, i+1) - vec[i] < 10**-10), (output, eval_ploy(output, i+1), i+1)
  
  return output


def transpose(matrix):
  return list(map(list, zip(*matrix)))


def r1cs_to_qap(A, B, C):
  A, B, C = transpose(A), transpose(B), transpose(C)

  print("--A", A)
  print("--B", B)
  print("--C", C)
  new_A = [lagrange_interp(a) for a in A]
  new_B = [lagrange_interp(b) for b in B]
  new_C = [lagrange_interp(c) for c in C]
  Z = [1]

  for i in range(1, len(A[0]) + 1):
    Z = multiply_ploys(Z, [-i, 1])
  
  print("--new_A", new_A)
  print("--new_B", new_B)
  print("--new_C", new_C)
  print("--Z", Z)
  return new_A, new_B, new_C, Z


def create_solution_polynomials(r, new_A, new_B, new_C):
  A_ploy = []
  for rval, a in zip(r, new_A):
    A_ploy = add_ploys(A_ploy, multiply_ploys([rval], a))
  B_ploy = []
  for rval, b in zip(r, new_B):
    B_ploy = add_ploys(B_ploy, multiply_ploys([rval], b))
  C_ploy = []
  for rval, c in zip(r, new_C):
    C_ploy = add_ploys(C_ploy, multiply_ploys([rval], c))
  
  output = subtract_ploys(multiply_ploys(A_ploy, B_ploy), C_ploy)
  for i in range(1, len(new_A[0]) + 1):
    assert abs(eval_ploy(output, i) < 10**-10), (eval_ploy(output, i), i)
  
  return A_ploy, B_ploy, C_ploy, output

def create_divisor_polynomial(sol, Z):
  quot, remainder = div_ploys(sol, Z)
  for x in remainder:
    assert abs(x) < 10**-10
  return quot


r = [1, 3, 35, 9, 27, 30]
A = [[0, 1, 0, 0, 0, 0],
     [0, 0, 0, 1, 0, 0],
     [0, 1, 0, 0, 1, 0],
     [5, 0, 0, 0, 0, 1]]
B = [[0, 1, 0, 0, 0, 0],
     [0, 1, 0, 0, 0, 0],
     [1, 0, 0, 0, 0, 0],
     [1, 0, 0, 0, 0, 0]]
C = [[0, 0, 0, 1, 0, 0],
     [0, 0, 0, 0, 1, 0],
     [0, 0, 0, 0, 0, 1],
     [0, 0, 1, 0, 0, 0]]

Ap, Bp, Cp, Z = r1cs_to_qap(A, B, C)
print('Ap')
for x in Ap: print(x)
print('Bp')
for x in Bp: print(x)
print('Cp')
for x in Cp: print(x)
print('Z')
print(Z)
Apoly, Bpoly, Cpoly, sol = create_solution_polynomials(r, Ap, Bp, Cp)
print('Apoly', Apoly)
print('Bpoly', Bpoly)
print('Cpoly', Cpoly)
print('Sol', sol)
print('Z cofactor', create_divisor_polynomial(sol, Z))
