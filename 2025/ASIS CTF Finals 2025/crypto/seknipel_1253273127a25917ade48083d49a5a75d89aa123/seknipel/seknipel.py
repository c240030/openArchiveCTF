#!/usr/bin/env python3

from Crypto.Util.number import *
from decimal import Decimal, getcontext
from flag import flag
getcontext().prec = 72

def keygen(nbit):
	while True:
		p, q = [getPrime(nbit) for _ in ';)']
		phi = (p - 1) * (q - 1)
		d = getRandomNBitInteger(nbit >> 2)
		if p % 3 == q % 3 == 1:
			if GCD(d, phi) == 1:
				break
	u, v = [getRandomRange(1, 3) for _ in ':)']
	n = p ** u * q ** v
	x = getRandomRange(1, n)
	y = pow(x, 3, n)
	D = int(Decimal(n) ** (Decimal(1) / Decimal(2 * u + 2 * v)))
	if d < D:
		e = inverse(d, phi ** 2 * n ** 2 // (p ** 2 * q ** 2))
	return n, x, e, d

def ADD(A, B, pkey):
	n, x, _ = pkey
	y = pow(x, 3, n)
	a, b, c = A
	d, e, f = B
	u = (a * d + y * (b * f + e * c)) % n
	v = (a * e + b * d + y * c * f) % n
	w = (b * e + a * f + c * d) % n
	return (u, v, w)

def DOUBLE(A, pkey):
	n, x, _ = pkey
	y = pow(x, 3, n)
	a, b, c = A
	u = (a ** 2 + 2 * y * b * c) % n
	v = (2 * a * b + y * c ** 2) % n
	w = (b ** 2 + 2 * a * c) % n
	return (u, v, w)

def MUL(t, A, pkey):
	B = bin(t)[2:][::-1]
	u, v, w = 1, 0, 0
	for i in range(t.bit_length() - 1, -1, -1):
		u, v, w = DOUBLE((u, v, w), pkey)
		if B[i] == '1':
			u, v, w = ADD((u, v, w), A, pkey)
	return (u, v, w)

def encode(M, pkey):
	n, x, _ = pkey
	y = pow(x, 3, n)
	m_1, m_2 = M
	u, v, w = m_1, m_2, 1
	a = (u ** 3 + 2 * x ** 2 * u * (v ** 2 + x * v * w + x ** 2 * w ** 2) + x ** 4 * v * w * (v + x * w)) % n
	b = (x ** 2 * v ** 3 + 2 * v * (u ** 2 + x ** 2 * u * w + x ** 4 * w ** 2) + x * u * w * (u + x ** 2 * w)) % n
	c = (x ** 5 * w ** 3 + 2 * x * w * (u ** 2 + x * u * v + x ** 2 * v ** 2) + u * v * (u + x * v)) % n
	r = (u ** 3 + y * v ** 3 + y ** 2 * w ** 3 - 3 * y * u * v * w) % n
	X, Y, Z = (a * inverse(r, n)) % n, (b * inverse(r, n)) % n, (c * inverse(x * r, n)) % n
	return (X, Y, Z)

def encrypt(M, pkey):
	m_1, m_2 = M
	n, x, e = pkey
	assert m_1 < n and m_2 < n
	y = pow(x, 3, n)
	X, Y, Z = encode(M, pkey)
	C = MUL(e, (X, Y, Z), pkey)
	return C

nbit = 512
n, x, e, d = keygen(nbit)
m = bytes_to_long(flag)
m_1, m_2 = int(str(m)[:len(str(m))//2]), int(str(m)[len(str(m))//2:])
C = encrypt((m_1, m_2), (n, x, e))
print(f'{n = }')
print(f'{x = }')
print(f'{e = }')
print(f'{C = }')