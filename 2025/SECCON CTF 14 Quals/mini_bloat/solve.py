import base64
import gzip
import json
import struct
import hashlib
from z3 import *

B64_DATA = "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"

def solve():
    try:
        compressed_data = base64.b64decode(B64_DATA)
        json_str = gzip.decompress(compressed_data).decode('utf-8')
        puzzle_data = json.loads(json_str)
        print("Decompressed puzzle data.")
    except Exception as e:
        print(f"Decompression error: {e}")
        return

    solutions = []

    print("Solving with Z3 Solver...")
    for day in puzzle_data:
        s = Solver()
        x = BitVec('x', 32)
        all_exprs = day['eqExprs'] + day['maskExprs']

        for expr in all_exprs:
            clean_expr = expr.strip()
            py_expr = clean_expr.replace(">>>", ">>").replace("===", "==")
            try:
                s.add(eval(py_expr))
            except Exception as e:
                print(f"Failed to parse expression for day {day['day']}: {e}")

        if s.check() == sat:
            model = s.model()
            val = model[x].as_long()
            solutions.append(val)
            print(f"Day {day['day']}: {val}")
        else:
            print(f"Day {day['day']}: No solution found!")
            return

    print("\nDecrypting flag...")

    MN = "uJVY4mJFB6T9yppuCdGFmTW1O5GZ06yw4OTVml4VNOw="
    SALT_STR = "boolean-advent-2025-pepper"

    key_buffer = bytearray()
    for sol in solutions:
        key_buffer.extend(struct.pack('>I', sol))

    salt = SALT_STR.encode('utf-8')
    input_data = salt + key_buffer + salt
    key_hash = hashlib.sha256(input_data).digest()

    encrypted_flag = base64.b64decode(MN)

    keystream = bytearray()
    ctr = 0
    while len(keystream) < len(encrypted_flag):
        ctr_bytes = struct.pack('>I', ctr)
        block_input = key_hash + ctr_bytes
        block_hash = hashlib.sha256(block_input).digest()
        keystream.extend(block_hash)
        ctr += 1

    final_flag = bytearray()
    for i in range(len(encrypted_flag)):
        final_flag.append(encrypted_flag[i] ^ keystream[i])

    try:
        print("Flag:", final_flag.decode('utf-8'))
    except:
        print("Decoded bytes (not UTF-8):", final_flag.hex())

if __name__ == "__main__":
    solve()