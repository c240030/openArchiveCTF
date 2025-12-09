import os
import re
import socket
import sys
import time

HOST = "crypto-rot13.chals.blahaj.sg"
PORT = 29237


class NetCat:
    def __init__(self, ip, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((ip, port))
        self.s.settimeout(15)
        self.buffer = ""

    def read_until(self, marker):
        start_time = time.time()
        while marker not in self.buffer:
            try:
                data = self.s.recv(4096).decode("utf-8", errors="ignore")
                if not data:
                    break
                self.buffer += data
            except socket.timeout:
                break
            if time.time() - start_time > 20:  # Safe timeout
                break

        if marker in self.buffer:
            pos = self.buffer.find(marker) + len(marker)
            result = self.buffer[:pos]
            self.buffer = self.buffer[pos:]
            return result
        return self.buffer

    def send_line(self, line):
        self.s.sendall(f"{line}\n".encode())

    def close(self):
        self.s.close()


def parse_int(text, var_name):
    pattern = re.search(f"{var_name}\s*=\s*(\d+)", text)
    if pattern:
        return int(pattern.group(1))
    return None


def main():
    print(f"[*] [PYTHON] Connecting to {HOST}:{PORT}...")
    nc = NetCat(HOST, PORT)

    data_block = nc.read_until("v? ")

    n = parse_int(data_block, "n")
    e = parse_int(data_block, "e")
    c = parse_int(data_block, "c")
    x0 = parse_int(data_block, "x0")
    x1 = parse_int(data_block, "x1")
    x2 = parse_int(data_block, "x2")

    if not n or not x0:
        print("[-] Failed to parse. Server might be lagging. Try again.")
        return

    x_list = [x0, x1, x2]
    pair_idx = []

    for i in range(3):
        for j in range(i + 1, 3):
            if (x_list[i] % 2) == (x_list[j] % 2):
                pair_idx = [i, j]
                break

    idx_a, idx_b = pair_idx
    print(f"[*] [PYTHON] Collision at indices {idx_a} & {idx_b}")

    v_val = (x_list[idx_a] + x_list[idx_b]) // 2
    nc.send_line(str(v_val))

    result_block = nc.read_until("Bye!")
    nc.close()

    c0 = parse_int(result_block, "c0")
    c1 = parse_int(result_block, "c1")
    c2 = parse_int(result_block, "c2")
    c_list = [c0, c1, c2]

    b_bits = 512 // 3 + 1
    lower_mask = (1 << b_bits) - 1
    middle_mask = lower_mask << b_bits
    upper_mask = middle_mask << b_bits
    masks = [lower_mask, middle_mask, upper_mask]

    ma_plus_mb = c_list[idx_a] + c_list[idx_b] - n

    known_p = 0
    known_p |= ma_plus_mb & masks[idx_a]
    known_p |= ma_plus_mb & masks[idx_b]

    missing_idx = 3 - idx_a - idx_b

    shift_bits = 0
    if missing_idx == 1:
        shift_bits = 171
    elif missing_idx == 2:
        shift_bits = 342

    print(f"[*] [PYTHON] Missing part index: {missing_idx}. Generating Sage script...")

    sage_script = f"""
from sage.all import *
from Crypto.Util.number import long_to_bytes

n = {n}
e = {e}
c = {c}
known_p = {known_p}
shift_bits = {shift_bits}

print("[*] [SAGE] Running Coppersmith with beta=0.5...")

P.<x> = PolynomialRing(Zmod(n))
f = known_p + x * (2^shift_bits)
f = f.monic()

# FIX: beta=0.5 is crucial because p is approx N^0.5
roots = f.small_roots(beta=0.5, epsilon=0.01)

if roots:
    missing_val = Integer(roots[0])
    p = known_p + missing_val * (2^shift_bits)

    if n % p == 0:
        print("[+] [SAGE] Factor p FOUND!")
        q = n // p
        phi = (p - 1) * (q - 1)
        d = inverse_mod(e, phi)
        m = power_mod(c, d, n)

        try:
            flag = long_to_bytes(int(m)).decode()
            print("\\n" + "="*40)
            print(f"FLAG: {{flag}}")
            print("="*40 + "\\n")
        except:
            print(f"Decrypted (raw): {{m}}")
    else:
        print("[-] [SAGE] p check failed.")
else:
    print("[-] [SAGE] Roots not found with beta=0.5.")
"""

    with open("crack.sage", "w", encoding="utf-8") as f:
        f.write(sage_script)

    print(f"[*] [PYTHON] Executing 'sage crack.sage'...")
    os.system("sage crack.sage")


if __name__ == "__main__":
    main()
