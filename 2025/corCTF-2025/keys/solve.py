from functools import reduce
import itertools

def xor(x, y):
    # Helper function to XOR two byte strings.
    return bytes([a ^ b for a, b in zip(x, y)])

def solve():
    # Attempts to decrypt the flag-enc.bmp file by exploiting the linear
    # keystream and guessing the background color.
    try:
        with open('flag-enc.bmp', 'rb') as f:
            d = f.read()
            # The encryption script separates the header from the image data.
            # The data is the last 3 * 1024 * 1024 bytes.
            header_size = len(d) - (1024 * 1024 * 3)
            header = d[:header_size]
            data = d[header_size:]
    except FileNotFoundError:
        print("Error: 'flag-enc.bmp' not found. Please place it in the same directory as the script.")
        return

    # Split the ciphertext data into 3-byte chunks (pixels)
    chunked_ciphertext = [data[i:i+3] for i in range(0, len(data), 3)]

    # --- GUESS THE BACKGROUND COLOR ---
    # Common colors to try:
    # Black: b'\x00\x00\x00'
    # White: b'\xff\xff\xff'
    # Red:   b'\x00\x00\xff'  (BMP is BGR)
    # Green: b'\x00\xff\x00'
    # Blue:  b'\xff\x00\x00'
    
    # Guessing the background is black.
    guessed_pixel = b'\x00\x00\x00'
    print(f"Attempting decryption with guessed background color: {guessed_pixel.hex()}")

    # --- RECONSTRUCT THE KEYSTREAM ---
    # We assume the pixels at indices 0, 1, 2, 4, ... are the background color.
    # From K_j = C_j ^ P_j, we can find the corresponding keys.
    C0 = chunked_ciphertext[0]
    K0_guess = xor(C0, guessed_pixel)

    # These are the basis vectors for the keystream generation
    Y_guess = []
    for i in range(20):
        # Index is a power of 2
        idx = 1 << i
        C_idx = chunked_ciphertext[idx]
        K_idx_guess = xor(C_idx, guessed_pixel)
        Y_i = xor(K0_guess, K_idx_guess)
        Y_guess.append(Y_i)

    # Generate the full keystream
    num_pixels = 1024 * 1024
    keystream = []
    for j in range(num_pixels):
        # The key K_j is a combination of the basis vectors Y_i
        # based on the binary representation of the index j.
        key_xor_part = b'\x00\x00\x00'
        for i in range(20):
            if (j >> i) & 1:
                key_xor_part = xor(key_xor_part, Y_guess[i])
        
        Kj = xor(K0_guess, key_xor_part)
        keystream.append(Kj)

    # --- DECRYPT THE IMAGE ---
    decrypted_pixels = []
    for i in range(num_pixels):
        decrypted_pixel = xor(chunked_ciphertext[i], keystream[i])
        decrypted_pixels.append(decrypted_pixel)

    # --- SAVE THE RESULT ---
    output_filename = 'flag-dec.bmp'
    with open(output_filename, 'wb') as f:
        f.write(header)
        f.write(b''.join(decrypted_pixels))

    print(f"Decryption complete. Result saved to '{output_filename}'")
    print("Please check the image to see if the flag is visible.")

solve()