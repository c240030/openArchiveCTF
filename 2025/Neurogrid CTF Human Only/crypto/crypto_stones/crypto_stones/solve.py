import sys

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

SIGIL_A = 215467030496758327356459851529799063230
SEAL_HEX = "eb5dbac62b1d25df756d848972fd091a63f88471e2ebffa01cea7b611f5f42920662684e80ae7e3ba0978aafe91e7d4e"
STONES_FILE = "stones.txt"


def solve():
    print(f"[*] Target Sigil A: {SIGIL_A}")

    prefix_str = f"Stone #{SIGIL_A}"
    target_plaintext_block = prefix_str.encode()[:16]

    print(f"[*] Calculated Target Block 0 (Plaintext): {target_plaintext_block}")
    if len(target_plaintext_block) != 16:
        print("[!] Error: Plaintext block is not 16 bytes.")
        return

    print("[*] Generating lookup table for 2^24 keys. Please wait...")

    lookup_table = {}

    for echo in range(2**24):
        key = b"\x00" * 12 + echo.to_bytes(4, "big")

        cipher = AES.new(key, AES.MODE_ECB)
        encrypted_block = cipher.encrypt(target_plaintext_block)

        lookup_table[encrypted_block] = echo

        if echo % 1000000 == 0 and echo > 0:
            print(f"    Generated {echo} candidates...", end="\r")

    print(f"\n[*] Table generation complete. {len(lookup_table)} entries.")

    print("[*] Scanning stones.txt...")
    found_echo = None
    full_ciphertext = None

    try:
        with open(STONES_FILE, "r") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue

                ct_block_hex = line[:32]
                try:
                    ct_block = bytes.fromhex(ct_block_hex)
                except ValueError:
                    continue

                if ct_block in lookup_table:
                    found_echo = lookup_table[ct_block]
                    full_ciphertext = bytes.fromhex(line)
                    print(f"\n[+] MATCH FOUND at line {i + 1}!")
                    print(f"[+] Echo (Key Part): {found_echo}")
                    break
    except FileNotFoundError:
        print(
            f"[!] Error: Could not open {STONES_FILE}. Make sure it is in the same directory."
        )
        return

    if found_echo is None:
        print("[!] Failed to find the target stone. Check byte order or sigil value.")
        return

    key = b"\x00" * 12 + found_echo.to_bytes(4, "big")
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_stone = cipher.decrypt(full_ciphertext)

    print(f"[*] Decrypted Stone Text: {decrypted_stone}")

    try:
        content = decrypted_stone.split(b"#")[1]
        sigil_b_str = content.split(b":")[1]
        sigil_b = int(sigil_b_str)
        print(f"[+] Recovered Sigil B: {sigil_b}")
    except Exception as e:
        print(f"[!] Error parsing sigil_b: {e}")
        return

    print("[*] Decrypting the flag...")
    try:
        flag_key = sigil_b.to_bytes(16, "big")
        flag_cipher = AES.new(flag_key, AES.MODE_ECB)
        seal_bytes = bytes.fromhex(SEAL_HEX)

        flag_padded = flag_cipher.decrypt(seal_bytes)
        flag = unpad(flag_padded, 16)

        print("\n" + "=" * 40)
        print(f"FLAG: {flag.decode()}")
        print("=" * 40 + "\n")
    except Exception as e:
        print(f"[!] Error decrypting flag: {e}")


if __name__ == "__main__":
    solve()
