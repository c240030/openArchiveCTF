import struct

def solve():
    try:
        with open('flag.fshr', 'rb') as f:
            encoded_data = f.read()
    except FileNotFoundError:
        print("Error: File flag.fshr not found!")
        return

    decoded_output = bytearray()

    for i in range(0, len(encoded_data), 2):
        if i + 1 >= len(encoded_data):
            break

        token = encoded_data[i]
        literal = encoded_data[i+1]

        length = token & 0b111
        distance = token >> 3

        if length > 0:
            start_index = len(decoded_output) - distance
            for _ in range(length):
                if start_index < len(decoded_output):
                    char_to_copy = decoded_output[start_index]
                    decoded_output.append(char_to_copy)
                    start_index += 1
                else:
                    decoded_output.append(0)

        decoded_output.append(literal)

    print("-" * 30)
    print("FLAG FOUND:")
    print("-" * 30)
    try:
        print(decoded_output.decode('utf-8'))
    except UnicodeDecodeError:
        print("Raw bytes (not plain text):")
        print(decoded_output)
    print("-" * 30)
    
    with open('flag_decoded.txt', 'wb') as f:
        f.write(decoded_output)
        print("Flag saved to file: flag_decoded.txt")

if __name__ == "__main__":
    solve()