# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: ./main.py
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2025-10-29 14:47:38 UTC (1761749258)

attack = input('What attack shall Servine use? > ')
print(f'Servine used {attack}!')

def vine_whip(val, r_bits, max_bits=32):
    return (val << r_bits | val >> max_bits - r_bits) & (1 << max_bits) - 1

def leech_seed(val, r_bits, max_bits=32):
    return (val >> r_bits | val << max_bits - r_bits) & (1 << max_bits) - 1

def bullet_seed(val):
    val = val.encode().zfill(64)
    nums = []
    for i in range(0, len(val), 4):
        nums.append(int.from_bytes(val[i:i + 4]))
    import random
    random.seed(b'servine')
    for i in range(len(nums)):
        nums[i] = nums[i] ^ random.getrandbits(32)
    for i in range(5, 16):
        nums[i] = vine_whip(nums[i], i)
    for i in range(0, 9):
        nums[i] = (nums[i] * random.getrandbits(32) | 1) % 4294967296
    for i in range(2, 14):
        nums[i] = (nums[i] + random.getrandbits(32)) % 4294967296
    random.shuffle(nums)
    if nums == [1454433542, 955021940, 2872705261, 1399142311, 2924800640, 3026681276, 1547421538, 933541538, 1051185089, 2694598254, 2712507769, 4180449996, 3943065784, 1268979863, 2359636600, 2675638245]:
        print("Servine's attack was very effective!")
    else:
        print("The attack wasn't very effective...")
bullet_seed(attack)