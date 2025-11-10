from pathlib import Path
from itertools import cycle

# --- Step 1: Recover the Key ---

# A standard PNG file's first 16 bytes are very predictable.
# It's the 8-byte signature followed by the 8-byte IHDR chunk header.
known_plaintext_header = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'

# We assume the 'recipes' directory is in the current working directory.
# Let's target one of the encrypted PNG files.
encrypted_file_path = Path("recipes/1f.png.enc")

try:
    # Read the first 16 bytes of the encrypted file
    with open(encrypted_file_path, "rb") as f:
        ciphertext_header = f.read(16)

    # Recover the key by XORing the known plaintext with the ciphertext
    # (Plaintext ^ Key = Ciphertext) implies (Ciphertext ^ Plaintext = Key)
    if len(ciphertext_header) == 16:
        key = bytes(c ^ p for c, p in zip(ciphertext_header, known_plaintext_header))
        print(f"Successfully recovered the key!")
        print(f"Key (bytes): {key}")
        print(f"Key (hex):   {key.hex()}")
    else:
        print("Error: Could not read 16 bytes from the encrypted file.")
        key = None

except FileNotFoundError:
    print(f"Error: The file '{encrypted_file_path}' was not found.")
    print("Please ensure the 'recipes' directory is present.")
    key = None
