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
  gcd, x, y = extended_euclidean_algorithm(n, p) 
  return x % p

def elliptic_curve_addition(self, other: Point) -> Point:
  # handle special case of P + 0 = 0 + P = 0
  if self == INF: return other
  if other == INF: return self
  # handle special case of P + (-P) = 0
  if self.x == other.x and self.y != other.y: return INF
  # compute the slope
  if self.x == other.x:
    m = (3 * self.x**2 + self.curve.a) * inv(2 * self.y, self.curve.p)
  else:
    m = (self.y - other.y) * inv(self.x - other.x, self.curve.p)
  # compute the new point
  rx = (m**2 - self.x - other.x) % self.curve.p
  ry = (-(m*(rx - self.x) + self.y)) % self.curve.p
  return Point(self.curve, rx, ry)
Point.__add__ = elliptic_curve_addition

sk = 1 # secret key
pk = G # public key (because 1 * G = G)
print(f"secret key: {sk}\npublic key: {(pk.x, pk.y)}")
print("Verify public key is on the curve: ", (pk.y**2 - pk.x**3 - 7) % bitcoin_curve.p == 0)
# if it was 2, the public key is G + G:
sk = 2
pk = G + G
print(f" secret key: {sk}\n public key: {(pk.x, pk.y)}")
print("Verify the public key is on the curve: ", (pk.y**2 - pk.x**3 - 7) % bitcoin_curve.p == 0)
# etc.:
sk = 3
pk = G + G + G
print(f" secret key: {sk}\n public key: {(pk.x, pk.y)}")
print("Verify the public key is on the curve: ", (pk.y**2 - pk.x**3 - 7) % bitcoin_curve.p == 0)

def double_and_add(self, k: int) -> Point:
  assert isinstance(k, int) and k >= 0
  result = INF
  append = self
  while k:
    if k & 1:
      result += append
    append += append
    k >>= 1
  return result
Point.__rmul__ = double_and_add

print(G == 1*G)
print(G + G == 2*G)
print(G + G + G == 3*G)

public_key = secret_key * G
print(f"x: {public_key.x}\ny: {public_key.y}")
print("Verify the public key is on the curve: ", (public_key.y**2 - public_key.x**3 - 7) % bitcoin_curve.p == 0)
