#!/usr/bin/env python3
from pwn import *
from Crypto.Util.number import *
import sys
import time

sys.set_int_max_str_digits(100000)
context.log_level = 'info'

def iroot(n, k):
    if n < 0: return None
    if n == 0: return 0
    if k == 1: return n
    low = 1
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

def fast_attack(N, e, k):
    log.info(f"Running EEA Attack for k={k}...")
    
    A = pow(N, k) + 1
    M = e
    
    r0, t0 = M, 0
    r1, t1 = A, 1
    
    steps = 0
    max_steps = 30000 
    
    start_time = time.time()
    
    while r1 > 0 and steps < max_steps:
        steps += 1
        if steps % 5000 == 0:
            print(f"[*] Step {steps}...", end="\r")

        curr_j = abs(t1)
        curr_val = abs(r1)
        
        if curr_j > 0:
            Sk_est = curr_val // curr_j
            sk_bits = Sk_est.bit_length()
            target_bits = (N.bit_length() * k) // 2
            
            if abs(sk_bits - target_bits) < 10:
                for diff in range(-100, 101):
                    Sk = Sk_est + diff
                    if Sk.bit_length() < target_bits: continue
                    
                    roots = solve_quadratic(1, -Sk, pow(N, k))
                    if roots:
                        pk, qk = roots
                        if pk > 1 and qk > 1:
                            p = iroot(pk, k)
                            q = iroot(qk, k)
                            if p and q and p * q == N:
                                return p, q
        
        quotient = r0 // r1
        r0, r1 = r1, r0 - quotient * r1
        t0, t1 = t1, t0 - quotient * t1
    
    print("")
    return None

def main():
    while True:
        r = None
        try:
            r = remote('65.109.214.93', 13137)
            
            r.recvuntil(b'[Q]uit')
            r.sendline(b'e')
            r.recvuntil(b'enc = ')
            line = r.recvline().strip()
            if not line:
                r.close()
                continue
            enc = int(line)
            
            r.recvuntil(b'[Q]uit')
            r.sendline(b'p')
            r.recvuntil(b'N = ')
            N = int(r.recvline().strip())
            r.recvuntil(b'e = ')
            e_val = int(r.recvline().strip())
            
            n_len = N.bit_length()
            e_len = e_val.bit_length()
            k = int(round(e_len / n_len))
            
            log.info(f"Connected. Params: N={n_len}bits, k={k}")
            
            if k < 4:
                log.warning(f"k={k} < 4 (too hard/slow). Skip & Retry...")
                r.close()
                continue
            
            result = fast_attack(N, e_val, k)
            
            if result:
                p, q = result
                log.success("FOUND FACTORS p, q!")
                
                phi = (p - 1) * (q - 1)
                d_rsa = inverse(e_val, phi)
                m_int = pow(enc, d_rsa, N)
                
                try:
                    msg = long_to_bytes(m_int).decode()
                    log.success(f"Secret: {msg}")
                    
                    r.recvuntil(b'[Q]uit')
                    r.sendline(b's')
                    r.recvuntil(b'secret message: ')
                    r.sendline(msg.encode())
                    
                    flag = r.recvall(timeout=5).decode()
                    print("\n" + "="*60)
                    print(flag.strip())
                    print("="*60 + "\n")
                    r.close()
                    sys.exit(0)
                except Exception as e:
                    log.error(f"Decode failed: {e}")
                    r.close()
            else:
                log.failure("Attack failed (not found in EEA steps). Retrying...")
                r.close()

        except KeyboardInterrupt:
            log.info("User interrupted.")
            if r: r.close()
            sys.exit(0)
        except Exception as e:
            log.warning(f"Network/Error: {e}. Retrying...")
            try: r.close()
            except: pass

if __name__ == "__main__":
    main()