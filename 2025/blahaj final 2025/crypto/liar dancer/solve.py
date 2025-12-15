from pwn import *
from sympy import isprime, discrete_log, primerange, n_order
from sympy.ntheory.modular import crt
import random
import sys
import multiprocessing
import time

sys.set_int_max_str_digits(100000)

NUM_CORES = multiprocessing.cpu_count()
TARGET_COUNT = 10
K_BITS = 60 

def search_worker(args):
    worker_id, primes_list = args
    random.seed(time.time() + worker_id)
    
    while True:
        k = 1
        while k.bit_length() < K_BITS - 5:
            k *= random.choice(primes_list)
        while k.bit_length() < K_BITS:
            k *= random.choice(primes_list[:10])
            
        q1 = 6 * k + 1
        if not isprime(q1): continue
        q2 = 12 * k + 1
        if not isprime(q2): continue
        q3 = 18 * k + 1
        if not isprime(q3): continue
        
        Q = 36 * k**2 + 11 * k + 1
        if isprime(Q):
            return (k, q1, q2, q3)

def solve():
    smooth_primes = list(primerange(2, 301))
    
    print(f"[*] Starting parallel search on {NUM_CORES} cores...")
    
    with multiprocessing.Pool(processes=NUM_CORES) as pool:
        tasks = []
        for i in range(TARGET_COUNT):
            tasks.append(pool.apply_async(search_worker, ((i, smooth_primes),)))
        
        results = []
        while len(results) < TARGET_COUNT:
            for i, t in enumerate(tasks):
                if t and t.ready():
                    res = t.get()
                    if res:
                        results.append(res)
                        print(f"[+] Found parameter set {len(results)}/{TARGET_COUNT}")
                        tasks[i] = None
                        if len(results) + len([x for x in tasks if x is not None]) < TARGET_COUNT:
                             tasks.append(pool.apply_async(search_worker, ((len(tasks), smooth_primes),)))
            time.sleep(0.5)

    print(f"[*] Search complete. Gathered {len(results)} parameters.")

    moduli = []
    residues = []

    for idx, (k, q1, q2, q3) in enumerate(results):
        p = q1 * q2 * q3
        
        try:
            r = remote('crypto-liar-dancer.finals.blahaj.sg', 17490, level='error')
            r.recvuntil(b"p?\n> ")
            r.sendline(str(p).encode())
            
            resp = r.recvall(timeout=5).decode().strip()
            r.close()
            
            lines = resp.splitlines()
            vars_lines = [l for l in lines if '=' in l]
            
            if len(vars_lines) < 2:
                print(f"[-] Invalid response format #{idx+1}")
                continue

            a_val = int(vars_lines[0].split('=')[1].strip())
            y_val = int(vars_lines[1].split('=')[1].strip())
            
            print(f"[*] Solving DLOG for #{idx+1}...")
            
            curr_res = []
            curr_mods = []
            
            for q in [q1, q2, q3]:
                val = discrete_log(q, y_val, a_val)
                
                real_order = n_order(a_val, q)
                
                curr_res.append(val)
                curr_mods.append(real_order)
            
            crt_result = crt(curr_mods, curr_res)
            
            if crt_result is None:
                print(f"[-] Inconsistent DLOG results for #{idx+1}. Skipping.")
                continue
                
            val_crt, mod_crt = crt_result
            moduli.append(mod_crt)
            residues.append(val_crt)
            print(f"[+] Recovered partial flag mod {mod_crt}")
            
        except Exception as e:
            print(f"[-] Error processing #{idx+1}: {e}")
            continue

    if not moduli:
        print("[-] No moduli collected.")
        return

    print("[*] Reconstructing final flag...")
    full_crt = crt(moduli, residues)
    
    if full_crt is None:
        print("[-] Final CRT failed due to inconsistencies.")
        return
        
    full_val, full_mod = full_crt
    
    try:
        num_bytes = (full_val.bit_length() + 7) // 8
        flag = full_val.to_bytes(num_bytes, 'big')
        print(f"\n[+] FLAG: {flag.decode()}")
    except Exception as e:
        print(f"\n[-] Could not decode flag: {e}")
        print(f"Value: {full_val}")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    solve()