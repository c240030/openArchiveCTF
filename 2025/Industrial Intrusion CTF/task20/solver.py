import os

def solve_aes_gcm_nonce_reuse(file1_path, file2_path, known_plaintext_str):
    """
    Recovers the plaintext from the second file in an AES-GCM nonce reuse attack.

    Args:
        file1_path (str): Path to the first captured packet file.
        file2_path (str): Path to the second captured packet file.
        known_plaintext_str (str): The known plaintext of the first packet.

    Returns:
        str: The recovered plaintext of the second packet, or an error message.
    """
    try:
        # Step 1: Read the raw byte data from both files.
        with open(file1_path, 'rb') as f1, open(file2_path, 'rb') as f2:
            packet1_data = f1.read()
            packet2_data = f2.read()

        # File format: [16 bytes nonce] || [96 bytes ciphertext] || [16 bytes GCM tag]
        # Step 2: Extract the 96-byte ciphertext from each file.
        ciphertext1 = packet1_data[16:112]
        ciphertext2 = packet2_data[16:112]

        # Sanity check file lengths
        if len(ciphertext1) != 96 or len(ciphertext2) != 96:
            return f"Error: Ciphertext length is not 96 bytes. Check file formats. Got {len(ciphertext1)} and {len(ciphertext2)}."

        # Step 3: Encode the known plaintext string into bytes.
        plaintext1 = known_plaintext_str.encode('utf-8')

        if len(plaintext1) != 96:
            return f"Error: Known plaintext is not 96 bytes long. It is {len(plaintext1)} bytes."

        # Step 4: Perform the byte-wise XOR operation (P1 ^ C1 ^ C2)
        recovered_plaintext_bytes = bytes([
            p1_byte ^ c1_byte ^ c2_byte
            for p1_byte, c1_byte, c2_byte in zip(plaintext1, ciphertext1, ciphertext2)
        ])

        # Decode the resulting bytes to reveal the hidden message
        return recovered_plaintext_bytes.decode('utf-8')

    except FileNotFoundError as e:
        return f"File not found: {e}. Please ensure the file paths are correct."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- Main execution ---

# **IMPORTANT**: Use the actual CTF files.
PATH_TO_CIPHER1 = 'cipher1(1).bin'
PATH_TO_CIPHER2 = 'cipher2(1).bin'

# The known plaintext for the first packet, as provided in the challenge.
# Need to pad to exactly 96 bytes (adding 1 byte padding)
KNOWN_PLAINTEXT = "BEGIN TELEMETRY VIRELIA;ID=ZTRX0110393939DC;PUMP1=OFF;VALVE1=CLOSED;PUMP2=ON;VALVE2=CLOSED;END;" + "\x00"

# Run the solver function
recovered_message = solve_aes_gcm_nonce_reuse(PATH_TO_CIPHER1, PATH_TO_CIPHER2, KNOWN_PLAINTEXT)

print("\n--- AES-GCM Nonce Reuse Attack ---")
print(f"Known Plaintext 1:\n> {KNOWN_PLAINTEXT}")
print("\nAttempting to recover Plaintext 2...")
print("-" * 35)
print("Recovered Plaintext 2:")
print(f"> {recovered_message}")
print("-" * 35)