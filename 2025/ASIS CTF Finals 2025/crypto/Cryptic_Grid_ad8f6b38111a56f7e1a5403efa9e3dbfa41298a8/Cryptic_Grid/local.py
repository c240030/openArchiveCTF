import os
import queue
import random
import sys
import threading
import time

try:
    from Crypto.Cipher import AES
except ImportError:
    print("[ERROR] Missing library. Run: pip install pycryptodome")
    sys.exit(1)

FAKE_FLAG = "CTX{7h3_p47h_0f_7h3_h1dd3n_k3y5}"

input_queue = queue.Queue()
output_queue = queue.Queue()


class ChallengeGame:
    def __init__(self):
        self.key = None
        self.MAX_ATTEMPTS = 0b101010
        self.core = list(range(0x40))
        random.shuffle(self.core)
        self.core = bytes(self.core)
        self.focus = random.randint(0, 0x3F)
        self.attempts = self.MAX_ATTEMPTS
        self.grid = {}

    def pr(self, *args):
        s = " ".join(map(str, args))
        output_queue.put(s + "\n")

    def sc(self):
        return input_queue.get()

    def die(self, *args):
        self.pr(*args)
        raise SystemExit("Game Over")

    def wrap(self, data, mode=True):
        try:
            c = AES.new(self.key, AES.MODE_ECB)
            if mode:
                return c.encrypt(int(data).to_bytes(0x10, "big")).hex()
            else:
                return int.from_bytes(c.decrypt(bytes.fromhex(data)), "big")
        except Exception:
            return None

    def build_grid(self):
        self.key = os.urandom(16)
        self.grid = {self.wrap(i): self.wrap(self.core[i]) for i in range(0x40)}

    def run(self):
        try:
            border = "┃"
            self.pr("┏" + "━" * 47 + "┓")
            self.pr(border, "  .::  THE CRYPTIC GRID OF HIDDEN PATHS  ::. ", border)
            self.build_grid()

            while self.MAX_ATTEMPTS >= self.attempts > 0:
                self.pr(border, f"Attempts: {self.attempts}")
                self.pr(border, "[C]heck [Q]uery [R]eflect [S]hift e[X]it")
                cmd = self.sc().strip().lower()

                if cmd == "s":
                    self.attempts -= 1
                    self.focus = (self.focus * 5 + 3) & 0x3F
                    self.pr(border, f"Focus pulse: {self.focus}")

                elif cmd == "q":
                    self.attempts -= 1
                    self.pr(border, "Entry (hex):")
                    entry = self.sc().strip()
                    self.pr(border, "Delta:")
                    delta = int(self.sc().strip())

                    dec_entry = self.wrap(entry, False)
                    if dec_entry is None:
                        dec_entry = 0

                    idx = (dec_entry + delta + 0x20) & 0x3F
                    enc_idx = self.wrap(idx)
                    out = self.grid.get(enc_idx)

                    if out and self.wrap(out, False) == self.focus:
                        self.pr(border, f"ALIGNMENT FOUND at {idx}")
                        self.attempts = self.MAX_ATTEMPTS
                        self.build_grid()
                    else:
                        self.pr(border, f"Trace: {out}")

                elif cmd == "r":
                    self.attempts -= 8
                    self.pr(border, "Input (hex):")
                    inp = self.sc().strip()[:0x20]
                    is_encrypt = len(inp) < 0x20
                    self.pr(border, f"Reflection: {self.wrap(inp, is_encrypt)}")

                elif cmd == "c":
                    self.pr(border, "Core key:")
                    try:
                        attempt_core = bytes.fromhex(self.sc().strip())
                    except:
                        attempt_core = b""
                    if attempt_core == self.core:
                        self.die(border, f"UNLOCKED: {FAKE_FLAG}")
                    else:
                        self.die(border, "REJECTED")
                elif cmd == "x":
                    self.die(border, "Vanishing into the void...")
                else:
                    self.pr(border, "Invalid")
            self.die(border, "Attempts depleted.")
        except SystemExit:
            pass
        except Exception as e:
            output_queue.put(f"GAME_CRASH: {e}\n")


def run_solver():
    print("[Solver] Starting solve...")

    def send(line):
        input_queue.put(str(line))

    def read_until(txt):
        buffer = ""
        while True:
            line = output_queue.get()
            buffer += line
            if txt in buffer:
                return buffer
            if "Attempts depleted" in line or "GAME_CRASH" in line:
                return None

    core = [None] * 64
    pivot_idx = None

    if not read_until("e[X]it"):
        return False

    while None in core:
        send("r")
        read_until("Input (hex):")
        send("0")
        buff = read_until("Reflection: ")
        if not buff:
            return False
        enc_zero = buff.split("Reflection: ")[1].strip()
        if not read_until("e[X]it"):
            return False

        if pivot_idx is None:
            print(f"[*] Scanning for Pivot...")
            for i in range(34):
                if core[i] is not None:
                    continue

                send("q")
                read_until("Entry (hex):")
                send(enc_zero)
                read_until("Delta:")
                send(str(i - 32))

                res = read_until("[C]heck")
                if not res:
                    return False

                if "ALIGNMENT FOUND" in res:
                    print(f"[+] Found Pivot at index {i}! (Health restored)")
                    pivot_idx = i
                    break
                elif "Trace:" in res:
                    pass
                elif "Attempts depleted" in res:
                    return False
            else:
                return False

        else:
            unknowns = [x for x in range(64) if core[x] is None and x != pivot_idx]

            if not unknowns and core[pivot_idx] is None:
                print(f"[*] Only Pivot ({pivot_idx}) remains. Using Shift to decrypt...")
                send("s")
                read_until("Focus pulse:")
                read_until("e[X]it")

                send("q")
                read_until("Entry (hex):")
                send(enc_zero)
                read_until("Delta:")
                send(str(pivot_idx - 32))

                buff = read_until("Trace: ")
                enc_val = buff.split("Trace: ")[1].strip()
                read_until("e[X]it")

                send("r")
                read_until("Input (hex):")
                send(enc_val)
                buff = read_until("Reflection: ")
                dec_val = int(buff.split("Reflection: ")[1].strip())
                read_until("e[X]it")

                core[pivot_idx] = dec_val
                print(f"[*] Decrypted Pivot: {dec_val}")
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

                buff = read_until("Trace: ")
                enc_val = buff.split("Trace: ")[1].strip()
                read_until("e[X]it")

                send("r")
                read_until("Input (hex):")
                send(enc_val)
                buff = read_until("Reflection: ")
                dec_val = int(buff.split("Reflection: ")[1].strip())
                read_until("e[X]it")

                core[idx] = dec_val

            send("q")
            read_until("Entry (hex):")
            send(enc_zero)
            read_until("Delta:")
            send(str(pivot_idx - 32))
            res = read_until("[C]heck")
            if "ALIGNMENT FOUND" not in res:
                return False

    print("[*] Found all 64 numbers. Sending flag...")
    send("c")
    read_until("Core key:")
    send(bytes(core).hex())
    final = read_until("}")

    print("\n" + "=" * 60)
    print(final)
    print("=" * 60 + "\n")
    return True


if __name__ == "__main__":
    attempt = 1
    while True:
        with input_queue.mutex:
            input_queue.queue.clear()
        with output_queue.mutex:
            output_queue.queue.clear()

        print(f"\n--- RUN #{attempt} ---")
        game = ChallengeGame()
        t = threading.Thread(target=game.run)
        t.daemon = True
        t.start()

        if run_solver():
            break
        attempt += 1
        time.sleep(0.5)
