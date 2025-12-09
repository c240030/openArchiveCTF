from pwn import *
import base64
import struct

def sha256_padding(length):
    padding = b'\x80'
    padding += b'\x00' * ((56 - (length + 1) % 64) % 64)
    padding += struct.pack('>Q', length * 8)
    return padding

def sha256_extend(original_hash, length, append_data):
    h = [int(original_hash[i:i+8], 16) for i in range(0, 64, 8)]
    k = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]
    
    def right_rotate(value, shift):
        return ((value >> shift) | (value << (32 - shift))) & 0xFFFFFFFF

    pad1 = sha256_padding(length)
    current_total_len = length + len(pad1)
    final_total_len = current_total_len + len(append_data)
    
    pad2 = sha256_padding(final_total_len)
    to_process = append_data + pad2
    
    for i in range(0, len(to_process), 64):
        chunk = to_process[i:i+64]
        w = [0] * 64
        for j in range(16):
            w[j] = struct.unpack('>I', chunk[j*4:j*4+4])[0]
        for j in range(16, 64):
            s0 = right_rotate(w[j-15], 7) ^ right_rotate(w[j-15], 18) ^ (w[j-15] >> 3)
            s1 = right_rotate(w[j-2], 17) ^ right_rotate(w[j-2], 19) ^ (w[j-2] >> 10)
            w[j] = (w[j-16] + s0 + w[j-7] + s1) & 0xFFFFFFFF

        a, b, c, d, e, f, g, h_val = h
        for j in range(64):
            s1 = right_rotate(e, 6) ^ right_rotate(e, 11) ^ right_rotate(e, 25)
            ch = (e & f) ^ (~e & g)
            temp1 = (h_val + s1 + ch + k[j] + w[j]) & 0xFFFFFFFF
            s0 = right_rotate(a, 2) ^ right_rotate(a, 13) ^ right_rotate(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (s0 + maj) & 0xFFFFFFFF

            h_val = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF

        h[0] = (h[0] + a) & 0xFFFFFFFF
        h[1] = (h[1] + b) & 0xFFFFFFFF
        h[2] = (h[2] + c) & 0xFFFFFFFF
        h[3] = (h[3] + d) & 0xFFFFFFFF
        h[4] = (h[4] + e) & 0xFFFFFFFF
        h[5] = (h[5] + f) & 0xFFFFFFFF
        h[6] = (h[6] + g) & 0xFFFFFFFF
        h[7] = (h[7] + h_val) & 0xFFFFFFFF

    return ''.join(f'{x:08x}' for x in h), pad1 + append_data

io = remote('crypto-waiting-room.chals.blahaj.sg', 19681)

io.sendlineafter(b'> ', b'1')
io.sendlineafter(b'> ', b'A')

io.sendlineafter(b'> ', b'4')
io.recvuntil(b'message = ')
msg_b64 = eval(io.recvline().strip().decode())
io.recvuntil(b'hash = ')
sig = eval(io.recvline().strip().decode())

original_msg = base64.b64decode(msg_b64)
to_add = b';queue_number=1'
key_len = 64

new_sig, extension = sha256_extend(sig, key_len + len(original_msg), to_add)
new_msg = original_msg + extension

io.sendlineafter(b'> ', b'2')
io.sendlineafter(b'> ', base64.b64encode(new_msg))
io.sendlineafter(b'> ', new_sig.encode())

io.sendlineafter(b'> ', b'3')

io.interactive()
