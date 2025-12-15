from pwn import *
from Crypto.Hash import TupleHash128
from Crypto.Random.random import randrange

KEY_SIZE = 2048
HASH_BITS = 128
MOD = 2**HASH_BITS

def compute_hash(A0, B0, A1, B1):
    h = TupleHash128.new(digest_bytes=HASH_BITS // 8)
    for item in [A0, B0, A1, B1]:
        h.update(item.to_bytes(KEY_SIZE // 8, 'big'))
    return int.from_bytes(h.digest(), 'big')

def solve():
    r = remote('crypto-election.finals.blahaj.sg', 26742)
    
    r.recvuntil(b'p = ')
    p = int(r.recvline().strip(), 16)
    r.recvuntil(b'q = ')
    q = int(r.recvline().strip(), 16)
    r.recvuntil(b'g = ')
    g = int(r.recvline().strip(), 16)
    r.recvuntil(b'y = ')
    y = int(r.recvline().strip(), 16)
    
    r.recvuntil(b'Now cast your vote!')
    
    vote_value = 40
    rand_r = randrange(1, q)
    R = pow(g, rand_r, p)
    S = (pow(y, rand_r, p) * pow(g, vote_value, p)) % p
    
    f0 = randrange(1, q)
    f1 = randrange(1, q)
    
    A0 = pow(g, f0, p)
    B0 = pow(y, f0, p)
    A1 = pow(g, f1, p)
    B1 = pow(y, f1, p)
    
    challenge = compute_hash(A0, B0, A1, B1)
    
    q_inv = pow(q, -1, MOD)
    d = (challenge * q_inv) % MOD
    
    c0 = 0
    c1 = d * q
    
    r.sendlineafter(b'R: ', hex(R)[2:].encode())
    r.sendlineafter(b'S: ', hex(S)[2:].encode())
    r.sendlineafter(b'c0: ', hex(c0)[2:].encode())
    r.sendlineafter(b'c1: ', hex(c1)[2:].encode())
    r.sendlineafter(b'f0: ', hex(f0)[2:].encode())
    r.sendlineafter(b'f1: ', hex(f1)[2:].encode())
    
    r.interactive()

if __name__ == '__main__':
    solve()
