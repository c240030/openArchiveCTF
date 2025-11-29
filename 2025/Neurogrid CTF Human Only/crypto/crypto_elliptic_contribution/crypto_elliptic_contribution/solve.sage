#!/usr/bin/env sage
import socket
import time
from sage.all import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import sys

HOST = '94.237.61.52'
PORT = 39708

class Remote:
    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.buffer = b""

    def recvuntil(self, delim):
        if isinstance(delim, str): delim = delim.encode()
        while delim not in self.buffer:
            data = self.s.recv(4096)
            if not data: return b""
            self.buffer += data
        idx = self.buffer.find(delim)
        ret = self.buffer[:idx+len(delim)]
        self.buffer = self.buffer[idx+len(delim):]
        return ret.decode()

    def recvline(self):
        return self.recvuntil(b'\n')

    def sendline(self, data):
        if isinstance(data, str): data = data.encode()
        self.s.sendall(data + b'\n')

    def close(self):
        self.s.close()

def solve():
    a = 0x426b522d14487e10aa36de8bfd0f807c2db07551727ea79e1c8670bfa1b6f4f1
    b = 0x2f76b6d71e3ec56f0fd49703151b3ea66bd4fd713e8630fbf461772e2088e2a7

    io = Remote(HOST, PORT)

    print("[*] 1. Recovering Modulus P...")

    def get_server_point():
        io.recvuntil(':: ')
        io.sendline('1')
        io.recvuntil(': ')
        line = io.recvline().strip()
        parts = line.strip("()").split(',')
        return Integer(parts[0]), Integer(parts[1])

    P1 = get_server_point()
    P2 = get_server_point()

    val1 = P1[1]**2 - P1[0]**3 - a*P1[0] - b
    val2 = P2[1]**2 - P2[0]**3 - a*P2[0] - b

    p = GCD(val1, val2)
    print(f"[+] Recovered p: {p}")

    E = EllipticCurve(GF(p), [a, b])
    order = E.order()
    print(f"[+] Curve Order: {order}")

    print("[*] 2. Finding Small Subgroup...")
    factors = order.factor()
    print(f"    Factors: {factors}")

    target_q = None
    for f, exp in factors:
        if 1000 < f < 1000000:
            target_q = int(f)
            break

    if not target_q:
        for f, exp in factors:
            if f > 2:
                target_q = int(f)
                break

    if not target_q:
        print("[-] No suitable factor found.")
        return

    print(f"[+] Selected Subgroup Order: {target_q}")

    print("[*] 3. Generating Malicious Point...")
    G_small = E(0)
    while G_small == E(0):
        R = E.random_point()
        G_small = (order // target_q) * R

    offering = G_small[0]
    print(f"[*] Sending Offering (x-coord): {offering}")

    io.recvuntil(':: ')
    io.sendline('2')
    io.recvuntil(':: ')
    io.sendline(str(offering))

    resp = io.recvline()
    if "sealed verse" not in resp:
        print("[-] Unexpected response from server.")
        resp = io.recvline()

    try:
        hex_ct = resp.split("::")[1].strip()
        enc_data = bytes.fromhex(hex_ct)
    except:
        print(f"[-] Could not parse ciphertext: {resp}")
        return

    iv = enc_data[:16]
    ct = enc_data[16:]

    print(f"[+] Ciphertext captured. Brute-forcing {target_q} keys locally...")

    pt_found = False
    curr = G_small

    byte_orders = ['big', 'little']

    for i in range(1, target_q + 1):
        if i % 5000 == 0:
            print(f"    Checking {i}/{target_q}...")

        sigil = int(curr[0])

        for bo in byte_orders:
            try:
                key_len = (sigil.bit_length() + 7) // 8
                key = int.to_bytes(sigil, length=key_len, byteorder=bo)

                if len(key) not in [16, 24, 32]:

                cipher = AES.new(key, AES.MODE_CBC, iv)
                plaintext = cipher.decrypt(ct)

                try:
                    dec = unpad(plaintext, 16)
                    if b'HTB{' in dec or b'flag{' in dec:
                        print(f"\n[!!!] FLAG FOUND: {dec.decode()}")
                        pt_found = True
                        break
                except:
                    pass
            except Exception:
                pass

        if pt_found:
            break

        curr += G_small

    if not pt_found:
        print("[-] Failed to find flag. Subgroup might be too small for valid key sizes.")

    io.close()

if __name__ == "__main__":
    solve()