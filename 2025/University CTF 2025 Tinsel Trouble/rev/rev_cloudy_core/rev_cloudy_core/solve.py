import zlib

with open(r'c:\Users\LEGION\Desktop\rev_cloudy_core\rev_cloudy_core\snownet_stronger.tflite', 'rb') as f:
    data = f.read()

# The encrypted blob at offset 0x238 (36 bytes based on length at 0x234)
enc = data[0x238:0x238+36]
# XOR with k3y!
key = b'k3y!'
dec = bytes([enc[i] ^ key[i % len(key)] for i in range(len(enc))])
print('Decrypted (XOR):', dec.hex())
print('First bytes:', hex(dec[0]), hex(dec[1]))
# 78 9C is zlib signature - decompress
try:
    decompressed = zlib.decompress(dec)
    print('Decompressed:', decompressed)
except Exception as e:
    print('Decompression error:', e)
    # Maybe we need more data