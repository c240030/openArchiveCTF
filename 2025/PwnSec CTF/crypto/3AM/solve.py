import socket
import ssl
import re
import sys
import hashlib
import hmac
from typing import List, Tuple, Dict

# Remote target
HOST = "f618e14e1914fcbd.chal.ctf.ae"
PORT = 443

# secp256k1 params (for ECDSA key recovery)
P  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
A  = 0
B  = 7
Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
N  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Finite-field curve used for dataset/keystream
p_field= 1144001070343154634288961
Acoef= 272144002963733033258483
Bcoef= 454511900449591275020144

# Nonce masking windows (bits cleared)
kHoles= [(36, 24), (140, 24)]

# Small noise bound in dataset
boundb= (1<<16) - 1

# ---------- Utilities ----------

def inv_mod(a: int, m: int) -> int:
    return pow(a, -1, m)

def HKDF(key: bytes, info: bytes, outlen: int = 32) -> bytes:
    prk = hmac.new(b"\x00"*32, key, hashlib.sha256).digest()
    out = b""; t = b""; c = 1
    while len(out) < outlen:
        t = hmac.new(prk, t + info + bytes([c]), hashlib.sha256).digest()
        out += t; c += 1
    return out[:outlen]

def parse_int_hexline(line: str, key: str) -> int:
    m = re.search(rf"^{key}=0x([0-9a-fA-F]+)$", line.strip())
    if not m:
        raise ValueError(f"Couldn't parse {key} from: {line}")
    return int(m.group(1), 16)

# ---------- Networking ----------

class Remote:
    def __init__(self, host: str, port: int, use_tls: bool = False):
        self.host = host
        self.port = port
        self.use_tls = use_tls
        self.sock = None
        self.f = None
        self._connect()

    def _connect(self):
        if self.sock:
            try:
                self.f.close()
            except Exception:
                pass
            try:
                self.sock.close()
            except Exception:
                pass
        if self.use_tls:
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=self.host)
            s.connect((self.host, self.port))
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
        self.sock = s
        self.f = s.makefile('rwb', buffering=0)

    def recv_until(self, marker: bytes) -> bytes:
        buf = b""
        while marker not in buf:
            b = self.f.read(1)
            if not b:
                break
            buf += b
        return buf

    def recv_line(self) -> str:
        line = self.f.readline()
        if not line:
            return ""
        return line.decode(errors='ignore')

    def send_line(self, s: str):
        self.f.write((s + "\n").encode())
        self.f.flush()

    def close(self):
        try:
            self.f.close()
        except Exception:
            pass
        try:
            self.sock.close()
        except Exception:
            pass

# ---------- ECDSA private key recovery from masked nonces ----------

def recover_d_with_z3(samples: List[Tuple[int,int,int,int]]) -> int:
    try:
        from z3 import Solver, Int, And
    except ImportError:
        print("Please install z3-solver: pip install z3-solver", file=sys.stderr)
        sys.exit(1)

    a_list = []
    c_list = []
    for (z, r, s, km) in samples:
        s_inv = inv_mod(s, N)
        a_i = (r * s_inv) % N
        b_i = (z * s_inv) % N
        c_i = (km - b_i) % N
        if c_i > N//2:
            c_i -= N
        a_list.append(a_i)
        c_list.append(c_i)

    m = len(samples)
    S = Solver()
    d = Int('d')
    S.add(And(d > 0, d < N))

    AL = 1 << 24  # each window width

    e_vars = []
    alpha_vars = []
    beta_vars = []

    for i in range(m):
        ei = Int(f'e_{i}')
        ai = Int(f'alpha_{i}')
        bi = Int(f'beta_{i}')
        e_vars.append(ei); alpha_vars.append(ai); beta_vars.append(bi)
        S.add(And(ai >= 0, ai < AL))
        S.add(And(bi >= 0, bi < AL))

    for i in range(m):
        S.add(a_list[i] * d - (1 << 36) * alpha_vars[i] - (1 << 140) * beta_vars[i] - N * e_vars[i] == c_list[i])

    if S.check() != 1:
        raise RuntimeError("Z3 failed to solve for d")
    model = S.model()
    return model[d].as_long() % N

# ---------- Dataset inversion to get t-values ----------

def compute_MK(d: int) -> bytes:
    return HKDF(hashlib.sha256(d.to_bytes(32,'big')).digest(), b"mk", 32)

def derive_t_values(dataset: List[Tuple[int,int,int]], MK: bytes) -> Dict[int, int]:
    # Returns mapping a -> T_a (unique t per multiplier a)
    T: Dict[int,int] = {}
    for (i, a, y) in dataset:
        seed = i.to_bytes(4,'big')
        # beta from b|
        braw = HKDF(MK, b"b|" + seed, 16)
        beta = (int.from_bytes(braw,'big') % (2*boundb+1)) - boundb
        y0 = (y - beta) % p_field

        # Select first ctr such that (nu*mu - lam) != 0 (equivalent to server's check)
        ctr = 0
        while True:
            if ctr == 0:
                raw = HKDF(MK, b"M|" + seed, 96)
            else:
                raw = HKDF(MK, b"M|" + seed + ctr.to_bytes(2,'big'), 96)
            lam = int.from_bytes(raw[:32], 'big') % p_field or 1
            mu  = int.from_bytes(raw[32:64], 'big') % p_field
            nu  = int.from_bytes(raw[64:], 'big') % p_field or 1
            if (nu * mu - lam) % p_field != 0:
                break
            ctr += 1

        denom = (y0 * nu - lam) % p_field
        if denom == 0:
            # extremely unlikely; skip this row
            continue
        t = ( (mu - y0) * inv_mod(denom, p_field) ) % p_field
        if a not in T:
            T[a] = t
        else:
            # verify consistency
            if T[a] != t:
                # If mismatch, prefer the earliest value; continue
                pass
    # Expect three values for a = 2,3,5
    if not all(x in T for x in (2,3,5)):
        raise RuntimeError(f"Missing T values for some a: have {list(T.keys())}")
    return T

# ---------- Recover Kx and r from T2,T3,T5 using division polynomials ----------

def x2_num_den(X, A, B):
    # x(2P) = (X^4 - 2 A X^2 - 8 B X + A^2) / (4 X^3 + 4 A X + 4 B)
    num = X**4 - 2*A*X**2 - 8*B*X + A**2
    den = 4*X**3 + 4*A*X + 4*B
    return num, den

def x3_num_den(X, A, B):
    # Using division polynomials: x(3P) = (x*psi3^2 - psi4*psi2) / psi3^2
    # with psi2=2y -> psi4*psi2 eliminates y^2 -> 8*(x^3+Ax+B)*( ... )
    psi3 = 3*X**4 + 6*A*X**2 + 12*B*X - A**2
    num = X*psi3**2 - 8*(X**3 + A*X + B)*(X**6 + 5*A*X**4 + 20*B*X**3 - 5*A**2*X**2 - 4*A*B*X - 8*B**2 - A**3)
    den = psi3**2
    return num, den

def mod_poly(expr, p):
    # Reduce integer coefficients modulo p
    from sympy import Poly
    X = list(expr.free_symbols)[0]
    poly = Poly(expr, X, modulus=p)
    return poly

def solve_for_Kx_and_r(T2: int, T3: int, T5: int) -> Tuple[int,int]:
    from sympy import symbols, factor_list
    X = symbols('X')
    A = Acoef
    B = Bcoef
    p = p_field

    n2, d2 = x2_num_den(X, A, B)
    n3, d3 = x3_num_den(X, A, B)

    delta23 = (T2 - T3) % p
    # Build: n2/d2 - n3/d3 - delta23 == 0  =>  n2*d3 - n3*d2 - delta23*d2*d3 == 0
    F = (n2*d3 - n3*d2 - delta23*(d2*d3))
    P = mod_poly(F, p)
    # Factor over GF(p)
    facs = factor_list(P, modulus=p)
    roots = []
    for (fac, exp) in facs[1]:
        if fac.degree() == 1:
            # linear factor a*X + b => root = -b/a
            a = fac.all_coeffs()[0] % p
            b = fac.all_coeffs()[1] % p
            if a % p == 0:
                continue
            root = (-b * inv_mod(a, p)) % p
            roots.append(root)

    if not roots:
        raise RuntimeError("No candidate roots for Kx found")

    # Evaluate rational functions numerically for verification
    def x2_eval(x):
        num = (pow(x,4,p) - (2*A)%p * pow(x,2,p) - (8*B)%p * x % p + (A*A)%p) % p
        den = (4*pow(x,3,p) + (4*A)%p * x % p + (4*B)%p) % p
        if den == 0:
            return None
        return (num * inv_mod(den, p)) % p

    def x3_eval(x):
        psi3 = (3*pow(x,4,p) + (6*A)%p * pow(x,2,p) + (12*B)%p * x % p - (A*A)%p) % p
        num = (x * pow(psi3,2,p) - (8 * ( (pow(x,3,p) + (A*x)%p + B) % p ) * ( (pow(x,6,p) + (5*A)%p * pow(x,4,p) + (20*B)%p * pow(x,3,p) - (5*pow(A,2,p))%p * pow(x,2,p) - (4*A*B)%p * x % p - (8*pow(B,2,p))%p - pow(A,3,p)) % p ) ) ) % p
        den = pow(psi3,2,p)
        if den == 0:
            return None
        return (num * inv_mod(den, p)) % p

    # Optionally x5 for extra check: compute via group law using y sqrt
    def is_quadratic_residue(v):
        return pow(v, (p-1)//2, p) != p-1

    def sqrt_mod(v):
        # Tonelli-Shanks generic sqrt mod prime
        if v == 0:
            return 0
        if p % 4 == 3:
            return pow(v, (p+1)//4, p)
        # Factor p-1 = q*2^s
        q = p-1; s = 0
        while q % 2 == 0:
            q //= 2; s += 1
        z = 2
        while pow(z, (p-1)//2, p) != p-1:
            z += 1
        c = pow(z, q, p)
        x = pow(v, (q+1)//2, p)
        t = pow(v, q, p)
        m = s
        while t != 1:
            i = 1
            tt = (t*t) % p
            while tt != 1:
                tt = (tt*tt) % p
                i += 1
            b = pow(c, 1 << (m - i - 1), p)
            x = (x*b) % p
            c = (b*b) % p
            t = (t*c) % p
            m = i
        return x

    def ff_add(P1, P2):
        if P1 is None:
            return P2
        if P2 is None:
            return P1
        x1,y1 = P1; x2,y2 = P2
        if x1 == x2 and (y1 + y2) % p == 0:
            return None
        if P1 == P2:
            s = (3*x1*x1 + A) * inv_mod((2*y1) % p, p) % p
        else:
            s = (y2 - y1) * inv_mod((x2 - x1) % p, p) % p
        x3 = (s*s - x1 - x2) % p
        y3 = (s*(x1 - x3) - y1) % p
        return (x3, y3)

    def ff_mul(k, P_):
        if k == 0 or P_ is None:
            return None
        Q = None; A_ = P_
        kk = k
        while kk:
            if kk & 1:
                Q = ff_add(Q, A_)
            A_ = ff_add(A_, A_)
            kk >>= 1
        return Q

    for x0 in roots:
        x2 = x2_eval(x0)
        x3 = x3_eval(x0)
        if x2 is None or x3 is None:
            continue
        r = (T2 - x2) % p
        if (x3 + r) % p != T3:
            continue
        # Optional 5P check via group law
        # Recover y from x0
        rhs = (pow(x0,3,p) + (A*x0)%p + B) % p
        if not is_quadratic_residue(rhs):
            # Not a valid point
            continue
        y0 = sqrt_mod(rhs)
        P0 = (x0, y0)
        P5 = ff_mul(5, P0)
        if P5 is None:
            continue
        if (P5[0] + r) % p != T5:
            # Try opposite sign
            P0m = (x0, (-y0) % p)
            P5m = ff_mul(5, P0m)
            if P5m is None or (P5m[0] + r) % p != T5:
                continue
        # Success
        return x0, r

    raise RuntimeError("No (Kx,r) candidate satisfied all checks")

# ---------- Orchestration ----------

def collect_header_and_menu(r: Remote) -> List[str]:
    lines = []
    # Read some lines including Qx/Qy/d_masked and menu
    for _ in range(10):
        line = r.recv_line()
        if not line:
            break
        lines.append(line)
        if line.strip() == ">":
            break
    if not any(l.strip() == ">" for l in lines):
        data = r.recv_until(b"> ")
        for l in data.decode(errors='ignore').splitlines():
            lines.append(l+"\n")
    return lines

def parse_header(lines: List[str]):
    Qx = Qy = d_masked = None
    for l in lines:
        s = l.strip()
        if s.startswith("Qx="):
            Qx = parse_int_hexline(s, "Qx")
        elif s.startswith("Qy="):
            Qy = parse_int_hexline(s, "Qy")
        elif s.startswith("d_masked="):
            d_masked = parse_int_hexline(s, "d_masked")
    if Qx is None or Qy is None or d_masked is None:
        raise RuntimeError("Failed to parse header")
    return Qx, Qy, d_masked

def get_dataset(r: Remote) -> List[Tuple[int,int,int]]:
    r.send_line("1")
    rows = []
    while True:
        line = r.recv_line()
        if not line:
            break
        s = line.strip()
        if s == ">":
            break
        parts = s.split()
        if len(parts) == 3 and parts[0].isdigit():
            i = int(parts[0]); a = int(parts[1]); y = int(parts[2])
            rows.append((i,a,y))
    return rows

def get_signature(r: Remote, msg_hex: str):
    r.send_line("2")
    r.recv_until(b"message: ")
    r.send_line(msg_hex)
    z = r_ = s_ = k_masked = None
    while True:
        line = r.recv_line()
        if not line:
            break
        s = line.strip()
        if s.startswith("z="):
            z = int(s.split("=",1)[1])
        elif s.startswith("r="):
            r_ = int(s.split("=",1)[1])
        elif s.startswith("s="):
            s_ = int(s.split("=",1)[1])
        elif s.startswith("k_masked="):
            k_masked = int(s.split("=",1)[1], 16)
        elif s == ">":
            break
    if None in (z, r_, s_, k_masked):
        raise RuntimeError("Failed to parse signature")
    return z, r_, s_, k_masked

def get_ciphertext(r: Remote) -> bytes:
    r.send_line("3")
    ct = None
    while True:
        line = r.recv_line()
        if not line:
            break
        s = line.strip()
        if s.startswith("ct=0x"):
            ct = bytes.fromhex(s.split("=0x",1)[1])
        elif s == ">":
            break
    if ct is None:
        raise RuntimeError("Failed to get ciphertext")
    return ct

def main():
    print("[*] Connecting to remote (TLS first)...")
    # Try TLS first, then fallback to raw if header parsing fails
    r = Remote(HOST, PORT, use_tls=True)
    try:
        lines = collect_header_and_menu(r)
        Qx, Qy, d_masked = parse_header(lines)
    except Exception:
        print("[!] TLS parse failed, retrying with raw TCP...")
        r = Remote(HOST, PORT, use_tls=False)
        lines = collect_header_and_menu(r)
        Qx, Qy, d_masked = parse_header(lines)
    print(f"[+] Header parsed; d_masked={d_masked:#x}")

    print("[*] Fetching dataset...")
    dataset = get_dataset(r)
    print(f"[+] Rows: {len(dataset)}")

    print("[*] Collecting signatures...")
    samples = []
    for i in range(16):
        z, rr, ss, km = get_signature(r, f"{i:02x}")
        samples.append((z, rr, ss, km))
    print("[+] Signatures collected")

    print("[*] Fetching ciphertext...")
    ct = get_ciphertext(r)
    print(f"[+] Ciphertext len: {len(ct)}")

    print("[*] Solving for d with Z3...")
    d = recover_d_with_z3(samples)
    print(f"[+] d = 0x{d:064x}")

    print("[*] Deriving MK and inverting dataset...")
    MK = compute_MK(d)
    T = derive_t_values(dataset, MK)  # a -> T_a
    T2, T3, T5 = T[2], T[3], T[5]
    print(f"[+] T2,T3,T5 recovered")

    print("[*] Solving for (Kx, r)...")
    Kx, r_val = solve_for_Kx_and_r(T2, T3, T5)
    print(f"[+] Kx={Kx}, r={r_val}")

    print("[*] Decrypting flag...")
    ks = hashlib.shake_128(str((Kx, r_val)).encode()).digest(len(ct))
    flag = bytes(x ^ y for x,y in zip(ks, ct))
    try:
        print("[+] FLAG:", flag.decode())
    except Exception:
        print("[+] FLAG bytes:", flag)

    r.send_line("4")
    r.close()

if __name__ == "__main__":
    main()
