import sys
import time

import requests

URL = "http://crypto-keygen-ii.chals.blahaj.sg"
BLOCK_SIZE = 16
TARGET_STR = b"v@l1d_adm1n_k3y_thatimadesure_is2blocks+long_:)"

# Calculate PKCS7 padding
pad_len = BLOCK_SIZE - (len(TARGET_STR) % BLOCK_SIZE)
TARGET_PLAINTEXT = TARGET_STR + bytes([pad_len]) * pad_len


def query_oracle(session, payload):
    url = f"{URL}/api/check/{payload}"
    while True:
        try:
            resp = session.get(url)
            # If server is overloaded or errors out, retry
            if resp.status_code >= 500 or resp.status_code == 429:
                time.sleep(0.5)
                continue

            data = resp.json()
            if "error" in data:
                return False  # Padding Error
            return True  # Padding Valid (or other logical message)

        except (
            requests.exceptions.JSONDecodeError,
            requests.exceptions.RequestException,
        ):
            time.sleep(0.5)
            continue


def get_intermediate_block(session, ciphertext_block):
    intermediate = bytearray(BLOCK_SIZE)
    ciphertext_hex = ciphertext_block.hex()

    for byte_pos in range(BLOCK_SIZE - 1, -1, -1):
        padding_val = BLOCK_SIZE - byte_pos
        probe_iv = bytearray(BLOCK_SIZE)

        for i in range(byte_pos + 1, BLOCK_SIZE):
            probe_iv[i] = intermediate[i] ^ padding_val

        found_byte = None
        for b in range(256):
            probe_iv[byte_pos] = b
            payload = probe_iv.hex() + ciphertext_hex

            if query_oracle(session, payload):
                if padding_val == 1:
                    # Double check for false positive padding (e.g. 0x02 0x02)
                    verify_iv = bytearray(probe_iv)
                    verify_iv[byte_pos - 1] ^= 0x1
                    if not query_oracle(session, verify_iv.hex() + ciphertext_hex):
                        continue
                found_byte = b
                break

        if found_byte is None:
            print(f"[-] Failed to find byte at index {byte_pos}")
            sys.exit(1)

        intermediate[byte_pos] = found_byte ^ padding_val
        print(f"[+] Decrypted byte {byte_pos}: {hex(intermediate[byte_pos])}", end="\r")

    print()
    return bytes(intermediate)


def solve():
    session = requests.Session()
    # Initialize session/IP registration
    try:
        session.get(f"{URL}/api/generate_key")
        print("[*] Session initialized")
    except:
        pass

    blocks = [
        TARGET_PLAINTEXT[i : i + BLOCK_SIZE]
        for i in range(0, len(TARGET_PLAINTEXT), BLOCK_SIZE)
    ]

    # Start with arbitrary ciphertext for the last block
    curr_ciphertext = bytes([0x00] * BLOCK_SIZE)
    full_ciphertext = [curr_ciphertext]

    # CBC-R Attack
    for i, p_block in enumerate(reversed(blocks)):
        print(f"[*] Forging block {len(blocks) - 1 - i}")
        intermediate = get_intermediate_block(session, curr_ciphertext)
        prev_ciphertext = bytes(a ^ b for a, b in zip(intermediate, p_block))
        full_ciphertext.insert(0, prev_ciphertext)
        curr_ciphertext = prev_ciphertext

    final_token = b"".join(full_ciphertext).hex()
    print(f"[*] Admin Token: {final_token}")

    resp = session.get(f"{URL}/api/check/{final_token}")
    try:
        print(f"[*] Result: {resp.json().get('message')}")
    except:
        print(f"[*] Raw Result: {resp.text}")


if __name__ == "__main__":
    solve()
