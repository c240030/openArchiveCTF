#!/usr/bin/env python3
#
# This script solves the challenge using a two-phase attack:
# 1. Binary Search to find the RSA modulus 'n'.
# 2. Meet-in-the-Middle attack to find the flag.
#
# Required libraries: pwntools, pycryptodome
# pip install pwntools pycryptodome
#
from pwn import *
from Crypto.Util.number import long_to_bytes

# --- Connection Details ---
# Note: The port might change if the challenge instance resets.
# The user's provided script used PORT 31114.
HOST = "nc.deadsec.quest"
PORT = 31114

# --- Public Exponent from the Challenge ---
e = 12389231641983877009741841713701317189420787527171545487350619433744301520682298136425919859970313849150196317044388637723151690904279767516595936892361663

def oracle_query(r, i):
    """Sends a number 'i' to the oracle and returns the hex-encoded AES output."""
    try:
        # The server expects a string representation of the number.
        r.sendlineafter(b'sign: ', str(i).encode())
        line = r.recvline(timeout=2)
        # The server returns "bad input, exiting" if i >= n.
        if b'bad input' in line:
            return None
        return line.strip().decode()
    except Exception:
        return None

def find_n_binary_search(host, port):
    """
    Performs a binary search to discover the RSA modulus 'n'.
    This works by finding the boundary where the server accepts vs. rejects input.
    """
    log.info("Phase 1: Starting binary search to find the modulus 'n'...")
    # 'n' is a 1024-bit number, so it's between 2^1023 and 2^1024.
    low = 2**1023
    high = 2**1024

    # Each probe should use a new connection to not interfere with the main session.
    # We set pwntools logging to 'error' for probes to keep the output clean.
    while high > low + 1:
        mid = (low + high) // 2
        with remote(host, port, level='error') as r_probe:
            r_probe.recvuntil(b'service...\n')
            r_probe.recvline() # Consume the ciphertext line
            res = oracle_query(r_probe, mid)
            if res is not None:
                # Server accepted 'mid', so n > mid. Search the upper half.
                log.info(f"Probe at bit-length {mid.bit_length()} SUCCEEDED.")
                low = mid
            else:
                # Server rejected 'mid', so n <= mid. Search the lower half.
                log.info(f"Probe at bit-length {mid.bit_length()} FAILED.")
                high = mid

    n = high
    log.success(f"Found modulus n (bit length: {n.bit_length()})")
    return n

def main():
    """Main function to orchestrate the full attack."""
    context.log_level = 'info'

    # --- STEP 1: Find the modulus n ---
    n = find_n_binary_search(HOST, PORT)
    if n is None:
        log.failure("Could not determine n. Exiting.")
        return

    # --- STEP 2: Start the main connection for the attack ---
    log.info("Connecting for the main attack...")
    conn = remote(HOST, PORT)
    conn.recvuntil(b'service...\n')
    ct = int(conn.recvline().strip()) # The flag's ciphertext
    log.info(f"Received the encrypted flag's ciphertext (ct).")

    # --- STEP 3: Build the dictionary (Side A of the MITM) ---
    # We map the AES output to the known small integer 'j' that produced it.
    # The dictionary format is: { aes_output_hex: j }
    dictionary = {}
    limit_j = 40000  # A larger dictionary increases success chance and time.
    log.info(f"Phase 2: Building lookup dictionary with {limit_j} entries...")
    for j in range(1, limit_j + 1):
        # Encrypt the known plaintext 'j' to get its ciphertext.
        payload = pow(j, e, n)
        response = oracle_query(conn, payload)
        if response is not None:
            dictionary[response] = j
        if j % 2000 == 0:
            log.info(f"Dictionary progress: {j}/{limit_j}")
    log.success("Dictionary built successfully.")

    # --- STEP 4: Search for a collision (Side B of the MITM) ---
    # We vary a multiplier 'k' to find a plaintext (m*k) that collides with a 'j'.
    log.info("Searching for a collision by varying multiplier 'k'...")
    k_found, j_found = -1, -1
    for k in range(1, limit_j + 1):
        # Create the ciphertext for (m * k) using RSA's homomorphic property.
        payload = (ct * pow(k, e, n)) % n
        response = oracle_query(conn, payload)

        if response in dictionary:
            j_found = dictionary[response]
            k_found = k
            log.success(f"Collision found! k = {k_found}, j = {j_found}")
            break
        if k % 2000 == 0:
            log.info(f"Collision search progress: k = {k}")

    if k_found == -1:
        log.failure("Could not find a collision. Try increasing search limits for j/k.")
        conn.close()
        return

    # --- STEP 5: Solve for the flag ---
    # The collision means: m*k = j (mod 2^512).
    # This implies: m*k = j + q*2^512 for some small integer q.
    # We solve for m: m = (j + q*2^512) * k^-1 (mod n)
    log.info("Phase 3: Solving for the flag by iterating through small values of 'q'...")
    k_inv = pow(k_found, -1, n)
    M = 2**512
    # 'q' is almost always a very small integer. We'll search a reasonable range.
    for q in range(2048):
        numerator = j_found + q * M
        m_candidate = (numerator * k_inv) % n

        try:
            flag_bytes = long_to_bytes(m_candidate)
            # Check if the decrypted bytes contain the expected flag format.
            if b'DEAD{' in flag_bytes:
                log.success(f"🎉 Flag Recovered! (found with q={q})")
                print(f"--> {flag_bytes.decode().strip()} <--")
                conn.close()
                return
        except Exception:
            continue

    log.failure("Could not recover the flag. The value of 'q' might be larger than searched.")
    conn.close()

if __name__ == "__main__":
    main()