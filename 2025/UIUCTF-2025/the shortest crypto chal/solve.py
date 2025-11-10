from Cryptodome.Cipher import AES

# The key derived from the solution to the Diophantine equation.
key = "0000051920114400".encode("utf-8")

# The ciphertext provided in the challenge.
ciphertext_hex = "41593455378fed8c3bd344827a193bde7ec2044a3f7a3ca6fb77448e9de55155"
ciphertext = bytes.fromhex(ciphertext_hex)

# Create an AES cipher object in ECB mode.
cipher = AES.new(key, AES.MODE_ECB)

# Decrypt the ciphertext.
decrypted_flag_bytes = cipher.decrypt(ciphertext)

# Decode and print the flag.
# It may have padding, which we can strip.
flag = decrypted_flag_bytes.decode("utf-8").strip()

print(f"The flag is: {flag}")