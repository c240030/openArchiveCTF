import random
import string

def vine_whip(val, r_bits, max_bits=32):
    return (val << r_bits | val >> max_bits - r_bits) & (1 << max_bits) - 1

def leech_seed(val, r_bits, max_bits=32):
    return (val >> r_bits | val << max_bits - r_bits) & (1 << max_bits) - 1

def mod_inverse(a, m=2**32):
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

random.seed(b'servine')
xor_vals = [random.getrandbits(32) for _ in range(16)]
mul_vals = [random.getrandbits(32) for _ in range(9)]
add_vals = [random.getrandbits(32) for _ in range(12)]
shuffle_perm = list(range(16))
random.shuffle(shuffle_perm)

target = [1454433542, 955021940, 2872705261, 1399142311, 2924800640, 3026681276, 1547421538, 933541538, 1051185089, 2694598254, 2712507769, 4180449996, 3943065784, 1268979863, 2359636600, 2675638245]

unshuffled = [0] * 16
for i in range(16):
    unshuffled[shuffle_perm[i]] = target[i]
for i in range(2, 14):
    unshuffled[i] = (unshuffled[i] - add_vals[i-2]) % 4294967296

valid_chars = string.ascii_letters + string.digits + '_{}0'

print("Brute forcing indices 0-4:")
for idx in range(5):
    val_target = unshuffled[idx]
    m = mul_vals[idx]
    
    found = []
    for c1 in valid_chars:
        for c2 in valid_chars:
            for c3 in valid_chars:
                for c4 in valid_chars:
                    chunk = c1 + c2 + c3 + c4
                    chunk_int = int.from_bytes(chunk.encode(), 'big')
                    after_xor = chunk_int ^ xor_vals[idx]
                    after_mul = ((after_xor * m) | 1) % (2**32)
                    if after_mul == val_target:
                        found.append(chunk)
    
    print(f'  [{idx}] mul={m}, odd={m%2==1}: {found}')
