import gdb

def solve():
    gdb.execute("set pagination off")
    gdb.execute("set confirm off")
    
    try:
        gdb.execute("start", to_string=True)
    except Exception:
        return

    inferior = gdb.selected_inferior()

    try:
        sigma_addr = gdb.parse_and_eval("&sigma_words")
        real_key = inferior.read_memory(sigma_addr, 16).tobytes()

        enc_addr = gdb.parse_and_eval("&flag_enc")
        real_cipher = inferior.read_memory(enc_addr, 18).tobytes()
    except Exception:
        return

    flag_content = ""
    for i in range(len(real_cipher)):
        c = real_cipher[i]
        k = real_key[i % 16] 
        p = (c ^ (i + k)) & 0xFF
        flag_content += chr(p)

    print(f"SECCON{{{flag_content}}}")
    gdb.execute("quit")

if __name__ == "__main__":
    solve()

# To run: gdb -q -x solve.py ./chall