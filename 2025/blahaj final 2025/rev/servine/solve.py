import random
import struct

target_nums = [
    1454433542, 955021940, 2872705261, 1399142311,
    2924800640, 3026681276, 1547421538, 933541538,
    1051185089, 2694598254, 2712507769, 4180449996,
    3943065784, 1268979863, 2359636600, 2675638245
]

MOD = 4294967296

def leech_seed(val, r_bits, max_bits=32):
    return (val >> r_bits | val << (max_bits - r_bits)) & ((1 << max_bits) - 1)

def solve():
    random.seed(b'servine')
    
    xor_rands = [random.getrandbits(32) for _ in range(16)]
    
    mult_rands = [random.getrandbits(32) for _ in range(9)]
    
    add_rands = [random.getrandbits(32) for _ in range(12)]
    
    indices = list(range(16))
    random.shuffle(indices)
    
    print("[*] Đang giải mã...")

    nums = [0] * 16
    for current_pos, original_pos in enumerate(indices):
        nums[original_pos] = target_nums[current_pos]

    for i in range(2, 14):
        r = add_rands[i - 2]
        nums[i] = (nums[i] - r) % MOD

    for i in range(5, 16):
        nums[i] = leech_seed(nums[i], i)

    for i in range(len(nums)):
        nums[i] ^= xor_rands[i]

    flag_bytes = b""
    for n in nums:
        try:
            flag_bytes += n.to_bytes(4, 'big')
        except:
            pass

    flag = flag_bytes.replace(b'\x00', b'')
    
    print(f"[+] Flag found: {flag.decode('utf-8', errors='ignore')}")

if __name__ == "__main__":
    solve()