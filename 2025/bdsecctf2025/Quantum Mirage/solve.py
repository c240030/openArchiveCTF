import base64
import hashlib

# Constants from the provided script
X = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476,
     0xC3D2E1F0, 0x76543210, 0xFEDCBA98, 0x89ABCDEF]
b_seed = b"simple_seed_123"

# Re-implementation of the G function to generate the key
def G(a, b):
    d = a
    for i in range(b):
        if i % 4 == 0:
            d = hashlib.sha256(d).digest()
        elif i % 4 == 1:
            d = hashlib.blake2b(d, digest_size=32).digest()
        elif i % 4 == 2:
            d = hashlib.md5(d).digest() * 2
        else:
            d = hashlib.sha1(d).digest() + d[:12]
    return d

# Our inverse H function
def reverse_H(encrypted_message, key):
    decrypted_bytes = bytearray()
    for i, byte in enumerate(encrypted_message):
        # 1. Reverse the XOR with the X array element
        temp_byte = byte ^ (X[i % len(X)] & 0xFF)
        # 2. Reverse the left bit-rotation (by right-rotating)
        temp_byte = ((temp_byte >> 3) | (temp_byte << 5)) & 0xFF
        # 3. Reverse the XOR with the key byte
        original_byte = temp_byte ^ key[i % len(key)]
        decrypted_bytes.append(original_byte)
    return bytes(decrypted_bytes)

# The intercepted message
intercepted_message = "FL6gWSgGl71j8RANN2yzz9XckwawQ8MXqE7IAOVygOclZiHgi161L7s="

# 1. Base64 decode the message
decoded_ciphertext = base64.b64decode(intercepted_message)

# 2. Generate the decryption key
decryption_key = G(b_seed, 5)

# 3. Apply the reverse_H function to decrypt
decrypted_message = reverse_H(decoded_ciphertext, decryption_key)

# Print the decrypted message (the flag)
print(decrypted_message.decode())
