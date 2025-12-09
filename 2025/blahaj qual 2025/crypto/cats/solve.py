from pwn import *

host = 'crypto-cats.chals.blahaj.sg'
port = 30513

def solve():
    r = remote(host, port)
    val = 2**130

    for _ in range(5):
        r.recvuntil(b'\xf0\x9f\x90\xb1 = ')
        r.recvline()
        
        r.sendlineafter(b'= ', str(val).encode())
        r.sendlineafter(b'= ', str(-val).encode())
        r.sendlineafter(b'= ', str(val).encode())

    r.interactive()

if __name__ == '__main__':
    solve()