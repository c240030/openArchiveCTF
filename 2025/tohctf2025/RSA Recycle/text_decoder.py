#!/usr/bin/env python3
"""
Text Decoder for RSA Recycle Challenge
Converts decrypted integer to various text formats
"""

def int_to_8bit_text(m):
    """Convert integer to standard 8-bit ASCII text"""
    try:
        bits = bin(m)[2:]
        # Pad to multiple of 8
        bits = bits.zfill((len(bits) + 7) // 8 * 8)
        result = ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))
        return result
    except (ValueError, OverflowError):
        return "Cannot decode as 8-bit ASCII"

def int_to_7bit_text(m):
    """Convert integer to 7-bit ASCII text (used in this challenge)"""
    try:
        bits = bin(m)[2:]
        # Pad to multiple of 7
        bits = bits.zfill((len(bits) + 6) // 7 * 7)
        result = ''.join(chr(int(bits[i:i+7], 2)) for i in range(0, len(bits), 7))
        return result
    except (ValueError, OverflowError):
        return "Cannot decode as 7-bit ASCII"

def int_to_6bit_text(m):
    """Convert integer to 6-bit text (base64-like)"""
    try:
        bits = bin(m)[2:]
        # Pad to multiple of 6
        bits = bits.zfill((len(bits) + 5) // 6 * 6)
        result = ''.join(chr(int(bits[i:i+6], 2) + 32) for i in range(0, len(bits), 6) if int(bits[i:i+6], 2) + 32 < 127)
        return result
    except (ValueError, OverflowError):
        return "Cannot decode as 6-bit text"

def int_to_hex_string(m):
    """Convert integer to hexadecimal string"""
    hex_str = hex(m)[2:]
    if len(hex_str) % 2 == 1:
        hex_str = '0' + hex_str
    try:
        result = bytes.fromhex(hex_str).decode('ascii', errors='ignore')
        return result
    except:
        return f"Hex: {hex_str}"

def int_to_base64_decode(m):
    """Try to interpret as base64 encoded data"""
    import base64
    try:
        hex_str = hex(m)[2:]
        if len(hex_str) % 2 == 1:
            hex_str = '0' + hex_str
        data = bytes.fromhex(hex_str)
        # Try to decode as base64
        decoded = base64.b64decode(data).decode('ascii', errors='ignore')
        return decoded
    except:
        return "Cannot decode as base64"

def analyze_integer_patterns(m):
    """Analyze the integer for common patterns"""
    print(f"Integer: {m}")
    print(f"Bit length: {m.bit_length()}")
    print(f"Hex: {hex(m)}")
    print(f"Binary (first 64 bits): {bin(m)[:66]}...")
    print()

def try_all_decodings(m):
    """Try all possible text decodings"""
    print("="*60)
    print("RSA RECYCLE - TEXT DECODER")
    print("="*60)
    
    analyze_integer_patterns(m)
    
    print("DECODING ATTEMPTS:")
    print("-" * 40)
    
    # 7-bit decoding (most likely for this challenge)
    result_7bit = int_to_7bit_text(m)
    print(f"7-bit ASCII: {result_7bit}")
    
    # 8-bit decoding
    result_8bit = int_to_8bit_text(m)
    print(f"8-bit ASCII: {result_8bit}")
    
    # 6-bit decoding
    result_6bit = int_to_6bit_text(m)
    print(f"6-bit text:  {result_6bit}")
    
    # Hex string
    result_hex = int_to_hex_string(m)
    print(f"Hex string:  {result_hex}")
    
    # Base64 attempt
    result_b64 = int_to_base64_decode(m)
    print(f"Base64:      {result_b64}")
    
    print("-" * 40)
    
    # Check for flag patterns
    potential_flags = [result_7bit, result_8bit, result_6bit, result_hex, result_b64]
    for i, result in enumerate(potential_flags):
        if any(flag_format in result.lower() for flag_format in ['flag{', 'toh{', 'ctf{', '_{', '}']) and len(result) > 10:
            formats = ['7-bit', '8-bit', '6-bit', 'hex', 'base64']
            print(f"🚩 POTENTIAL FLAG FOUND in {formats[i]}: {result}")
    
    return result_7bit  # Return the most likely result

def main():
    """Main function for standalone testing"""
    # Test with the decrypted integer from the RSA challenge
    test_integer = 3812639487317588278587438626619393202717034828070805675410227659806456269102541209288435765865997262933379159578025636045381432418107041608830035856816637
    
    result = try_all_decodings(test_integer)
    print(f"\nMost likely result: {result}")

if __name__ == "__main__":
    main()
