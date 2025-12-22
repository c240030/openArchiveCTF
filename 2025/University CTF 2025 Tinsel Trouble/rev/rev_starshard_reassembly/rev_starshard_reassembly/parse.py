#!/usr/bin/env python3
import re
import os

def parse_flag_from_asm(filename):
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    flag_chars = {}
    pattern = r'main__ptr_R(\d+)_Expected\s+proc.*?mov\s+eax,\s+([0-9A-Fa-f]+)h'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        index = int(match[0])
        char_code = int(match[1], 16)
        flag_chars[index] = chr(char_code)
    
    if flag_chars:
        max_index = max(flag_chars.keys())
        flag = ''.join(flag_chars.get(i, '?') for i in range(max_index + 1))
        return flag
    return None

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    asm_file = os.path.join(script_dir, "memory_minder.asm")
    flag = parse_flag_from_asm(asm_file)
    print(f"FLAG: {flag}")
