from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Curve:
  p: int # prime modulus of finite field
  a: int
  b: int

# curve: y^2 = x^3 + 7 (mod p)
bitcoin_curve = Curve(
  p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F, 
  a = 0x0000000000000000000000000000000000000000000000000000000000000000, # 0
  b = 0x0000000000000000000000000000000000000000000000000000000000000007, # 7
)

@dataclass
class Point:
  """ An interger point on a Curve """
  curve: Curve
  x: int
  y: int

# this generator point is publically known and agreed upon
G = Point(
  bitcoin_curve,
  x = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
  y = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8,
)
print("Generator IS on the curve: ", (G.y**2 - G.x**3 - 7) % bitcoin_curve.p == 0)

@dataclass
class Generator:
  """
  A generator over a curve: an initial point and the (pre-computed) order
  """
  G: Point
  n: int

bitcoin_gen = Generator(
  G = G, # the order of G is known and can be mathematically derived
  n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
)

secret_key = int.from_bytes(b"Lukas is cool", "big")
assert 1 <= secret_key < bitcoin_gen.n
print(secret_key)

INF = Point(None, None, None)

def extended_euclidean_algorithm(a, b):
  """
  Returns (gcd, x, y) s.t. a * x + b * y == gcd
  Runs in O(log b) in the worst case
  """
  old_r, r = a, b
  old_s, s = 1, 0
  old_t, t = 0, 1
  while r != 0:
    quotient = old_r // r
    old_r, r = r, old_r - quotient * r
    old_s, s = s, old_s - quotient * r
    old_t, t = t, old_t - quotient * r
  return old_r, old_s, old_t

def inv(n, p):
  """ returns modular multiplicate inverse m s.t. (n * m) % p == 1 """
  gcd, x, y = extended_euclidean_algorithm(n, p) # pylint: disable=unused-variable
  return x % p