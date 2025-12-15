from pwn import *
from Crypto.Util.number import getPrime, inverse, GCD

p = getPrime(520)
e = 65537
while GCD(e, p - 1) != 1:
    p = getPrime(520)

conn = remote("crypto-babyrsachallenge.finals.blahaj.sg", 18700)

conn.recvuntil(b">> ")
conn.sendline(str(p).encode())

conn.recvuntil(b"c = ")
c = int(conn.recvline().strip())

d = inverse(e, p - 1)
m = pow(c % p, d, p)

conn.recvuntil(b">> ")
conn.sendline(str(m).encode())

print(conn.recvall(timeout=2).decode())
conn.close()
