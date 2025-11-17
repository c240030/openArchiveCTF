#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
import os
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rbktypes import Perm, LayerPub, PublicKey
from perms import compose, inverse, perm_to_cycles, pow_perm, identity, perm_order
from salt import recover_r_from_Jd
from modlinalg import mat_inv_mod, mat_vec_mul_mod
from kem import hkdf_key_from_exponents, aead_open, deserialize_cipher

def unsalt_cipher(salted_cipher: List[Perm], salt_meta: List[Dict]) -> List[Perm]:
    """Unsalt the cipher by recovering r from J and d"""
    unsalted = []
    for C_salted, meta in zip(salted_cipher, salt_meta):
        d = meta["d"]
        J = tuple(meta["J"])
        r = recover_r_from_Jd(J, d)
        r_inv = inverse(r)
        C = compose(r, compose(C_salted, r_inv))
        unsalted.append(C)
    return unsalted

def extract_exponents_cycles(cipher: List[Perm], pub: PublicKey, gen_names: List[str]) -> List[int]:
    """Extract exponents using cycle shifts on each generator independently.

    For disjoint supports: final layer cipher restricted to a generator's cycles
    equals that generator public perm ^ e. Public generator is k * base^s * k^-1.
    We brute force e in [0, ord_g-1] by checking equality on cycle indices.
    """
    all_exps: List[int] = []
    for C_layer, L in zip(cipher, pub.layers):
        for nm in gen_names:
            g = L.gens[nm]
            ord_g = perm_order(g)
            if ord_g <= 1:
                all_exps.append(0)
                continue
            cycles = perm_to_cycles(g)
            # union of indices influenced
            idxs = [i for cyc in cycles for i in cyc]
            # Precompute powers lazily; ord_g max 24 so OK
            found = None
            for e in range(ord_g):
                g_e = pow_perm(g, e)
                if all(C_layer[i] == g_e[i] for i in idxs):
                    found = e
                    break
            if found is None:
                # Fallback: attempt shift detection per first cycle
                first = cycles[0]
                a0 = first[0]
                target = C_layer[a0]
                try:
                    pos = first.index(target)
                    found = pos % ord_g
                except ValueError:
                    found = 0
            all_exps.append(found)
    return all_exps

def solve_rubik_kem():
    """Solve the Rubik KEM challenge"""
    # Load handout
    with open("handout.json", "r") as f:
        handout = json.load(f)
    
    print("[*] Loading handout data...")
    
    # Parse public key
    pub_layers = []
    for L in handout["pub"]["layers"]:
        gens = {nm: tuple(p) for nm, p in L["gens"].items()}
        pub_layers.append(LayerPub(gens=gens, meta=L.get("meta", {})))
    pub = PublicKey(layers=pub_layers)
    
    # Parse cipher and parameters
    salted_cipher = deserialize_cipher(handout["kem"]["cipher"])
    gen_order = handout["kem"]["gen_order"]
    salt_meta = handout["params"]["salt"]
    M = handout["params"]["mix"]["M"]
    A = handout["params"]["mix"]["A"]
    sealed_flag = handout["sealed_flag"]
    
    print(f"[*] Layers: {len(pub_layers)}")
    print(f"[*] Generators per layer: {len(gen_order)}")
    print(f"[*] Total exponents: {len(gen_order) * len(pub_layers)}")
    print(f"[*] Modulus M: {M}")
    
    # Step 1: Unsalt the cipher
    print("\n[*] Step 1: Unsalting cipher...")
    cipher = unsalt_cipher(salted_cipher, salt_meta)
    print("[+] Cipher unsalted!")
    
    # Step 2: Extract original exponents e via cycle analysis
    print("\n[*] Step 2: Extracting original exponents via cycle shifts...")
    e = extract_exponents_cycles(cipher, pub, gen_order)
    print(f"[+] Extracted e (first layer shown) = {e[:len(gen_order)]}")

    # Step 3: Mix exponents: e' = A * e mod M (per hint)
    print("\n[*] Step 3: Mixing exponents e' = A * e mod M ...")
    e_prime = mat_vec_mul_mod(A, e, M)
    print(f"[+] Computed e' (first 18) = {e_prime[:len(gen_order)]}")

    # Step 4: Derive key from e'
    print("\n[*] Step 4: Deriving encryption key from e'...")
    kem_info = b"Rubik-KEM-v2"
    key = hkdf_key_from_exponents(e_prime, info=kem_info)
    print(f"[+] Key derived: {key.hex()[:32]}...")
    
    # Step 5: Decrypt the flag
    print("\n[*] Step 5: Decrypting flag...")
    try:
        flag_bytes = aead_open(key, sealed_flag, aad=b"Rubik-CTF-v2")
        flag = flag_bytes.decode("utf-8")
        print(f"\n{'='*60}")
        print(f"[+] FLAG: {flag}")
        print(f"{'='*60}")
        return flag
    except Exception as err:
        print(f"[-] Decryption failed: {err}")
        return None

if __name__ == "__main__":
    flag = solve_rubik_kem()
    if not flag:
        print("\n[!] Failed to decrypt. Need to debug exponent extraction...")
