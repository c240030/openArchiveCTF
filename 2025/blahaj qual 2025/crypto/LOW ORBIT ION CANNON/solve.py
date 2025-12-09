from pwn import *
from Crypto.Util.number import bytes_to_long, isPrime, inverse

def solve():
    while True:
        try:
            r = remote('crypto-loic.chals.blahaj.sg', 25998)
            
            r.recvuntil(b'n = ')
            n = int(r.recvline().strip())
            r.recvuntil(b'e = ')
            e = int(r.recvline().strip())
            
            target_msg = b"winner"
            target_int = bytes_to_long(target_msg)
            
            found_idx = -1
            n_prime = -1
            
            for i in range(2048):
                candidate = n ^ (1 << i)
                if candidate % 2 == 0: continue
                if isPrime(candidate):
                    found_idx = i
                    n_prime = candidate
                    break
            
            if found_idx == -1:
                r.close()
                continue
                
            r.sendlineafter(b'> ', str(found_idx).encode())
            
            phi = n_prime - 1
            d = inverse(e, phi)
            sig_int = pow(target_int, d, n_prime)
            sig_hex = hex(sig_int)
            
            r.sendlineafter(b'> ', sig_hex.encode())
            
            r.interactive()
            break
            
        except Exception:
            try:
                r.close()
            except:
                pass
            continue

if __name__ == '__main__':
    solve()
