from Crypto.Util.number import bytes_to_long, long_to_bytes

P = 4294967311
F = GF(P)
R.<x> = F[]

N_str = "67256387*x^16 + 3785639081*x^15 + 2243704320*x^14 + 2510382192*x^13 + 1559187120*x^12 + 1523961994*x^11 + 2440248838*x^10 + 764754967*x^9 + 4190435294*x^8 + 4065822583*x^7 + 1057162888*x^6 + 4235943041*x^5 + 988301557*x^4 + 3205679312*x^3 + 4147841349*x^2 + 2991402492*x + 493401902"
c_str = "1716040029*x^15 + 1696954190*x^14 + 4053818925*x^13 + 1939649983*x^12 + 2138498341*x^11 + 1570315003*x^10 + 1612601010*x^9 + 2438663461*x^8 + 979049063*x^7 + 1638778176*x^6 + 2539855018*x^5 + 3011253693*x^4 + 74288680*x^3 + 3575879293*x^2 + 390800087*x + 2221336254"
e = 65537

def parse_poly(poly_str):
    terms = poly_str.split(' + ')
    poly = R(0)
    for term in terms:
        if 'x^' in term:
            coeff, exp = term.split('*x^')
            poly += int(coeff) * (x^int(exp))
        elif 'x' in term:
            coeff, _ = term.split('*x')
            poly += int(coeff) * x
        else:
            poly += int(term)
    return poly

N = parse_poly(N_str)
c = parse_poly(c_str)

print("[*] Factoring N...")
factors = N.factor()
print(f"[*] Factors: {factors}")

group_orders = []
for f, exponent in factors:
    if f.degree() > 0:
        group_orders.append(P^f.degree() - 1)

L = LCM(group_orders)
d = inverse_mod(e, L)
print(f"[*] Calculated private exponent d")

r = pow(c, d, N)

m0_known = bytes_to_long(b"blah")
r0 = r(0)
n0 = N(0)

k = (F(m0_known) - F(r0)) / F(n0)
k = Integer(k)
print(f"[*] Recovered k: {k}")

m = r + k * N

m_coeffs = m.list()
flag = b""

for i in range(17):
    val = int(m_coeffs[i])
    if i == 16:
        flag += long_to_bytes(val).rjust(2, b'\x00')
    else:
        flag += long_to_bytes(val).rjust(4, b'\x00')

print(f"[*] Flag: {flag.decode()}")
