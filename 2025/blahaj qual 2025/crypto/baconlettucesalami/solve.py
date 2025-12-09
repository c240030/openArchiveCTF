import subprocess

from pwn import *

HOST = "crypto-baconlettucesalami.chals.blahaj.sg"
PORT = 30044
context.log_level = "error"


def attack(i):
    print(f"[*] Attempt {i}...")
    try:
        r = remote(HOST, PORT)
        r.recvuntil(b"My public key is ", timeout=60)
        alice = r.recvline().strip().decode()
        r.recvuntil(b"mine's ")
        bob = r.recvline().strip().decode()
        r.recvuntil(b"[You] ")
        charlie = r.recvline().strip().decode()

        proc = subprocess.run(
            ["sage", "rogue.sage", alice, bob, charlie], capture_output=True, text=True
        )
        if "Error" in proc.stderr:
            return False
        rx, ry = proc.stdout.strip().split("|")

        r.sendlineafter(b"> ", b"3")
        r.sendlineafter(b"commas\n> ", rx.encode())
        r.sendlineafter(b"commas\n> ", ry.encode())

        r.sendlineafter(b"> ", b"1")
        r.sendlineafter(b"message > ", b"We'll give the flag entirely to Charlie")

        r.sendlineafter(b"> ", b"4")
        r.sendlineafter(b"id\n> ", b"0")

        res = r.recvall(timeout=3).decode()
        r.close()

        if "blahaj{" in res:
            print("\n" + "=" * 40)
            print(res)
            return True
    except:
        pass
    return False


i = 1
while True:
    if attack(i):
        break
    i += 1
