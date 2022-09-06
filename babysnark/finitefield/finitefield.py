import random
from .polynomial import polynomialsOver
from .modp import *

def isIrreducible(polynomial, p):
  ZmodP = IntegersModP(p)
  if polynomial.field is not ZmodP:
        raise TypeError(
            "Given a polynomial that's not over %s, but instead %r"
            % (ZmodP.__name__, polynomial.field.__name__)
        )

  poly = polynomialsOver(ZmodP).factory
  x = poly([0, 1])
  powerTerm = x
  isUnit = lambda p: p.degree() == 0

  for _ in range(int(polynomial.degree() / 2)):
      powerTerm = powerTerm.powmod(p, polynomial)
      gcdOverZmodp = gcd(polynomial, powerTerm - x)
      if not isUnit(gcdOverZmodp):
          return False

  return True


def generateIrreduciblePolynomial(modules, degree):
  Zp = IntegersModP(modules)
  Polynomial = polynomialsOver(Zp)
  while True:
    coefficients = [Zp(random.randint(0, modules - 1) for _ in range(degree))]
    randomMonicPolynomial = Polynomial(coefficients + (Zp(1)))
    print(randomMonicPolynomial)

    if isIrreducible(randomMonicPolynomial, modules):
      return randomMonicPolynomial
    
@memoize
def FiniteField(p, m, ploynomialModules=None):
  Zp = IntegersModP(p)
  if m == 1:
    return Zp
  
  Polynomial = polynomialsOver(Zp)
  if ploynomialModules is None:
    ploynomialModules = generateIrreduciblePolynomial(modules=p, degree=m)
  
  class Fq(FieldElement):
    fieldSize = int(p ** m)
    primeSubfield = Zp
    idealGenerator = ploynomialModules
    operatorPrecedence = 3

    def __init__(self, poly):
      if type(poly) is Fq:
        self.poly = poly.poly
      elif type(poly) is int or type(poly) is Zp:
        self.poly = Polynomial([Zp(poly)])
      elif isinstance(poly, Polynomial):
        self.poly = poly % ploynomialModules
      else:
        self.poly = Polynomial([Zp(x) for x in poly]) % ploynomialModules
    
      self.field = Fq

    @typecheck
    def __add__(self, other):
      return Fq(self.poly + other.poly)
    
    @typecheck
    def __sub__(self, other):
      return Fq(self.poly - other.poly)
    
    @typecheck
    def __mul__(self, other):
      return Fq(self.poly * other.poly)

    @typecheck
    def __eq__(self, other):
      return isinstance(other, Fq) and self.poly == other.poly
    
    def __pow__(self, n):
      return Fq(pow(self.poly, n))
    
    def __neg__(self):
      return Fq(-self.poly)
    
    def __abs__(self):
      return abs(self.poly)

    def __repr__(self):
      return repr(self.poly) + " \u2208" + self.__class__.__name__
    
    @typecheck
    def __divmod__(self, divisor):
      quotient, remainder = divmod(self.poly, divisor.poly)
      return (Fq(quotient), Fq(remainder))
    
    def inverse(self):
      if self == Fq(0):
        return ZeroDivisionError
      
      x, y, d = extendedEuclideanAlgorithm(self.poly, self.idealGenerator)
      if d.degree() != 0:
        raise Exception("Somehow this element has no inverse!")
      
      return Fq(x) * Fq(d.coefficients[0].inverse())
  
  Fq.__name__ = "F_{%d^%d}" % (p, m)
  return Fq

