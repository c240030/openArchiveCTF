import sys
from sage.all import *
proof.all(False)

p = 0x1a0111ea397fe69a4b1ba7b6434bacd764774b84f38512bf6730d2a0f6b0f6241eabfffeb153ffffb9feffffffffaaab
Fp = GF(p)
F12 = GF(p**12, name='a'); a = F12.gens()[0]
RF = PolynomialRing(F12, name='T'); T = RF.gens()[0]
j = (T**2 + 1).roots(ring=RF, multiplicities=0)[0]
E2 = EllipticCurve(F12, [0, 4*(j+1)])

alice = eval(sys.argv[1])
bob = eval(sys.argv[2])
charlie = eval(sys.argv[3])

def get_pt(c):
    x = sum([Fp(k) * a**i for i, k in enumerate(c)])
    return E2.lift_x(x)

P_New = get_pt(charlie) - get_pt(alice) - get_pt(bob)

lx = P_New[0].list(); ly = P_New[1].list()
while len(lx)<12: lx.append(0)
while len(ly)<12: ly.append(0)
print(f"{str(lx)[1:-1]}|{str(ly)[1:-1]}")
