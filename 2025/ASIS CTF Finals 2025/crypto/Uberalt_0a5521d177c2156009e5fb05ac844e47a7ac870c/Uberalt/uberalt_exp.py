#!/usr/bin/env sage

## Uberalt Crypto task writeup - ASIS CTF Final 2025
# factoreal@asis.sh

import re
import socket
import time
import base64
from sage.all import *

host = "127.0.0.1"
port = 12400
zzz = 0.2


def lll_factor(low_bits, low_bits_size, n):
	"""
	break RSA when we have low bits of p
	Solve x for low_bits+x*(1<<low_bits_size) = 0 (mod p)
	"""
	pp = (low_bits * int(inverse_mod(1 << low_bits_size, n))) % n
	max_x = 1 << ceil(int(n).bit_length() / 2 - low_bits_size)

	L = Matrix(
		ZZ,
		[
			[max_x**2, pp * max_x, 0],
			[0, max_x, pp],
			[0, 0, n],
		],
	)
	L = L.LLL()

	f2 = L[0][0] // (max_x**2)
	f1 = L[0][1] // max_x
	f0 = L[0][2]

	x = var("x")
	sols = (f0 + f1 * x + f2 * x**2).roots(ring=ZZ)

	if len(sols) == 0:
		return None
	p = int(sols[0][0] * (1 << low_bits_size) + low_bits)

	if n % p != 0:
		return None
	return p % n


SIMILAR_BITS_NUM = 400
MAX_NEXT_PRIME_ERRO_BITS_NUM = 10

f = Zmod(2**SIMILAR_BITS_NUM)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
	sock.connect((host, port))
	pos_e = int(time.time())
	time.sleep(zzz * 10)
	data = sock.recv(1 << 12).decode()
	print(data)
	# these are found by bruteforce in debug mode,.., there are much more!
	while True:
		for r in [
			9223372036854782774,
			9223372036854791838,
			9223372036854787812,
			9223372036854781344,
		]:
			pos_e = int(time.time())

			sock.sendall("r\n".encode())
			sock.sendall(f"{r}\n".encode())
			time.sleep(zzz)
			data = sock.recv(1 << 12).decode()
			matches = re.search(r"enc = (.+)\n", data)
			c = int.from_bytes(base64.b64decode(matches.group(1)), "big")
			# print(data)

			sock.sendall("g\n".encode())
			time.sleep(zzz)
			data = sock.recv(1 << 12).decode()
			matches = re.search(r"n = (\d+)", data)
			n = int(matches.group(1))
			poss_p_q = set()
			for next_prime_error in range(1 << MAX_NEXT_PRIME_ERRO_BITS_NUM):
				try:
					m_sol = (f(n) + f(next_prime_error) ** 2).nth_root(2)
				except ValueError:
					continue
				for m in [m_sol, -m_sol]:
					# solutions can be many, but we try several easy ones and trust to repeat:)
					pos_p, pos_q = int(m + next_prime_error), int(m - next_prime_error)
					if f(n) == f(pos_p * pos_q):
						# so far, we can just check it in mod 2**SIMILAR_BITS_NUM
						poss_p_q.add((min(pos_p, pos_q), max(pos_p, pos_q)))
			# print(poss_p_q)
			for pos_p, pos_q in poss_p_q:
				print(f"checking {pos_p=} {pos_q=} by LLL")
				res = lll_factor(pos_p, SIMILAR_BITS_NUM, n)
				if res is not None and n % res == 0:
					p, q = res, n // res
					print(f"{p=}")
					print(f"{q=}")
					print(f"{c=}")
					print(f"{pos_e=}")
					assert p * q == n
					for e in range(pos_e - 8, pos_e + 8):
						try:
							sec = pow(c, pow(e, -1, (p - 1) * (q - 1)), n)
						except Exception:
							continue
						print(f"{e=}")
						print(f"{sec=}")
						# sometimes, e can be not comprime to phi, so repeat is golden solution to find flag!
						try:
							sec = sec.to_bytes(128, "big").lstrip(b"\x00").decode()
						except Exception:
							continue
						printable = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
						if not all(char in printable for char in sec):
							continue

						print(f"{sec=}")
						sock.sendall("s\n".encode())
						time.sleep(zzz)
						data = sock.recv(1 << 12).decode()
						sock.sendall(f"{sec}\n".encode())
						time.sleep(zzz)
						data = sock.recv(1 << 12).decode()
						print(data)
						exit()
