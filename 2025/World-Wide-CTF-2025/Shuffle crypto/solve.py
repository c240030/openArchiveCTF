import socket
import re
import sys
import string

# --- Configuration ---
HOST = 'chal.wwctf.com'
PORT = 8010
KEYSTREAM_LEN = 300
# Define the set of printable ASCII bytes for our check.
PRINTABLE_BYTES = set(string.printable.encode('ascii'))

def find_plausible_decryptions(encrypted_flag: bytes, full_keystream: bytes):
    """
    Brute-forces the keystream alignment and yields any candidate that is fully printable.
    
    Args:
        encrypted_flag: The raw bytes of the encrypted flag.
        full_keystream: The recovered keystream from the server.
        
    Yields:
        A plausible decrypted candidate as a string.
    """
    flag_len = len(encrypted_flag)
    
    for shift in range(KEYSTREAM_LEN):
        key_segment = bytes(
            full_keystream[(i + shift) % KEYSTREAM_LEN] for i in range(flag_len)
        )
        decrypted_candidate = bytes(c ^ k for c, k in zip(encrypted_flag, key_segment))
        
        # New, looser check: is the entire candidate string printable?
        if all(char in PRINTABLE_BYTES for char in decrypted_candidate):
            # Instead of stopping, we 'yield' the result and keep searching.
            yield decrypted_candidate.decode(errors='ignore')

def solve():
    """
    Connects to the server, performs a chosen-plaintext attack, and finds the flag.
    """
    print(f"[*] Connecting to {HOST}:{PORT}...")
    try:
        with socket.create_connection((HOST, PORT), timeout=10) as sock:
            sock.recv(1024) # Discard banner
            encrypted_flag_hex = sock.recv(1024).strip()
            encrypted_flag = bytes.fromhex(encrypted_flag_hex.decode())
            print(f"[*] Received encrypted flag ({len(encrypted_flag)} bytes).")

            chosen_plaintext = (b'00' * KEYSTREAM_LEN) + b'\n'
            print(f"[*] Sending {KEYSTREAM_LEN} null bytes to recover the keystream...")
            sock.sendall(chosen_plaintext)
            
            keystream_hex = sock.recv(KEYSTREAM_LEN * 2)
            keystream = bytes.fromhex(keystream_hex.decode())
            print(f"[*] Recovered keystream ({len(keystream)} bytes).")

            print("\n[*] Brute-forcing... Printing all plausible decryptions:")
            print("-" * 55)
            
            found_count = 0
            for candidate in find_plausible_decryptions(encrypted_flag, keystream):
                print(f"  [Shift {found_count:03d}]: {candidate}")
                found_count += 1
            
            print("-" * 55)
            if found_count == 0:
                print("\n[!] No plausible decryptions found.")
            else:
                print(f"\n[!] Search complete. The flag should be one of the lines above.")

    except (socket.timeout, ConnectionRefusedError) as e:
        print(f"[!] Network Error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    solve()