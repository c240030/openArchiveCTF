from pwn import *
from Crypto.Util.number import bytes_to_long, long_to_bytes

HOST = "nc.deadsec.quest"
PORT = 31114

e = 12389231641983877009741841713701317189420787527171545487350619433744301520682298136425919859970313849150196317044388637723151690904279767516595936892361663

def bits_to_string(bit_string):
    # Pad to nearest multiple of 8 if needed
    padded = bit_string.ljust((len(bit_string) + 7) // 8 * 8, '0')
    try:
        # Convert to bytes
        byte_array = int(padded, 2).to_bytes(len(padded) // 8, byteorder='big')
        return byte_array.decode(errors='ignore')  # Ignore invalid characters
    except Exception as e:
        print(f"Error: {e}")
        return ""

def oracle_query(r, i):
    try:
        r.sendlineafter(b'sign: ', str(i).encode())
        line = r.recvline(timeout=10)
        if b'bad input' in line:
            return None
        result = line.strip().decode()
        return result
    except Exception as e:
        return None

def find_n_same_connection(r):
    low = 2**1023
    high = 2**1024
    
    while high > low + 1:
        mid = (low + high) // 2
        
        res = oracle_query(r, mid)
        if res is not None:
            low = mid
        else:
            high = mid
    
    n = high
    return n

r = remote(HOST, PORT)
r.recvuntil(b'service...\n')
ct = int(r.recvline().strip())

n = find_n_same_connection(r)

def shift(r,shift_amount,c,n,e):
    s = pow(2, shift_amount, n)
    s_e = pow(s, e, n)
    c_shifted = (c * s_e) % n
    return oracle_query(r, c_shifted)

def bits_to_number_with_start_exp(bit_string, start_exp,e,n):
    # bit_string assumed leftmost bit is highest power
    value = 0
    length = len(bit_string)
    for i, bit in enumerate(bit_string):
        if bit == '1':
            power = start_exp - i
            value += 2 ** power
    return pow(value, e, n)

bits = ""
for i in range(511,-1,-1):
    flag_c = shift(r,i,ct,n,e)
    candidate_0 = oracle_query(r, bits_to_number_with_start_exp("0" + bits, 511,e,n))
    candidate_1 = oracle_query(r, bits_to_number_with_start_exp("1" + bits, 511,e,n))
    if (flag_c == candidate_0):
        bits = "0" + bits
    elif(flag_c == candidate_1):
        bits = "1" + bits
    if("DEAD" in bits_to_string(bits)):
        print(bits_to_string(bits))