import socket

# --- Connection Details ---
HOST = "ctfi.ng"
PORT = 31556
NUM_SAMPLES = 1500

def solve():
    print("--- oooo solver (v3 - Final) ---")
    
    # --- 1. Data Collection ---
    ciphertexts = []
    flag_len = 0
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            with s.makefile(mode='rw', encoding='utf-8') as f:
                print(f.readline().strip()) # Print welcome message

                for i in range(NUM_SAMPLES):
                    f.write('go\n')
                    f.flush()
                    
                    hex_ct = f.readline().strip()
                    ct_bytes = bytes.fromhex(hex_ct)
                    
                    if i == 0:
                        flag_len = len(ct_bytes)
                        print(f"Flag length detected: {flag_len} bytes")

                    ciphertexts.append(ct_bytes)
                    
                    if (i + 1) % 100 == 0:
                        print(f"Collected {i+1}/{NUM_SAMPLES} ciphertexts...")
    except Exception as e:
        print(f"An error occurred during network communication: {e}")
        return

    # --- 2. Find Possible Deltas ---
    print("\n--- 2. Finding Possible Deltas ---")
    deltas = [[set() for _ in range(flag_len)] for _ in range(flag_len)]
    for i in range(flag_len):
        for j in range(i + 1, flag_len):
            forbidden = {ct[i] ^ ct[j] for ct in ciphertexts}
            possible = set(range(256)) - forbidden
            deltas[i][j] = possible
            deltas[j][i] = possible

    # --- 3. Resolve Ambiguities ---
    print("\n--- 3. Resolving Ambiguities ---")
    while True:
        changed_in_pass = False
        for i in range(flag_len):
            for j in range(i + 1, flag_len):
                if len(deltas[i][j]) == 1: continue # Already solved
                for k in range(flag_len):
                    if k == i or k == j: continue

                    # Prune delta(i, j) using a known intermediate delta(i, k) and delta(j, k)
                    if len(deltas[i][k]) == 1 and len(deltas[j][k]) == 1:
                        old_len = len(deltas[i][j])
                        d_ik = list(deltas[i][k])[0]
                        d_jk = list(deltas[j][k])[0]
                        correct_delta = d_ik ^ d_jk
                        deltas[i][j].intersection_update({correct_delta})
                        if len(deltas[i][j]) < old_len: changed_in_pass = True
                        deltas[j][i] = deltas[i][j]

        current_max = max(len(deltas[i][j]) for i in range(flag_len) for j in range(i+1, flag_len))
        print(f"Propagation pass complete. Max candidates remaining: {current_max}")
        if not changed_in_pass or current_max == 1:
            break

    if current_max > 1:
        print("Error: Could not fully resolve deltas. Try even more samples.")
        return

    # --- 4. Reconstruct the Flag ---
    print("\n--- 4. Reconstructing Flag ---")
    flag = [0] * flag_len
    flag[0] = ord('c') # Assume 'c' for corctf

    for i in range(1, flag_len):
        # Directly access the solved delta from the set
        flag[i] = flag[0] ^ list(deltas[0][i])[0]

    try:
        result = bytes(flag)
        print(f"Reconstructed Flag: {result.decode()}")
    except UnicodeDecodeError:
        print(f"Could not decode flag, but here are the bytes: {result}")

solve()