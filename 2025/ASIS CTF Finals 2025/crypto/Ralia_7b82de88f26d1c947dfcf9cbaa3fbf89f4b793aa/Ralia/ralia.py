#!/usr/bin/env python3

import sys
from Crypto.Util.number import *
from random import *
from secret import flag

def die(*args):
	pr(*args)
	quit()
	
def pr(*args):
	s = " ".join(map(str, args))
	sys.stdout.write(s + "\n")
	sys.stdout.flush()

def sc(): 
	return sys.stdin.buffer.readline()

# def is_persquat(n):
# 	if n == 1: return True
# 	a, b = 1 << 1, n >> 1
# 	while a <= b:
# 		c = (a + b) >> 1
# 		if n % c == 0 and abs(n/c - c)<1e-2: return True
# 		a, b = (a, c + 1)[c > n/c], (c - 1, b)[c < n/c]
# 	return False

def is_persquat(n):
	if n == 1: return True
	l, r = 2, n // 2
	while l <= r:
		m = (l + r) // 2
		s = m * m
		if s == n: return True
		elif s < n: l = m + 1
		else: r = m - 1
	return False

def main():
	border = "┃"
	pr(        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
	pr(border, ".::               Welcome to Ralia weird machine!             ::. ", border)
	pr(border, " You should send the correct answer in each step to get flag! :-) ", border)
	pr(        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
	step = 19
	for level in range(1, step + 1):
		bitel = randint(19 + level * 14 + step, 40 + level * 14 + step)
		pr(border, f'Please send the answer of level {level} and bitel = {bitel}: ')
		ans = sc().decode().strip().split(',')
		try:
			x, y, z = [abs(int(_)) for _ in ans]
		except:
			die(border, f"The input you provided is not valid!")
		_b = False
		if is_persquat(x + y) and is_persquat(y + z + 1) and is_persquat(z + x + 5):
			if isPrime(x) and isPrime(z):
				if x.bit_length() == y.bit_length() == z.bit_length() == bitel:
					_b = True
		if _b:
			if level == step:
				die(border, f'Congratz! You got the flag: {flag}')
			else:
				pr(border, f'Good job, please try level {level + 1}!')
		else:
			die(border, 'Wrong, No way to proceed more step. Sorry!!')

if __name__ == '__main__':
	main()