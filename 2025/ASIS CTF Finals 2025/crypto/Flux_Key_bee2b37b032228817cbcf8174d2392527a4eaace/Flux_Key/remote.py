#!/usr/bin/env python3
from pwn import *
from z3 import *
from binascii import hexlify, unhexlify
from Crypto.Util.number import long_to_bytes, bytes_to_long
import re
import random

HOST = '65.109.194.34'
PORT = 13337
context.log_level = 'info'

def decrypt_weak_iv(enc_msg, key_int, rounds=1424):
    if len(enc_msg) % 4 != 0: return b''
    dec = b''
    MSG = [enc_msg[4*k:4*k + 4] for k in range(len(enc_msg) // 4)]
    
    keys = []
    curr_k = key_int
    for _ in range(rounds):
        keys.append(curr_k)
        curr_k = ((curr_k & 1) << 63 | curr_k >> 1) & 0xFFFFFFFFFFFFFFFF
        
    for chunk in MSG:
        m_val = bytes_to_long(chunk)
        for i in range(rounds - 1, -1, -1):
            key_r = keys[i]
            
            head = (m_val >> 31) & 1
            m_shifted = m_val & 0x7FFFFFFF
            
            bit_16_old = (m_shifted >> 15) & 1
            bit_iv = 1
            bit_key = key_r & 1
            
            lsb = head ^ bit_16_old ^ bit_iv ^ bit_key
            
            m_val = (m_shifted << 1) | lsb
            
        dec += long_to_bytes(m_val, 4)
    return dec.rstrip(b'+')

def solve():
    try:
        r = remote(HOST, PORT)

        WEAK_IV = 0xFFFFFFFF
        log.info(f"Setting Weak IV: {hex(WEAK_IV)}")
        
        r.recvuntil(b'Options:')
        r.sendline(b'c')
        r.sendline(b'i')
        r.sendline(hex(WEAK_IV)[2:].encode())
        
        if b'Good IV' not in r.recvuntil(b'Options:'):
            log.error("Failed to set IV")
            return

        log.info("Getting Flag (encrypted with Weak IV)...")
        r.sendline(b'e')
        resp = r.recvuntil(b'Options:').decode()
        
        match = re.search(r"_flag_enc = b'([a-f0-9]+)'", resp)
        if not match: match = re.search(r"_flag_enc = ([a-f0-9]+)", resp)
        flag_enc = unhexlify(match.group(1))
        
        traces = []
        log.info("Collecting 3 traces...")
        for i in range(3):
            c_bytes = random.randbytes(4)
            c_val = bytes_to_long(c_bytes)
            
            r.sendline(b'd')
            r.sendline(hexlify(c_bytes))
            
            resp = r.recvuntil(b'Options:').decode()
            match = re.search(r"_msg = (b'.*?')", resp)
            if match:
                try:
                    pt_val = bytes_to_long(eval(match.group(1)))
                    traces.append((c_val, pt_val))
                    log.info(f"Trace {i+1}: OK")
                except: pass

        if len(traces) < 3:
            log.error("Not enough traces.")
            return

        log.info("Solving Key with Z3...")
        s = Solver()
        KEY = BitVec('KEY', 64)
        rounds = 1424
        
        for (c_val, p_val) in traces:
            msg = BitVecVal(p_val, 32)
            k = KEY
            for _ in range(rounds):
                head = Extract(16, 16, msg) ^ Extract(0, 0, msg) ^ 1 ^ Extract(0, 0, k)
                msg = Concat(head, Extract(31, 1, msg))
                k = RotateRight(k, 1)
            s.add(msg == BitVecVal(c_val, 32))

        if s.check() == sat:
            rec_key = s.model()[KEY].as_long()
            log.success(f"KEY FOUND: {hex(rec_key)}")
            
            flag_dec = decrypt_weak_iv(flag_enc, rec_key, rounds)
            
            log.success("==================================================")
            log.success(f"FLAG: {flag_dec.decode(errors='ignore')}")
            log.success("==================================================")
        else:
            log.error("Unsatisfiable!")

        r.close()
    except Exception as e:
        log.error(f"Error: {e}")

if __name__ == '__main__':
    solve()