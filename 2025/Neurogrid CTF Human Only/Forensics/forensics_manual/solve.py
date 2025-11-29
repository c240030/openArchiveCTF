import base64
import re
import sys


def solve():
    filename = "challenge.bat"

    try:
        with open(filename, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[-] No file '{filename}'")
        return

    print("[*] Analyzing...")

    var_pattern = re.compile(r"!qoz!\s+([^=]+)=(.*)")
    variables = {}
    lines = content.splitlines()

    for line in lines:
        match = var_pattern.search(line)
        if match:
            raw_name = match.group(1)
            value = match.group(2).strip()
            clean_name = re.sub(r"%[^%]+%", "", raw_name).strip()
            variables[clean_name] = value

    max_percent_line = ""
    if lines:
        max_percent_line = max(lines, key=lambda l: l.count("%"))

    execution_order = re.findall(r"%([^%]+)%", max_percent_line)

    full_cmd = ""
    for var in execution_order:
        if var in variables:
            full_cmd += variables[var]
        else:
            pass

    print(f"[*] Re-created the command (Preview): {full_cmd[:80]}...")

    payload_match = re.search(r"\$s='(.*?)'", full_cmd)

    if not payload_match:
        print("[-] Error: No pattern $s='...' in the the command")
        print("    Something is wrong")
        return

    raw_base64 = payload_match.group(1)

    garbage = "djlrttmeqqkr"
    clean_base64 = raw_base64.replace(garbage, "")

    print(f"[*] Extracted and cleaned Base64 ({len(clean_base64)} chars).")

    try:
        decoded_bytes = base64.b64decode(clean_base64)
        powershell_script = decoded_bytes.decode("utf-16le")
        print("\n[+] --- Solved:D ---\n")
        print(powershell_script)

        flag = re.search(r"HTB\{[^}]+\}", powershell_script)
        if flag:
            print(f"\n\n[!!!] FLAG FOUND: {flag.group(0)}")
        else:
            print("\n[-] No flag format pattern in the script")

    except Exception as e:
        print(f"\n[!] Decode error: {e}")


if __name__ == "__main__":
    solve()
