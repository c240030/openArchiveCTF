#!/usr/bin/env python3
from hashlib import sha256
from pwn import *
from py_ecc.sec256k1 import P, G as G_lib, N, multiply, add, inv

# --- Helper Class and Functions (from challenge) ---
class Point:
    def __init__(self, x, y):
        self.point = (x, y)
    def __add__(self, other):
        if self.point == (0, 0): return other
        if other.point == (0, 0): return self
        return Point(*add(self.point, other.point))
    def __mul__(self, scalar):
        if self.point == (0, 0): return self
        return Point(*multiply(self.point, scalar % N))
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    def __neg__(self):
        return Point(self.point[0], (P - self.point[1]) % P)
    def __eq__(self, other):
        return self.point == other.point
    def __repr__(self):
        return str(self.point)

G = Point(*G_lib)
INF_POINT = Point(0,0)

def H(*args):
    return int.from_bytes(sha256(str(args).encode()).digest(), "big")

def lamb(i, S):
    num, den = 1, 1
    for j in S:
        if j == i: continue
        num = (num * j) % N
        den = (den * (j - i)) % N
    return (num * inv(den, N)) % N

def sum_pts(points):
    res = INF_POINT
    for point in points:
        res = res + point
    return res

def poly_eval_comms(comms, i, threshold):
    return sum_pts([comms[k] * pow(i, k, N) for k in range(threshold)])

def eval_poly(coeffs, x):
    res = 0
    for coeff in coeffs[::-1]:
        res = (res * x + coeff) % N
    return res

def parse_point_from_line(line):
    # Extracts a point from a line like "  C_1,0 = (x, y)"
    pt_str = line.split(" = ")[1]
    return Point(*eval(pt_str))

# --- Main Exploit Logic ---
def solve():
    context.log_level = 'info'
    # Launch the challenge script as a local process
    r = process(['python3', 'chall.py'])

    # --- Constants from Challenge ---
    NUM_PARTIES = 9
    THRESHOLD = 7
    MY_ID = 9
    
    # --- Round 1: Parse and Commit ---
    r.recvuntil(b"context string ")
    CONTEXT = bytes.fromhex(r.recvline().strip().decode())
    log.info(f"Parsed CONTEXT: {CONTEXT.hex()}")

    # Dynamically parse commitments from other parties
    all_comms = {}
    for i in range(1, NUM_PARTIES):
        r.recvuntil(f"[+] Commitments from party {i}:\n".encode())
        comms_i = []
        for k in range(THRESHOLD):
            line = r.recvline().strip().decode()
            comms_i.append(parse_point_from_line(line))
        all_comms[i] = comms_i
    log.info("Parsed commitments from all other parties.")

    # My "Honest" Commitment
    my_coeffs = [1] * THRESHOLD
    my_comms = [c * G for c in my_coeffs]
    all_comms[MY_ID] = my_comms

    r.sendlineafter(b"your coefficients.", b"")
    for comm in my_comms:
        r.sendline(str(comm.point[0]).encode())
        r.sendline(str(comm.point[1]).encode())
    
    my_secret = my_coeffs[0]
    k_proof = 42 # Fixed k for reproducibility
    R_proof = k_proof * G
    c_proof = H(CONTEXT, MY_ID, my_comms[0], R_proof)
    mu_proof = (k_proof + my_secret * c_proof) % N

    r.sendlineafter(b"Send Point R:", str(R_proof.point[0]).encode())
    r.sendlineafter(b"Send mu:", str(R_proof.point[1]).encode())
    r.sendline(str(mu_proof).encode())
    log.info("Round 1: My commitments and proof sent.")

    # --- Round 2: Share Distribution ---
    my_shares = {j: eval_poly(my_coeffs, j) for j in range(1, NUM_PARTIES + 1)}
    r.recvuntil(b"provide your shares")
    for i in range(1, NUM_PARTIES + 1):
        r.sendlineafter(f"party {i}:".encode(), str(my_shares[i]).encode())

    my_signing_share = my_shares[MY_ID]
    for i in range(1, NUM_PARTIES):
        r.recvuntil(f"from party {i}: ".encode())
        share_from_i = int(r.recvline().strip())
        my_signing_share = (my_signing_share + share_from_i) % N

    my_public_share = sum_pts([poly_eval_comms(all_comms[j], MY_ID, THRESHOLD) for j in range(1, NUM_PARTIES + 1)])
    r.sendlineafter(b"your public verification share `Y_i`.", str(my_public_share.point[0]).encode())
    r.sendline(str(my_public_share.point[1]).encode())
    log.info("Round 2: My shares and public share sent.")

    # --- Phase 3: The Exploit ---
    for round_num in range(100):
        log.info(f"--- Starting Signing Round {round_num+1} ---")
        
        # Calculate full public state needed for the attack
        group_pk = sum_pts([all_comms[i][0] for i in range(1, NUM_PARTIES + 1)])
        public_shares = {i: sum_pts([poly_eval_comms(all_comms[j], i, THRESHOLD) for j in range(1, NUM_PARTIES + 1)]) for i in range(1, NUM_PARTIES + 1)}

        # 1. Generate "honest" internal nonce secrets
        d_9_h, e_9_h = 1337, 420
        D_9_h, E_9_h = d_9_h * G, e_9_h * G

        # 2. Receive server data
        r.recvuntil(b"Provide your nonces")
        r.recvuntil(b"Set of signers for this round: ")
        S = eval(r.recvline().strip())
        m = "GIVE ME THE FLAG PLEASE"
        
        # 3. Predict hashes and challenge `c` based on our HONEST nonces
        temp_nonsense = {}
        for i in S - {MY_ID}:
            r.recvuntil(f"Party {i} nonces: D=".encode())
            D_i_str = r.recvuntil(b",", drop=True).decode()
            E_i_str = r.recvline().strip().decode().split("=")[1]
            temp_nonsense[i] = (Point(*eval(D_i_str)), Point(*eval(E_i_str)))
        temp_nonsense[MY_ID] = (D_9_h, E_9_h)
        
        temp_nonsense_ordered = sorted([(i, Di, Ei) for i, (Di, Ei) in temp_nonsense.items()])
        rhos_h = {i: H(i, m, temp_nonsense_ordered) for i in S}
        R_9_h = D_9_h + rhos_h[MY_ID] * E_9_h
        group_nonsense_h = sum_pts([Di + rhos_h[i] * Ei for i, (Di, Ei) in temp_nonsense.items()])
        challenge_c_h = H(group_nonsense_h, group_pk, m)
        
        # 4. Calculate the error point
        Y_prime = sum_pts([public_shares[i] * lamb(i, S) for i in S])
        error_point = challenge_c_h * (Y_prime - group_pk)
        
        # 5. Craft and send MALICIOUS nonces
        R_9_mal = R_9_h + error_point
        E_9_mal = E_9_h
        D_9_mal = R_9_mal - (rhos_h[MY_ID] * E_9_mal)
        
        r.sendline(str(D_9_mal.point[0]).encode())
        r.sendline(str(D_9_mal.point[1]).encode())
        log.info("Malicious nonces sent.")
        
        # 6. Get the REAL challenge and rhos from the server
        r.recvuntil(b"Group challenge `c`: ")
        final_c = int(r.recvline().strip())
        
        final_nonsense = temp_nonsense
        final_nonsense[MY_ID] = (D_9_mal, E_9_mal)
        final_nonsense_ordered = sorted([(i, Di, Ei) for i, (Di, Ei) in final_nonsense.items()])
        final_rhos = {i: H(i, m, final_nonsense_ordered) for i in S}
        
        # 7. Calculate and send the signature share based on our ORIGINAL honest secrets
        my_lambda = lamb(MY_ID, S)
        my_zi = (d_9_h + e_9_h * final_rhos[MY_ID] + my_signing_share * final_c * my_lambda) % N

        r.sendlineafter(b"Provide your signature share `z_i`.", str(my_zi).encode())
        log.info("Corresponding signature share sent.")
        
        # Check for the flag
        try:
            line = r.recvline(timeout=2)
            if b"FLAG" in line:
                log.success(f"Flag found: {line.decode().strip()}")
                break
            if b"successful" in line:
                line = r.recvline(timeout=2)
                log.success(f"Flag found: {line.decode().strip()}")
                break
        except EOFError:
            log.error("Process terminated unexpectedly.")
            break
    
    r.close()

if __name__ == "__main__":
    solve()