from typing import Type


def memoize(f):
  cache = {}

  def memoizedFunction(*args, **kwargs):
    argTuple = args + tuple(kwargs)
    if argTuple not in cache:
      cache[argTuple] = f(*args, **kwargs)
    return cache[argTuple]
  
  memoizedFunction.cache = cache
  return memoizedFunction

def typecheck(f):
  def newF(self, other):
    if (
      hasattr(other.__class__, "operatorPrecedence") and other.__class__.operatorPrecedence > self.__class__.operatorPrecedence
    ):
      return NotImplemented
    
    if type(self) is not type(other):
      try:
        other = self.__class__(other)
      except TypeError:
        message = "Not able to typecase %s of type %s to type %s in function %s"
        raise TypeError(message % (other, type(other).__name__, type(self).__name__, f.__name__))
      except Exception as e:
        message = "Type error on arguments %r, %r for function %s. Reason: %s"
        raise TypeError(message % (self, other, f.__name__, e))
    
    return f(self, other)
  
  return newF


class DomainElement(object):
  operatorPrecedence = 1

  def __radd__(self, other):
    return self + other
  
  def __rsub__(self, other):
    return -self + other
  
  def __rmul__(self, other):
    return self * other
  
  def __pow__(self, n):
    if type(n) is not int:
      print(type(n))
      raise TypeError
    
    Q = self
    R = self if n & 1 else self.__class__(1)

    i = 2
    while i <= n:
      Q = Q * Q
      if n & i == i:
        R = Q * R
      
      i = i << 1
    
    return R

  def powmod(self, n, modules):
    if type(n) is not int and type(n) is not long:
      raise TypeError
    
    Q = self
    R = self if n & 1 else self.__class__(1)

    i = 2
    while i <= n:
      Q = (Q * Q) % modules
      if n & i == i:
        R = (Q * R) % modules
      
      i = i << 1
    
    return R
  
class FieldElement(DomainElement):
  def __truediv__(self, other):
    return self * other.inverse()
  
  def __rtruediv__(self, other):
    return self.inverse() * other
  
  def __div__(self, other):
    return self.__truediv__(other)
  
  def __rdiv__(self, other):
    return self.__rtruediv__(other)

