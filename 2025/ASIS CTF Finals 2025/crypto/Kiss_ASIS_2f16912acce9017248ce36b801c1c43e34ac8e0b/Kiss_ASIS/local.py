#!/usr/bin/env python3
import sys
import random
from Crypto.Util.number import getPrime, inverse, bytes_to_long, long_to_bytes

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def iroot(n, k):
    low = 0
    high = n
    while low < high:
        mid = (low + high + 1) // 2
        if mid ** k <= n:
            low = mid
        else:
            high = mid - 1
    return low

def solve_quadratic(a, b, c):
    delta = b*b - 4*a*c
    if delta < 0: return None
    sqrt_delta = iroot(delta, 2)
    if sqrt_delta ** 2 != delta: return None
    x1 = (-b + sqrt_delta) // (2*a)
    x2 = (-b - sqrt_delta) // (2*a)
    return x1, x2

def gaussian_reduction(v1, v2):
    def norm_sq(v): return v[0]**2 + v[1]**2
    
    while True:
        if norm_sq(v1) > norm_sq(v2):
            v1, v2 = v2, v1
        
        mu = (v2[0]*v1[0] + v2[1]*v1[1]) / norm_sq(v1)
        mu = int(round(mu))
        
        if mu == 0:
            return v1, v2
        
        v2 = [v2[0] - mu*v1[0], v2[1] - mu*v1[1]]

def attack(N, e):
    n_bits = N.bit_length()
    e_bits = e.bit_length()
    k_est = int(round(e_bits / n_bits))
    
    if k_est < 5:
        print(f"[-] k={k_est} is too small for lattice attack. Retrying...")
        return None

    print(f"[+] Estimated k = {k_est}. Attempting lattice reduction...")
    k = k_est
    
    W = 1 << (n_bits * k // 2)
    A = pow(N, k) + 1
    
    v1 = [W, A]
    v2 = [0, e]
    
    u1, u2 = gaussian_reduction(v1, v2)
    j_candidates = [abs(u1[0]) // W, abs(u2[0]) // W]
    
    for j in j_candidates:
        if j == 0: continue
        vec_y = abs(u1[1]) if j == abs(u1[0]) // W else abs(u2[1])
        
        Sk = vec_y // j
        roots = solve_quadratic(1, -Sk, pow(N, k))
        
        if roots:
            pk, qk = roots
            p = iroot(pk, k)
            q = iroot(qk, k)
            
            if p * q == N:
                print(f"[+] Found p: {p}")
                print(f"[+] Found q: {q}")
                return p, q
    
    return None

class Challenge:
    def __init__(self):
        self.flag = "ASIS{test_flag_local_123}"
        self.reinit()

    def reinit(self):
        self.D = random.uniform(0.9990, 0.9999)
        self.k = random.randint(1, 6)
        self.nbit = 1024
        self.N, self.e, self.p, self.q = self.genkey(self.nbit, self.D, self.k)
        self.rmsg = "".join([random.choice("ABCDEF0123456789") for _ in range(30)])
        self.enc = pow(bytes_to_long(self.rmsg.encode()), self.e, self.N)

    def genkey(self, nbit, D, k):
        dbit = int(nbit * D) + 1
        while True:
            p = getPrime(nbit >> 1)
            q = getPrime(nbit >> 1)
            if p % 4 == 3 and q % 4 == 3:
                N = p * q
                phi = (p ** k - 1) * (q ** k - 1)
                d = getPrime(dbit)
                r = random.randint(0, 1)
                try:
                    e = inverse(phi + (-1)**r * d, phi)
                    return N, e, p, q
                except ValueError:
                    continue

def main():
    print("--- Starting Local Solver ---")
    
    sim = Challenge()
    
    attempts = 0
    while True:
        attempts += 1
        print(f"\n[Iteration {attempts}]")
        N = sim.N
        e = sim.e
        enc = sim.enc
        
        print(f"N = {N}")
        print(f"e = {e}")
        result = attack(N, e)
        
        if result:
            p, q = result
            phi_rsa = (p - 1) * (q - 1)
            d_rsa = inverse(e, phi_rsa)
            dec_int = pow(enc, d_rsa, N)
            try:
                dec_msg = long_to_bytes(dec_int).decode()
                print(f"[+] Decrypted Secret: {dec_msg}")
                
                if dec_msg == sim.rmsg:
                    print(f"[+] SUCCESS! Flag: {sim.flag}")
                    break
            except:
                print("[-] Decryption failed (not printable).")
        
        print("[-] Attack failed or k too small. Reconnecting...")
        sim.reinit()

if __name__ == "__main__":
    main()