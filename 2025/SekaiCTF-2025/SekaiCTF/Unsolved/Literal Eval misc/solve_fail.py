# Final Solver for the "Literal Eval" Challenge

import socket
from hashlib import shake_128
from ast import literal_eval
from math import floor, ceil, log2
import sys

# --- Helper function to implement bytes_to_long (no external libraries needed) ---
def bytes_to_long(b: bytes) -> int:
    """Converts a big-endian byte string to an integer."""
    return int.from_bytes(b, 'big')

# --- Constants and Classes from the challenge source code ---
# These values are taken directly from chall.py
m = 256
w = 21
n = 128
l1 = ceil(m / log2(w))
l2 = floor(log2(l1 * (w - 1)) / log2(w)) + 1
l = l1 + l2

class WOTS:
    """
    A container for the static methods of the WOTS+ scheme,
    replicated from the challenge source for local computation.
    """
    @staticmethod
    def pack(num: int, length: int, base: int) -> list[int]:
        """Packs an integer into a list of base-w digits."""
        packed = []
        temp_num = num
        for _ in range(length):
            packed.append(temp_num % base)
            temp_num //= base
        return packed

    @staticmethod
    def chain(x: bytes, n: int) -> bytes:
        """Applies the WOTS+ chaining function (hash) n times to a value x."""
        if n == 0:
            return x
        res = x
        for _ in range(n):
            res = shake_128(b"\x03" + res).digest(16)
        return res

def get_full_packed_digest(message: bytes) -> list[int]:
    """
    Calculates the full WOTS+ packed digest for a given message,
    including the checksum, as done on the server.
    """
    digest = shake_128(b"\x00" + message).digest(32)
    d1 = WOTS.pack(bytes_to_long(digest), l1, w)
    checksum = sum(w - 1 - i for i in d1)
    d2 = WOTS.pack(checksum, l2, w)
    return d1 + d2

# --- Main Exploit Logic ---

def solve():
    """
    Connects to the server, performs the signature forgery,
    and retrieves the flag.
    """
    # TODO: UPDATE THESE VALUES WHEN YOU LAUNCH THE INSTANCE
    HOST = "literal-eval-auzw2my1wzlq.chals.sekai.team"
    PORT = 1337
    
    # Use a try...finally block to ensure the connection is always closed
    s = None
    try:
        # 1. Connect to the server
        print(f"[*] Connecting to {HOST}:{PORT}...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(30)  # Set a 30-second timeout for network operations
        s.connect((HOST, PORT))
        print("[+] Connection successful.")

        # 2. Receive the initial public key from the server (for confirmation)
        initial_output = s.recv(1024).decode()
        print(f"[+] Initial server output: {initial_output.strip()}")

        # 3. Define the target message and the message we will use for forgery
        # The vulnerability allows us to forge a signature for any message 'm'
        # as long as we have a signature for a message 'm_forge' where each
        # component of its digest is >= the corresponding component of m's digest.
        # A message of all null bytes often produces a digest with large components.
        flag_msg = b"Give me the flag"
        forge_msg = b'\x00' * 32

        # 4. Locally compute the digests to confirm our forge_msg is suitable
        print("[*] Locally computing and comparing message digests...")
        d_flag = get_full_packed_digest(flag_msg)
        d_forge = get_full_packed_digest(forge_msg)

        # This assertion verifies the core condition for the forgery attack
        assert all(d_forge[i] >= d_flag[i] for i in range(l)), "[-] Chosen forge_msg is not suitable."
        print("[+] Forge message is suitable.")

        # 5. Request a signature for the forge_msg from the server.
        # We can use any unused key index; index 0 is the simplest.
        print("[*] Requesting signature for the forge message from the server...")
        sign_req = f"{{'type': 'sign', 'num_sign': 1, 'inds': [0], 'messages': [{repr(forge_msg)}]}}"
        s.sendall(sign_req.encode() + b'\n')
        
        # Read the server's response, which contains the signature
        response_buffer = ""
        while "input: " not in response_buffer:
            response_buffer += s.recv(8192).decode()

        # The response needs to be parsed with literal_eval
        sign_resp_str = response_buffer.replace("input: ", "").strip()
        sign_resp = literal_eval(sign_resp_str)
        s_forge_full = sign_resp[0]
        print("[+] Received signature for forge message.")

        # 6. Forge the signature for the target message ("Give me the flag")
        # This is the core of the exploit. We "reduce" the signature for forge_msg
        # to the signature for flag_msg by applying the chain function more times.
        s_forge = s_forge_full[0]      # The WOTS signature part
        auth_path = s_forge_full[1:]   # The Merkle Tree authentication path

        s_flag = []
        for i in range(l):
            # The number of additional hashes needed is the difference between the digests
            diff = d_forge[i] - d_flag[i]
            s_flag.append(WOTS.chain(s_forge[i], diff))

        # Reconstruct the full signature for the flag message
        s_flag_full = [s_flag] + auth_path
        print("[+] Successfully forged signature for the target message.")

        # 7. Send the forged signature to the server's get_flag function
        # We must carefully format the signature as a string that literal_eval can parse.
        wots_sig_str = "[" + ",".join(map(repr, s_flag_full[0])) + "]"
        auth_path_str = ",".join([f"({p[0]}, {repr(p[1])})" for p in s_flag_full[1:]])
        sig_str = f"[{wots_sig_str},{auth_path_str}]"
        get_flag_req = f"{{'type': 'get_flag', 'sig': {sig_str}}}"

        print("[*] Sending forged signature to get the flag...")
        s.sendall(get_flag_req.encode() + b'\n')

        # 8. Receive the final response and print the flag
        flag_resp = s.recv(1024).decode()
        print("\n" + "="*40)
        print("  Server Response (Flag)  ")
        print("="*40)
        print(flag_resp.strip())
        print("="*40)

    except socket.timeout:
        print("\n[-] ERROR: The connection timed out. The server might be down or unreachable.")
    except ConnectionRefusedError:
        print("\n[-] ERROR: The connection was refused by the server.")
    except (socket.gaierror, OSError) as e:
        print(f"\n[-] ERROR: A network error occurred. Could not resolve hostname: {e}")
    except Exception as e:
        print(f"\n[-] An unexpected error occurred: {e}")
        # Print a more detailed traceback for debugging
        import traceback
        traceback.print_exc()
    finally:
        # Ensure the socket is closed
        if s:
            s.close()
            print("\n[*] Connection closed.")

if __name__ == "__main__":
    solve()