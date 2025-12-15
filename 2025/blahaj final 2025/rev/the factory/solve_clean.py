from Crypto.Hash import keccak

ENCRYPTED = bytes.fromhex(
    "c52b2cbc9254c72e657858e2fe17ab5e0d97dda00535d21bef4a217b"
)  # Encrypted flag data from Factory contract
KEY_STRING = "2XcLHm}"  # Magic string found in Flag contract bytecode
k = keccak.new(
    digest_bits=256
)  # Compute keccak256 hash as decryption key (Ethereum uses Keccak, not SHA3)
k.update(KEY_STRING.encode())
key = k.digest()
flag = "".join(
    chr((enc - key[i % len(key)]) % 256) for i, enc in enumerate(ENCRYPTED)
)  # Decrypt: reverse the (key + plaintext) % 256 operation

print(f"Flag: {flag}")
