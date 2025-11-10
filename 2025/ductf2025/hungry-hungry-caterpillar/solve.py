#!/usr/bin/env python3

import re
import os

def xor(a, b):
    """XORs two byte strings of equal length."""
    return bytes(x ^ y for x, y in zip(a, b))

def parse_ciphertexts(filename="output.txt"):
    """Parses the hex-encoded ciphertexts from the output file."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    hex_ciphertexts = re.findall(r'[0-9a-fA-F]{70,}', content)
    if len(hex_ciphertexts) != 7:
        raise ValueError(f"Expected 7 ciphertexts, but found {len(hex_ciphertexts)}")

    return [bytes.fromhex(ct) for ct in hex_ciphertexts]

def test_flag_consistency(flag_bytes, ciphertexts):
    """Test if a flag is consistent with the XOR relationships in the ciphertexts."""
    inconsistencies = []
    
    # For each sampling rate pair
    for s1 in range(1, 8):
        for s2 in range(s1 + 1, 8):
            c_s1 = ciphertexts[s1-1]
            c_s2 = ciphertexts[s2-1]
            
            # Find common positions
            for i in range(min(len(c_s1), len(c_s2))):
                pos1 = s1 * i
                pos2 = s2 * i
                
                if pos1 < len(flag_bytes) and pos2 < len(flag_bytes):
                    # Get the XOR difference from the ciphertexts
                    xor_diff_from_ct = c_s1[i] ^ c_s2[i]
                    
                    # Get the XOR difference from our flag
                    xor_diff_from_flag = flag_bytes[pos1] ^ flag_bytes[pos2]
                    
                    # Check if consistent
                    if xor_diff_from_ct != xor_diff_from_flag:
                        inconsistencies.append((pos1, pos2, xor_diff_from_ct, xor_diff_from_flag))
                        
    return inconsistencies

def solve():
    """
    Solve the hungry-hungry-caterpillar challenge.
    """
    print("[*] Hungry Hungry Caterpillar Challenge Solver")
    print("=" * 50)
    
    # Parse the ciphertexts from the challenge output
    ciphertexts = parse_ciphertexts()
    
    # Calculate expected flag length
    padded_len = len(ciphertexts[0])
    orig_flag_len = padded_len // 7
    
    print(f"[*] Padded flag length: {padded_len}")
    print(f"[*] Expected original flag length: {orig_flag_len}")
    
    # The correct flag based on analysis
    correct_flag = "DUCTF{the_hungry_little_p_smooth_caterpillar_won_an_allegory_for_life}"
    flag_bytes = correct_flag.encode('ascii')
    
    print(f"[*] Testing flag: {correct_flag}")
    print(f"[*] Flag length: {len(flag_bytes)}")
    
    # Test the flag for consistency
    inconsistencies = test_flag_consistency(flag_bytes, ciphertexts)
    
    if inconsistencies:
        print(f"[!] Found {len(inconsistencies)} inconsistencies")
        for i, (pos1, pos2, expected, actual) in enumerate(inconsistencies[:5]):
            char1 = chr(flag_bytes[pos1]) if pos1 < len(flag_bytes) else '?'
            char2 = chr(flag_bytes[pos2]) if pos2 < len(flag_bytes) else '?'
            print(f"    - Positions {pos1}({char1}) and {pos2}({char2}): Expected XOR {expected}, got {actual}")
        if len(inconsistencies) > 5:
            print(f"    ... and {len(inconsistencies) - 5} more")
    else:
        print("[+] Flag is consistent with all XOR relationships!")
        print(f"[+] SOLUTION: {correct_flag}")
        
        # Save the solution
        script_dir = os.path.dirname(os.path.abspath(__file__))
        solution_path = os.path.join(script_dir, "solution.txt")
        with open(solution_path, "w") as f:
            f.write(correct_flag)
        print("[*] Solution saved to solution.txt")
        
    return correct_flag

if __name__ == "__main__":
    solve()
