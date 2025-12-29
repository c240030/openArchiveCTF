from sage.all import *

n = 1235393610183688281665008071050170789586638192838138095986995296192782436457223668715676980459520352486540470004240180459371942782355070514708905391835197905107484915168701596111088569166004910043574218885071720178537189787619111569408113904672772854692718870814429737810408622828534631477433546852600373169909001977669017340918457104419136273188804515767629713472072288600818628376083517382373065731781865195101755630654681152414835350489971881833448717188942091
x = 300999545725924100172193739549794808534488865804908645351653561611741560383084470154769918578490716482737510914870142610490892321428365516163420218866145631042071581572793416667320615435096665691009513065949781000570895333946252018472083100906690827171945705495342066125754801748423029664543721273381224868003380464226810196962227243543681186462616532944655725118199405935344561298615015829636254961948459530505742778588365626510083559328283530838607375406679603
e = 684493310438523562625193317194826784976075337014012240866981326572393268716090450596339472546811543652148747905604341573879943835614401443781968339360436103317524703592011569498797196741010679024533815615265893690255837352971582775034399040927755118828546583453618819566360778246774030221213416345681420508037313779968851091639343434376050568765635852554462330505059103569458386027241681489423310284975425544986381725769285636879031906068024562922534306783459120728580060616091734712010188071235659323940012062215742706288100214865245604374722340836114310998674617532338541327331122117726336703381675096366955027319027296252153523554891591701367652596568745503664539724714181253324038321311333205604636135941491796622612373121367631441890363382784746903771429535821177781611281894462340775766926885431622402025604928761442702816013875642683793139303557959235333533967033184673133609437918914194742604655750459379319541612013
C = (69272578566369127397656541088861926936240597261108163176012675802901498322586712145419512855479750192014704175962618189145538265937020719738286102605390332742549406573117540177938455694288389040621015541980825426474986705926477388804168806218577673125351014863818455365500526291604142369629890129125419466744882658811492513923135812372014903153621333137382445645230873646662026824175321590713964712352464848217359827854687687196999289046650994582377780596697419, 1093002213031725454053444022374781346792817037681092732083686138927821980664876306295732369507596781751148647758693430833150274545941361456387404227347542540432731750265514788865023885820335370642734386657542840137476788557946390436380263016281258811477486812987160474747983385403611186959879066306187473162349611498371628436234782451061900915338463254351576897433573620661322287681499979212841593557189058976121042389968295870236303960305804392482720529574979463, 437229762039382396503661315116674730090219261873638392503563536339154743310093703666894322465802239395273835915127158858656830350951811720231808521481196631637300158604163901655511581543053295697591823042128390892798069046841689972143200046002248546597737847201205980702146290525238539332393132497064517491736582639630282278098426879113343580775456092897558327327775258703265339370876080876687455978082462803119618208197347631116966938861131923079948651369448211)

def long_to_bytes(val):
    return int(val).to_bytes((int(val).bit_length() + 7) // 8, 'big')

def solve_wiener(e, n):
    print(f"[*] Running Wiener's attack with e ~ {int(e).bit_length()} bits...")
    lst = continued_fraction(Integer(e) / Integer(n)**2)
    conv = lst.convergents()

    for c in conv:
        k = int(c.numerator())
        d = int(c.denominator())
        if k == 0 or d == 0: continue

        if d < 1000: continue

        if (e * d - 1) % k == 0:
            phi_cand = (e * d - 1) // k
            if phi_cand.bit_length() > int(n).bit_length():
                return d
    return None

def factor_n(n, d, e):
    print("[*] Factoring n...")
    k_phi = e * d - 1
    g = 2
    while True:
        t = k_phi
        while t % 2 == 0:
            t //= 2
            x_val = power_mod(g, t, n)
            if x_val != 1 and x_val != n - 1:
                p_cand = gcd(x_val - 1, n)
                if 1 < p_cand < n:
                    base = p_cand
                    if base.is_perfect_power():
                        base = base.perfect_power()[0]
                    if n % base == 0:
                        p = base
                        q_part = n // p
                        while q_part % p == 0: q_part //= p
                        q = q_part.perfect_power()[0] if q_part.is_perfect_power() else q_part
                        return p, q
        g = next_prime(g)

def ADD(A, B, n, y):
    a, b, c = A
    d, e_val, f = B
    u = (a * d + y * (b * f + e_val * c)) % n
    v = (a * e_val + b * d + y * c * f) % n
    w = (b * e_val + a * f + c * d) % n
    return (u, v, w)

def DOUBLE(A, n, y):
    a, b, c = A
    u = (a ** 2 + 2 * y * b * c) % n
    v = (2 * a * b + y * c ** 2) % n
    w = (b ** 2 + 2 * a * c) % n
    return (u, v, w)

def RING_POW(A, exp, n, y):
    res = (1, 0, 0)
    base = A
    for bit in bin(exp)[2:][::-1]:
        if bit == '1':
            res = ADD(res, base, n, y)
        base = DOUBLE(base, n, y)
    return res

def solve_system_robust(p, x_val, Enc_vals):
    print("[*] Solving system of equations (Stacked Ring version)...")
    X_dec, Y_dec, Z_dec = Enc_vals
    Fp = GF(p)

    Rv = Fp['v']
    v = Rv.gen()

    Ruv = Rv['u']
    u = Ruv.gen()

    w = Fp(1)
    x_fp = Fp(x_val)
    X, Y, Z = Fp(X_dec), Fp(Y_dec), Fp(Z_dec)

    a = u**3 + 2*x_fp**2*u*(v**2 + x_fp*v*w + x_fp**2*w**2) + x_fp**4*v*w*(v + x_fp*w)
    b = x_fp**2*v**3 + 2*v*(u**2 + x_fp**2*u*w + x_fp**4*w**2) + x_fp*u*w*(u + x_fp**2*w)
    c = x_fp**5*w**3 + 2*x_fp*w*(u**2 + x_fp*u*v + x_fp**2*v**2) + u*v*(u + x_fp*v)

    eq1 = Y * a - X * b
    eq2 = Z * x_fp * a - X * c

    print("[*] Computing Resultant to eliminate variable u...")
    res_v = eq1.resultant(eq2)

    if res_v.is_zero():
        print("[-] Resultant = 0. Method failed.")
        return []

    print(f"[*] Finding roots for polynomial of degree {res_v.degree()} in variable v...")
    roots_v = res_v.roots()
    print(f"[+] Found {len(roots_v)} potential v values.")

    solutions = []
    Ru_final = Fp['u_final']
    u_gen = Ru_final.gen()

    for val_v, _ in roots_v:
        def evaluate_poly_at_v(poly_in_Ruv, val):
            coeffs = poly_in_Ruv.list()
            return sum(c(val) * u_gen**i for i, c in enumerate(coeffs))

        poly_u1 = evaluate_poly_at_v(eq1, val_v)
        poly_u2 = evaluate_poly_at_v(eq2, val_v)

        common_u = poly_u1.gcd(poly_u2)

        if common_u.degree() > 0:
            roots_u = common_u.roots()
            for val_u, _ in roots_u:
                solutions.append((val_u, val_v))

    return solutions

def solve():
    if '...' in str(n):
        print("ERROR: Please fill in n, x, e, C values!")
        return

    d = solve_wiener(e, n)
    if not d: return
    print(f"[+] d = {d}")

    factors = factor_n(n, d, e)
    if not factors: return
    p, q = factors
    print(f"[+] p = {p}")

    y = pow(x, 3, n)
    print("[*] Decrypting Ring...")
    Decoded = RING_POW(C, d, n, y)

    sols = solve_system_robust(p, x, Decoded)

    print(f"[*] Found {len(sols)} solution pairs (u, v).")
    for u_val, v_val in sols:
        m1, m2 = Integer(u_val), Integer(v_val)
        m_str = str(m1) + str(m2)
        try:
            flag = long_to_bytes(int(m_str))
            print(f"\n[?] Decoded Hex: {flag.hex()}")
            print(f"[?] Decoded Text: {flag}")
            if b'flag' in flag or b'Seknipel' in flag:
                print("\n[SUCCESS] FLAG FOUND!")
                break
        except:
            continue

if __name__ == '__main__':
    solve()
