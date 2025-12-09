from pwn import *
from Crypto.Util.Padding import pad, unpad

r = remote('crypto-you-can-not-reuse.chals.blahaj.sg', 26324)

r.recvuntil(b"Your input plaintext: ")
known_plaintext = b"A" * 50
r.sendline(known_plaintext)

r.recvuntil(b"Encrypted flag (hex): ")
encrypted_flag = bytes.fromhex(r.recvline().strip().decode())

r.recvuntil(b"Encrypted input (hex): ")
encrypted_input = bytes.fromhex(r.recvline().strip().decode())

padded_known = pad(known_plaintext, 16)
min_len = min(len(encrypted_flag), len(encrypted_input), len(padded_known))

flag = bytes([encrypted_flag[i] ^ encrypted_input[i] ^ padded_known[i] for i in range(min_len)])
flag_unpadded = unpad(flag, 16)

print(f"Flag: {flag_unpadded.decode()}")
r.close()
