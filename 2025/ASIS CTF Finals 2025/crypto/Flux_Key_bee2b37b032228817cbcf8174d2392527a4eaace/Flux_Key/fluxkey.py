#!/usr/bin/env python3

import sys
from Crypto.Util.number import *
from binascii import hexlify, unhexlify
from secret import decrypt, flag

def die(*args):
	pr(*args)
	quit()
	
def pr(*args):
	s = " ".join(map(str, args))
	sys.stdout.write(s + "\n")
	sys.stdout.flush()
	
def sc():
	return sys.stdin.buffer.readline()

def pad(msg):
	if len(msg) % 4 != 0:
		msg += (- len(msg) % 4) * b'+'
	return msg

def encrypt(msg: bytes, key: bytes) -> bytes:
	msg = pad(msg)
	l = len(msg)
	MSG = [msg[4*k:4*k + 4] for k in range(l // 4)]
	enc, KEY = b'', bytes_to_long(key)
	for _ in MSG:
		key, msg = KEY, bytes_to_long(_)
		for _ in range(rounds):
			_key = (msg >> TIPS[0]) & 1 | (msg >> TIPS[1]) & 2 | (msg >> TIPS[2]) & 4 | (msg >> TIPS[3]) & 8 | (msg >> TIPS[4]) & 16
			head = (msg >> 16 & 1) ^ (msg & 1) ^ (IV >> _key & 1) ^ (key & 1)
			msg = head << 31 | msg >> 1
			key = (key & 1) << 63 | key >> 1
		enc += long_to_bytes(msg).zfill(4)
	return enc

def validate_enc(_enc, __enc):
	if len(_enc) % 4 != 0 or len(_enc) >= len(__enc) or any(_enc[i:i + 4] in __enc for i in range(0, len(_enc), 4)):
		return False
	return True

def main():
	border = "┃"
	pr(        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
	pr(border, ".::    Welcome to the symmetric FluxKey crypto-system task!   ::.", border)
	pr(border, ".: Your mission is to find flag by analyzing this cryptosystem :.", border)
	pr(        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")

	global rounds, TIPS, IV, flag

	IV, TIPS = getRandomNBitInteger(32), [getRandomRange(1, 31) for _ in range(5)]
	rounds = 1424

	key = getRandomNBitInteger(64)
	key = long_to_bytes(key)

	while True:
		pr(f"{border} Options: \n{border}\t[C]hange Parameters! \n{border}\t[D]ecrypt message! \n{border}\t[E]ncrypt the flag! \n{border}\t[G]et Parameters! \n{border}\t[Q]uit")
		ans = sc().decode().strip().lower()
		_flag_enc = hexlify(encrypt(flag, key))
		if ans == 'e':
			pr(border, f'{_flag_enc = }')
		elif ans == 'c':
			pr(border, 'Which Parameter do you want to change: [I]V or [T]IPS?')
			c = sc().decode().strip().lower()
			if c == 'i':
				pr(border, 'Please send the IV as hex: ')
				_IV = sc().decode().strip()
				try:
					IV = int(_IV, 16)
					if len(_IV) == 8 and IV.bit_length() == 32:
						pr(border, 'Good IV :-D')
					else:
						pr(border, 'The length of your IV is wrong!')
				except:
					pr(border, 'Your IV is invalid!')
			elif c == 't':
				pr(border, 'You could NOT change TIPS, sorry!')
			else:
				pr(border, 'Your choice is incorr3cT!')
		elif ans == 'd':
			pr(border, 'Please send your message as hex:')
			_enc = sc().decode().strip()
			try:
				_enc = unhexlify(_enc)
				__enc = unhexlify(_flag_enc)
				if not validate_enc(_enc, __enc):
					pr(border, 'Kidding me!? :|')
				else:
					_msg = decrypt(_enc, key, IV, TIPS, rounds)
					pr(border, f'{_msg = }')
			except:
				pr(border, 'Your encrypted message is not valid!')
		elif ans == 'g':
			pr(border, f'{IV = }\n{border} {TIPS = }')
		elif ans == 'q':
			die(border, "Quitting...")
		else:
			die(border, "Bye...")

if __name__ == '__main__':
	main()