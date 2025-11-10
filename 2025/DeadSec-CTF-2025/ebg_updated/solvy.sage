#!/usr/bin/env sage
# Credits and References: https://github.com/Sarkoxed

from sage.all import (
    GF,
    EllipticCurve,
    gcd,
    Matrix,
    QQ,
    vector,
    Zmod,
    discrete_log,
    PolynomialRing,
    factor,
    crt,
    euler_phi,
    is_prime,
    ZZ,
)
import itertools as it
from output_69 import collect, hints, ct
from Crypto.Cipher import AES
from hashlib import sha256


def recover_ec_params():
    """
    Recover elliptic curve parameters (p, a, b) from collected points.
    """
    assert len(collect) == 50
    x0, y2_0 = collect[0][1], collect[0][2]
    x1, y2_1 = collect[1][1], collect[1][2]

    # Set up matrix equation to solve for a and b
    M = Matrix(QQ, [[x0, 1], [x1, 1]])
    v = vector(QQ, [y2_0 - x0**3, y2_1 - x1**3])

    a, b = M.solve_right(v)

    # Compute GCD to find the modulus p
    gcds = []
    for i in range(2, 50):
        _, x, y2 = collect[i]
        res = y2 - x**3 - a * x - b
        gcds.append(res.numerator())
    p = gcd(gcds)
    
    # Convert a and b to elements in Fp
    a = a.numerator() * pow(a.denominator(), -1, p) % p
    b = b.numerator() * pow(b.denominator(), -1, p) % p
    
    return p, a, b


def recover_q(E, G, hints):
    """
    Recover the modulus q from the hints.
    """
    o = 23 * 16883 * 43093 * 63247 * 12779779 * 14406383 * 1447085987
    assert G.order() == o

    eq0 = discrete_log(E(hints[1]), G, operation="+")
    eq1 = discrete_log(E(hints[2]), G, operation="+")

    # X**2 + 69 * Y**3 = eq0
    # 420 * X**3 + Y**2 == eq1

    # Use CRT to recover Y
    rs, mods = [], []
    for r, _ in factor(o):
        P = PolynomialRing(GF(r), "Y")
        Y = P.gen()

        left = (eq0 - 69 * Y**3) ** 3
        right = ((eq1 - Y**2) * pow(420, -1, r)) ** 2
        poly = left - right

        rs.append([int(x) for x, _ in poly.roots()])
        mods.append(r)

    Ys = []
    for rems in it.product(*rs):
        tmp = int(crt(list(rems), mods))
        if tmp.bit_length() == 84:
            Ys.append(tmp)

    assert len(Ys) == 1
    Y = Ys[0]

    # Use CRT to recover X
    rs = []
    for r, _ in factor(o):
        P = PolynomialRing(GF(r), "X")
        X = P.gen()
        poly = 420 * X**3 + Y**2 - eq1
        rs.append([int(x) for x, _ in poly.roots()])

    Xs = []
    for rems in it.product(*rs):
        tmp = int(crt(list(rems), mods))
        if tmp.bit_length() == 84:
            Xs.append(tmp)
    assert len(Xs) == 1
    X = Xs[0]
    
    # Combine X and Y to form q
    return (X << 84) + Y


class LCG:
    """
    Linear Congruential Generator implementation.
    """
    def __init__(self, seed, a, b, q=None):
        self.a, self.b = Fq(a), Fq(b)
        self.state = Fq(seed)

    def next_state(self):
        nxt = self.state * self.a + self.b
        self.state = nxt
        return int(nxt)


def recover_seed(collect, E, p, q, a, b):
    """
    Recover the LCG seed from collected points.
    """
    i, j = 0, 1
    assert collect[i][0] == collect[j][0] - 1

    x0 = collect[i][1]
    y0 = int(E.lift_x(ZZ(x0))[1])
    y1 = int(p - y0)
    assert pow(y0, 2, p) == collect[i][2]
    assert pow(y1, 2, p) == collect[i][2]

    x1 = collect[j][1]
    y2 = int(E.lift_x(ZZ(x1))[1])
    y3 = p - y2

    for s0, s1 in it.product([y0, y1], [y2, y3]):
        K = (s0 * a + b - s1) * pow(q, -1, p) % p
        tmp = (s1 + K * q - s0 * a - b) // p
        R1 = -tmp % a
        R0 = (tmp + R1) // a

        beta0 = s0 + R0 * p
        beta1 = s1 + R1 * p

        # Check if beta0 is the correct seed
        g = LCG(beta0, a, b)
        if g.next_state() == beta1:
            return beta0
    
    return None


def check_seed(seed, collect, p, q, a, b):
    """
    Verify if the recovered seed is correct.
    """
    lcg = LCG(seed, a, b)
    cntr = 1
    for i, _, y2 in collect[1:]:
        while cntr != i - 1:
            lcg.next_state()
            cntr += 1
        cur = lcg.next_state()
        cntr += 1
        if pow(cur, 2, p) != y2:
            print("UUUUUU", i)
            return False
        assert pow(cur, 2, p) == y2
    return True


def decrypt_flag(seed, p, q, a, b, ct):
    """
    Decrypt the flag using the recovered seed.
    """
    lcg = LCG(seed, a, b, q)
    cntr = 1
    while cntr != collect[-1][0]:
        lcg.next_state()
        cntr += 1

    state = lcg.next_state()
    power = 10**18
    rmp = (pow(a, power, q) * state + (pow(a, power, q) - 1) * pow(a - 1, -1, q) * b) % q

    key = sha256(str(rmp).encode()).digest()
    pt = AES.new(key, AES.MODE_ECB).decrypt(bytes.fromhex(ct))
    return pt


def main():
    # Recover elliptic curve parameters
    p, a, b = recover_ec_params()
    print(f"{p, a, b = }")
    E = EllipticCurve(GF(p), [a, b])
    G = E.gens()[0]
    
    # Recover q
    global Fq
    q = recover_q(E, G, hints)
    assert is_prime(q)
    print(f"{q = }")
    Fq = GF(q)
    
    # Recover seed
    seed = recover_seed(collect, E, p, q, a, b)
    print(f"{seed = }")
    
    # Check if seed is correct
    check_seed(seed, collect, p, q, a, b)
    
    # Decrypt flag
    flag = decrypt_flag(seed, p, q, a, b, ct)
    print(f"Flag: {flag}")
    
    # Save output for solve.py to use
    import json
    output_data = {
        "p": str(p),
        "a": str(a),
        "b": str(b),
        "q": str(q),
        "seed": str(seed),
        "ct": ct,
        "last_collect_idx": collect[-1][0]
    }
    
    with open("solve_output.json", "w") as f:
        json.dump(output_data, f)
    
    return flag


if __name__ == "__main__":
    flag = main()
