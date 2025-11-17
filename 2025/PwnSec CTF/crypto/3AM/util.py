import hashlib, hmac

def inv_mod(a, m): 
    return pow(a, -1, m)

def HKDF(key, info, outlen=32):
    prk = hmac.new(b"\x00"*32, key, hashlib.sha256).digest()
    out = b""; t = b""; c = 1
    while len(out) < outlen:
        t = hmac.new(prk, t + info + bytes([c]), hashlib.sha256).digest()
        out += t; c += 1
    return out[:outlen]

def sha256_int(b):
    return int.from_bytes(hashlib.sha256(b).digest(), 'big')

def parse_msg_bytes(s):
    s = s.strip()
    if s.startswith(("0x","0X")):
        h = s[2:]
        if len(h) % 2: h = "0"+h
        return bytes.fromhex(h)
    return s.encode()

def ec_add(P1, P2, Pmod, Acoeff):
    if P1 is None: return P2
    if P2 is None: return P1
    x1,y1 = P1; x2,y2 = P2
    if x1 == x2 and (y1 + y2) % Pmod == 0: return None
    if P1 == P2:
        s = (3*x1*x1 + Acoeff) * inv_mod((2*y1) % Pmod, Pmod) % Pmod
    else:
        s = (y2 - y1) * inv_mod((x2 - x1) % Pmod, Pmod) % Pmod
    x3 = (s*s - x1 - x2) % Pmod
    y3 = (s*(x1 - x3) - y1) % Pmod
    return (x3, y3)

def ec_mul(k, P_, N, Pmod, Acoeff):
    if k % N == 0 or P_ is None: return None
    k %= N
    Q = None; A_ = P_
    while k:
        if k & 1: Q = ec_add(Q, A_, Pmod, Acoeff)
        A_ = ec_add(A_, A_, Pmod, Acoeff)
        k >>= 1
    return Q

def bits_clear_windows(x, windows):
    for pos, width in windows:
        mask = ((1 << width) - 1) << pos
        x &= ~mask
    return x

def ff_add(P1, P2, p_field, Acoef, Bcoef):
    if P1 is None: return P2
    if P2 is None: return P1
    x1,y1 = P1; x2,y2 = P2
    if x1 == x2 and (y1 + y2) % p_field == 0: return None
    if P1 == P2:
        s = (3*x1*x1 + Acoef) * inv_mod((2*y1) % p_field, p_field) % p_field
    else:
        s = (y2 - y1) * inv_mod((x2 - x1) % p_field, p_field) % p_field
    x3 = (s*s - x1 - x2) % p_field
    y3 = (s*(x1 - x3) - y1) % p_field
    return (x3, y3)

def ff_mul(k, P_, p_field, Acoef, Bcoef):
    if k == 0 or P_ is None: return None
    Q = None; A_ = P_
    while k:
        if k & 1: Q = ff_add(Q, A_, p_field, Acoef, Bcoef)
        A_ = ff_add(A_, A_, p_field, Acoef, Bcoef)
        k >>= 1
    return Q

def ff_random_point(p_field, Acoef, Bcoef):
    import secrets
    while True:
        x = secrets.randbelow(p_field)
        y2 = (x*x*x + Acoef*x + Bcoef) % p_field
        if y2 == 0:
            y = 0
            return (x, y)
        if pow(y2, (p_field-1)//2, p_field) == p_field-1:
            continue
        if p_field % 4 == 3:
            y = pow(y2, (p_field+1)//4, p_field)
        else:
            q = p_field-1; s = 0
            while q % 2 == 0: q//=2; s+=1
            z = 2
            while pow(z, (p_field-1)//2, p_field) != p_field-1: z += 1
            c = pow(z, q, p_field); x_ts = pow(y2, (q+1)//2, p_field)
            t = pow(y2, q, p_field); m = s
            while t != 1:
                i = 1; tt = (t*t) % p_field
                while tt != 1:
                    tt = (tt*tt) % p_field; i += 1
                b = pow(c, 1 << (m - i - 1), p_field)
                x_ts = (x_ts*b) % p_field
                c = (b*b) % p_field
                t = (t*c) % p_field
                m = i
            y = x_ts
        if y is not None:
            if __import__("secrets").randbits(1): y = (-y) % p_field
            return (x, y)

def mobius_apply(lam, mu, nu, x, p_field):
    d = (nu * x + 1) % p_field
    if d == 0: return None
    return ((lam * x + mu) * inv_mod(d, p_field)) % p_field
