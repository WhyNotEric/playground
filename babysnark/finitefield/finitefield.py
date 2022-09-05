import imp
import random
from .polynomial import polynomialsOver
from .modp import *

def isIrreducible(polynomial, p):
  ZmodP = IntegersModP(p)