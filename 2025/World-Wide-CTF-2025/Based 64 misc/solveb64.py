import base64
import sys

def extract_flag_from_b64(data: str) -> str:
    """
    Extracts a hidden message from a specific Base64 steganography scheme.

    The scheme hides one hex nibble (4 bits) in the lower 4 bits of the
    index of the second character of any Base64 string representing a
    single byte (i.e., lines ending with '==').
    """
    # Use the standard Base64 character set for clarity.
    B64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    
    hex_nibbles = []
    
    # Process each line from the input data.
    for line in data.strip().splitlines():
        line = line.strip()
        
        # The core logic: only process lines that are padded for a single byte.
        if len(line) == 4 and line.endswith("=="):
            second_char = line[1]
            try:
                # Find the 6-bit value (0-63) of the second character.
                char_index = B64_ALPHABET.index(second_char)
                
                # The hidden data is stored in the lower 4 bits (nibble).
                # A bitwise AND with 15 (0b1111) isolates these bits.
                hidden_nibble = char_index & 0b1111
                
                # Convert the nibble to its hex character representation.
                hex_nibbles.append(f"{hidden_nibble:x}")
                
            except ValueError:
                # Handle cases where a character is not in the Base64 alphabet.
                print(f"Warning: Invalid character '{second_char}' in line '{line}'.", file=sys.stderr)
                continue

    # Join the list of nibbles into a single hexadecimal string.
    hex_string = "".join(hex_nibbles)
    
    # Decode the hex string to reveal the final message.
    try:
        return bytes.fromhex(hex_string).decode('utf-8')
    except (ValueError, UnicodeDecodeError):
        return "Error: Failed to decode the extracted hex string."

# The CTF data provided in the original script.
ctf_data = """
U3==
T3==
Un==
Un==
WW==
IG==
VH==
SL==
RX==
Ul==
RW==
IO==
SV==
U1==
IH==
Tj==
Tz==
ID==
Rm==
TE==
QV==
R/==
IG==
VC==
Tz==
IB==
Qn==
RU==
IH==
Rj==
T1==
Vf==
Tj==
RD==
IH==
SB==
RX==
Ul==
RT==
Lk==
IG==
UM==
TH==
Ra==
QV==
U/==
RX==
ID==
RH==
T0==
ID==
Tj==
T2==
VH==
ID==
Qw==
T1==
Tv==
VG==
SW==
Tn==
VV==
RW==
IO==
TH==
T9==
Tw==
Sw==
SQ==
Tg==
Ry4=
"""

# Standard main execution block.
if __name__ == "__main__":
    extracted_message = extract_flag_from_b64(ctf_data)
    print(f"Decoded Message: {extracted_message}")