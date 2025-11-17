import os, sys, secrets, hashlib
from util import *



P  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
A  = 0
B  = 7
Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
N  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# (4*pow(A,3,p) + 27*pow(B,2,p)) % p != 0
p_field= 1144001070343154634288961
Acoef= 272144002963733033258483
Bcoef= 454511900449591275020144

FLAG = os.getenv("FLAG", "flag{local_debug}")
dHoles= [(0, 16), (28, 24), (96, 32), (164, 16)]
kHoles= [(36, 24), (140, 24)]
boundb= (1<<16) - 1
n= 900
A_SET= (2,3,5)

def main():
    d = (secrets.randbits(256) % (N-1)) + 1
    Q = ec_mul(d, (Gx, Gy), N, P, A)
    d_masked = bits_clear_windows(d, dHoles)

    P0 = ff_random_point(p_field, Acoef, Bcoef)
    s = (secrets.randbits(128) | 1)
    Kp = ff_mul(s, P0, p_field, Acoef, Bcoef)
    r = secrets.randbelow(p_field)

    MK = HKDF(hashlib.sha256(d.to_bytes(32,'big')).digest(), b"mk", 32)

    rows = []
    for i in range(n):
        a = A_SET[secrets.randbelow(len(A_SET))]
        Pa = ff_mul(a, Kp, p_field, Acoef, Bcoef)
        t = (Pa[0] + r) % p_field

        seed = i.to_bytes(4,'big')
        raw = HKDF(MK, b"M|" + seed, 96)

        lam = (int.from_bytes(raw[:32],'big') % p_field) or 1
        mu  =  int.from_bytes(raw[32:64],'big') % p_field
        nu  = (int.from_bytes(raw[64:],'big') % p_field) or 1
        
        y0 = mobius_apply(lam, mu, nu, t, p_field)
        ctr = 1

        while y0 is None:
            raw = HKDF(MK, b"M|" + seed + ctr.to_bytes(2,'big'), 96)
            lam = (int.from_bytes(raw[:32],'big') % p_field) or 1
            mu  =  int.from_bytes(raw[32:64],'big') % p_field
            nu  = (int.from_bytes(raw[64:],'big') % p_field) or 1
            y0 = mobius_apply(lam, mu, nu, t, p_field)
            ctr += 1

        braw = HKDF(MK, b"b|" + seed, 16)
        beta = (int.from_bytes(braw,'big') % (2*boundb+1)) - boundb
        y = (y0 + beta) % p_field
        rows.append((a, y))

    ks = hashlib.shake_128(str((Kp[0], r)).encode()).digest(len(FLAG))
    ctxt = bytes(x ^ y for x,y in zip(ks, FLAG.encode()))

    print(f"Qx=0x{Q[0]:064x}")
    print(f"Qy=0x{Q[1]:064x}")
    print(f"d_masked=0x{d_masked:064x}")
    
    
    
    menu="""
    1. dataset
    2. sign a message
    3. flag 
    4. exit
    """
    print(menu)

    sig_idx = 0
    sig_asked=0
    
    while True:
        _in=input("> ").strip()
        if _in == "1":
            for i,(a,y) in enumerate(rows):
                print(f"{i} {a} {y}")
            continue
        if _in == "2":
            
            if sig_asked>15:
                print("no more hehe")
                continue
            m = parse_msg_bytes(input("message: "))
            z = sha256_int(m) % N
            k = (secrets.randbits(256) % (N-1)) + 1
            R = ec_mul(k, (Gx, Gy), N, P, A)
            r_ = R[0] % N
          

            while r_ == 0:
                k = (secrets.randbits(256) % (N-1)) + 1
                R = ec_mul(k, (Gx, Gy), N, P, A)
                r_ = R[0] % N
            s_ = (inv_mod(k, N) * (z + r_*d)) % N
            if s_ == 0: print("retry"); continue

            k_masked = bits_clear_windows(k, kHoles)
            
            print(f"ticket#{sig_idx}")
            print(f"z={z}")
            print(f"r={r_}")
            print(f"s={s_}")
            print(f"k_masked=0x{k_masked:064x}")
            sig_idx += 1
            sig_asked+=1
            continue
        
        if _in == "3":
            print(f"ct=0x{ctxt.hex()}")
            continue
        if _in == "4":
            print("bye, I will miss you")
            break

if __name__ == "__main__":
    main()
