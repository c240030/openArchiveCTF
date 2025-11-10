from pathlib import Path
from itertools import cycle

# --- Step 1: Recover the Key ---
# This part is the same as before. It will fail here, but you can
# run the combined script on your machine.

key = None
try:
    known_plaintext_header = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
    encrypted_file_path = Path("recipes/1f.png.enc")
    with open(encrypted_file_path, "rb") as f:
        ciphertext_header = f.read(16)

    if len(ciphertext_header) == 16:
        key = bytes(c ^ p for c, p in zip(ciphertext_header, known_plaintext_header))
        print(f"Successfully recovered the key: {key.hex()}")
    else:
        print("Error: Could not read 16 bytes from the encrypted file.")

except FileNotFoundError:
    print("Key recovery failed because 'recipes/1f.png.enc' not found.")
    print("Falling back to a placeholder key. You must run this locally.")
    # In a real scenario, the script would stop. For demonstration,
    # I'll pretend a key was found so the rest of the code can be shown.
    # Replace this with the actual key you recover.
    key = b'&\x8fv\xad\x141\xf12\x87\x9f\xcbl\x0epK\x99'


# --- Step 2: Decrypt all files using the recovered key ---

if key:
    TARGET_DIR = Path("recipes/")

    def decrypt(file: Path, key: bytes) -> None:
        """Decrypts a file using a repeating XOR key."""
        with open(file, "rb") as f:
            ciphertext = f.read()

        # The decryption process is identical to encryption
        plaintext = bytes(a ^ b for a, b in zip(ciphertext, cycle(key)))

        # Create the new filename by removing the .enc extension
        decrypted_path = file.with_suffix('')
        
        with open(decrypted_path, "wb") as f:
            f.write(plaintext)

        print(f"Decrypted: {file.name} -> {decrypted_path.name}")

    print("\nStarting decryption process...")
    
    if TARGET_DIR.exists() and TARGET_DIR.is_dir():
        encrypted_files = list(TARGET_DIR.rglob("*.enc"))
        if not encrypted_files:
            print("No .enc files found to decrypt.")
        else:
            for file in encrypted_files:
                if file.is_file():
                    decrypt(file, key)
            print("\nDecryption complete!")
    else:
        print(f"Directory '{TARGET_DIR}' not found. Cannot proceed with decryption.")
