#!/usr/bin/env python3

# Solves the FaultyCurve challenge by exploiting the singular curve vulnerability.

# For compatibility with different sympy versions
try:
    from sympy.ntheory.residue_methods import sqrt_mod
except ImportError:
    from sympy.ntheory import sqrt_mod # For older sympy versions
from sympy import discrete_log

# --- Given Problem Parameters ---
p = 3059506932006842768669313045979965122802573567548630439761719809964279577239571933
a = 2448848303492708630919982332575904911263442803797664768836842024937962142592572096
Gx = 3
Qx = 1461547606525901279892022258912247705593987307619875233742411837094451720970084133

# --- Solution ---

# 1. Recover the singular point's x-coordinate (x0) and the tangent slope (m).
# For a singular curve y^2 = x^3 + ax + b, the singular point (x0, 0)
# satisfies 3*x0^2 + a = 0 mod p.
print("[*] Step 1: Recovering curve parameters...")
inv3 = pow(3, -1, p)
x0_sq = (-a * inv3) % p
x0 = sqrt_mod(x0_sq, p)

# The tangents at the node (x0, 0) have slopes m = +/-sqrt(3*x0).
m_sq = (3 * x0) % p
m = sqrt_mod(m_sq, p)

# The missing curve parameter 'b' can also be found: b = 2*x0^3 mod p.
b = (2 * pow(x0, 3, p)) % p
print(f"    - Found singular point x0: {x0}")
print(f"    - Found tangent slope m: {m}")
print(f"    - Found curve parameter b: {b}")


# 2. Recover the full coordinates of the generator G and public point Q.
# We use the full curve equation y^2 = x^3 + ax + b to find the y-coordinates.
print("\n[*] Step 2: Recovering full point coordinates...")
Gy_sq = (pow(Gx, 3, p) + a * Gx + b) % p
Gy = sqrt_mod(Gy_sq, p)

Qy_sq = (pow(Qx, 3, p) + a * Qx + b) % p
Qy = sqrt_mod(Qy_sq, p) # We pick one root; the logic below handles ambiguity.
print(f"    - Found G = ({Gx}, {Gy})")
print(f"    - Found Q = ({Qx}, {Qy})")


# 3. Apply the isomorphism to map the ECDLP to a DLP in F_p.
# The map is phi(P) = (y - m*(x-x0)) / (y + m*(x-x0)).
# This transforms Q = flag * G into beta = alpha^flag.
print("\n[*] Step 3: Applying isomorphism (Smart's Attack)...")
num_alpha = (Gy - m * (Gx - x0)) % p
den_alpha = (Gy + m * (Gx - x0)) % p
alpha = (num_alpha * pow(den_alpha, -1, p)) % p

num_beta = (Qy - m * (Qx - x0)) % p
den_beta = (Qy + m * (Qx - x0)) % p
beta = (num_beta * pow(den_beta, -1, p)) % p
print(f"    - Mapped G to alpha: {alpha}")
print(f"    - Mapped Q to beta: {beta}")


# 4. Solve the DLP and decode the flag.
# The choice of the y-coordinate for Q determines if we solve for `flag` or `-flag`.
# We try both possibilities to find the one that decodes to a valid string.
print("\n[*] Step 4: Solving DLP and decoding flag...")

# Possibility 1: Solves for `flag`
flag_int_1 = discrete_log(p, beta, alpha)

# Possibility 2: Solves for `-flag` (by using the inverse of beta)
beta_inv = pow(beta, -1, p)
flag_int_2 = discrete_log(p, beta_inv, alpha)

try:
    flag_bytes = flag_int_1.to_bytes((flag_int_1.bit_length() + 7) // 8, 'big')
    print(f"\n[+] Success! Flag: {flag_bytes.decode()}")
except UnicodeDecodeError:
    print("\n[-] First possibility failed to decode. Trying the second.")
    try:
        flag_bytes = flag_int_2.to_bytes((flag_int_2.bit_length() + 7) // 8, 'big')
        print(f"\n[+] Success! Flag: {flag_bytes.decode()}")
    except UnicodeDecodeError:
        print("\n[!] Error: Both possibilities failed to decode. Check the math.")