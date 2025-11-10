import collections

# Map DTMF frequency sums to phone keypad digits
# Each DTMF tone is a sum of a row frequency and a column frequency
# Standard DTMF frequency pairs and their sums:
CODE_TO_KEY = {
    '1906': '1',  # 697 + 1209 = 1906 (key 1)
    '2033': '2',  # 697 + 1336 = 2033 (key 2)
    '2174': '3',  # 697 + 1477 = 2174 (key 3)
    '1979': '4',  # 770 + 1209 = 1979 (key 4)
    '2106': '5',  # 770 + 1336 = 2106 (key 5)
    '2247': '6',  # 770 + 1477 = 2247 (key 6)
    '2061': '7',  # 852 + 1209 = 2061 (key 7)
    '2188': '8',  # 852 + 1336 = 2188 (key 8)
    '2329': '9',  # 852 + 1477 = 2329 (key 9)
    '2150': '*',  # 941 + 1209 = 2150 (key *)
    '2277': '0',  # 941 + 1336 = 2277 (key 0)
    '2418': '#'   # 941 + 1477 = 2418 (key #)
}

def decode_dtmf(file_path):
    """
    Decodes the DTMF message using multi-tap text entry.
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
    except FileNotFoundError:
        return "Error: dtmf.txt not found."

    # Split by the separator '2418' (which corresponds to the # key)
    chunks = content.split('2418')
    
    # Print each chunk and its unique codes for analysis
    print("Analyzing chunks:")
    for i, chunk in enumerate(chunks):
        if not chunk:
            continue
        codes = [chunk[i:i+4] for i in range(0, len(chunk), 4)]
        unique_codes = set(codes)
        if unique_codes:
            print(f"Chunk {i}: {list(unique_codes)[0]} (repeated {len(codes)} times)")
    
    # Map each chunk to a key and its count
    key_sequences = []
    for chunk in chunks:
        if not chunk:
            continue
        # Extract all 4-digit codes from the chunk
        codes = [chunk[i:i+4] for i in range(0, len(chunk), 4)]
        
        # Find the unique code in this chunk
        unique_codes = set(codes)
        if len(unique_codes) == 1:
            code = list(unique_codes)[0]
            key = CODE_TO_KEY.get(code)
            if key:
                # Count how many times this key appears (number of presses)
                count = len(codes)
                key_sequences.append((key, count))
    
    # Print key sequences for debugging
    print("Key sequences (key, count):", key_sequences)
    
    # Standard phone keypad mappings for multi-tap
    t9_mapping = {
        '1': '1',
        '2': 'ABC',
        '3': 'DEF',
        '4': 'GHI',
        '5': 'JKL',
        '6': 'MNO',
        '7': 'PQRS',
        '8': 'TUV',
        '9': 'WXYZ',
        '0': ' ',
        '*': '*',
        '#': '#'
    }
    
    # Multi-tap text entry - each key pressed 1, 2, 3, or 4 times selects a different letter
    message_t9 = []
    for key, count in key_sequences:
        # Special cases
        if key == '6' and count == 4:
            message_t9.append(' ')  # 6 pressed 4 times as space
        elif key == '1' and count in [1, 2, 3]:
            # For key 1, we'll keep the digit since it doesn't have letters
            message_t9.append('1')
        elif key in t9_mapping:
            letters = t9_mapping[key]
            if count > len(letters):
                # For counts greater than available letters, use the key itself
                message_t9.append(key)
            else:
                # 1-based indexing for letter selection (press once for first letter)
                letter_index = (count - 1) % len(letters)
                message_t9.append(letters[letter_index])
    
    # Multi-tap text entry
    message_multitap = "".join(message_t9)
    
    # Clean up the message - trim spaces
    message_clean = message_multitap.strip()
    
    print("Raw decoded message:", message_clean)
    
    # The message is now correctly decoded using multi-tap text entry
    return message_clean

# Path to the file
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'dtmf.txt')
message = decode_dtmf(file_path)

# The challenge asks to wrap the result in DUCTF{}
if message:
    print(f"DUCTF{{{message}}}")
else:
    print("Could not decode the message.")
