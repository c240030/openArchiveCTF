import re
import socket
import sys
import time

HOST = "65.109.194.34"
PORT = 33331


def solve():
    print(f"[+] Connecting to {HOST}:{PORT}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
    except Exception as e:
        print(f"[-] Failed to connect: {e}")
        return False

    recv_buffer = ""

    def read_until(marker):
        nonlocal recv_buffer
        while marker not in recv_buffer:
            try:
                chunk = s.recv(4096).decode()
                if not chunk:
                    return None
                recv_buffer += chunk
            except Exception:
                return None

        idx = recv_buffer.find(marker) + len(marker)
        result = recv_buffer[:idx]
        recv_buffer = recv_buffer[idx:]
        return result

    def send(text):
        try:
            s.sendall((str(text) + "\n").encode())
        except:
            return False
        return True

    if not read_until("e[X]it"):
        print("[-] Failed to read banner.")
        return False

    core = [None] * 64
    pivot_idx = None

    print("[*] Connected. Starting attack...")

    while None in core:
        send("r")
        read_until("Input (hex):")
        send("0")

        response = read_until("e[X]it")
        if not response:
            return False

        match = re.search(r"Reflection:\s+([a-fA-F0-9]+)", response)
        if not match:
            print("[-] Error: Could not get Enc(0)")
            return False
        enc_zero = match.group(1)

        if pivot_idx is None:
            print(f"[*] Scanning for Pivot (Focus)...")
            for i in range(34):
                if core[i] is not None:
                    continue

                send("q")
                read_until("Entry (hex):")
                send(enc_zero)
                read_until("Delta:")
                send(str(i - 32))

                res = read_until("e[X]it")
                if not res:
                    return False

                if "ALIGNMENT FOUND" in res:
                    print(f"[+] BINGO! Found Pivot at index {i}. (Reset Attempts)")
                    pivot_idx = i
                    break
                elif "Trace:" in res:
                    pass
                elif "Attempts depleted" in res:
                    print("[-] Out of attempts while finding Pivot.")
                    return False
            else:
                print("[-] Scanned all 34 positions but no Pivot found. (Unlucky)")
                return False

        else:
            unknowns = [x for x in range(64) if core[x] is None and x != pivot_idx]

            if not unknowns and core[pivot_idx] is None:
                print(
                    f"[*] Only Pivot ({pivot_idx}) remains. Performing SHIFT to decrypt..."
                )

                send("s")
                read_until("e[X]it")

                send("q")
                read_until("Entry (hex):")
                send(enc_zero)
                read_until("Delta:")
                send(str(pivot_idx - 32))

                res = read_until("e[X]it")
                match = re.search(r"Trace:\s+([a-fA-F0-9]+)", res)
                if not match:
                    return False
                enc_val = match.group(1)

                send("r")
                read_until("Input (hex):")
                send(enc_val)
                res = read_until("e[X]it")
                match = re.search(r"Reflection:\s+(\d+)", res)
                if match:
                    val = int(match.group(1))
                    core[pivot_idx] = val
                    print(f"[*] Decrypted Pivot: {val}")
                break

            batch = unknowns[:3]
            if not batch:
                break

            print(f"[*] Decrypting batch: {batch}")
            for idx in batch:
                send("q")
                read_until("Entry (hex):")
                send(enc_zero)
                read_until("Delta:")
                send(str(idx - 32))

                res = read_until("e[X]it")
                match = re.search(r"Trace:\s+([a-fA-F0-9]+)", res)
                if not match:
                    continue
                enc_val = match.group(1)

                send("r")
                read_until("Input (hex):")
                send(enc_val)

                res = read_until("e[X]it")
                match = re.search(r"Reflection:\s+(\d+)", res)
                if match:
                    core[idx] = int(match.group(1))

            send("q")
            read_until("Entry (hex):")
            send(enc_zero)
            read_until("Delta:")
            send(str(pivot_idx - 32))
            res = read_until("e[X]it")
            if "ALIGNMENT FOUND" not in res:
                print("[-] Error: Failed to restore health!")
                return False

    print("[*] Found all 64 numbers. Sending Core key...")
    send("c")
    read_until("Core key:")
    send(bytes(core).hex())

    final_res = read_until("}")

    print("\n" + "=" * 60)
    if "UNLOCKED" in final_res:
        flag = re.search(r"UNLOCKED:\s+(.+)", final_res).group(1)
        print(f"FLAG: {flag}")
    else:
        print("Raw Output:")
        print(final_res)
    print("=" * 60 + "\n")

    s.close()
    return True


if __name__ == "__main__":
    attempt = 1
    while True:
        print(f"\n--- REMOTE ATTEMPT {attempt} ---")
        if solve():
            break
        attempt += 1
        time.sleep(1)
