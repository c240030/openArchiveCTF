#!/usr/bin/env python3
import argparse
import math
import queue
import subprocess
import sys
import threading
import time

try:
    from pwn import process, remote

    HAVE_PWN = True
except Exception:
    HAVE_PWN = False

try:
    from Crypto.Util.number import bytes_to_long, long_to_bytes
except Exception:

    def bytes_to_long(b: bytes) -> int:
        return int.from_bytes(b, "big")

    def long_to_bytes(n: int, k: int = None) -> bytes:
        if n == 0:
            out = b"\x00"
        else:
            length = (n.bit_length() + 7) // 8
            out = n.to_bytes(length, "big")
        if k is not None:
            return out.rjust(k, b"\x00")
        return out


PROMPT = b"> "
MOD64 = 1 << 64


def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def chunk_u64_be(b: bytes):
    assert len(b) % 8 == 0
    return [int.from_bytes(b[i : i + 8], "big") for i in range(0, len(b), 8)]


class IOBase:
    def sendline(self, data: bytes):
        raise NotImplementedError

    def recvuntil(self, token: bytes, timeout: float = 5.0) -> bytes:
        raise NotImplementedError


class PwntoolsIO(IOBase):
    def __init__(self, tube):
        self.tube = tube

    def sendline(self, data: bytes):
        self.tube.sendline(data)

    def recvuntil(self, token: bytes, timeout: float = 5.0) -> bytes:
        return self.tube.recvuntil(token, timeout=timeout)


class SubprocessIO(IOBase):
    def __init__(self, argv):
        self.proc = subprocess.Popen(
            argv,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0,
        )
        self.q = queue.Queue()
        self.t = threading.Thread(target=self._reader, daemon=True)
        self.t.start()

    def _reader(self):
        while True:
            chunk = self.proc.stdout.read(1)
            if not chunk:
                break
            self.q.put(chunk)

    def sendline(self, data: bytes):
        if not data.endswith(b"\n"):
            data += b"\n"
        self.proc.stdin.write(data)
        self.proc.stdin.flush()

    def recvuntil(self, token: bytes, timeout: float = 5.0) -> bytes:
        deadline = time.time() + timeout
        buf = b""
        while time.time() < deadline:
            try:
                part = self.q.get(timeout=deadline - time.time())
                buf += part
                if buf.endswith(token):
                    return buf
            except queue.Empty:
                break
        return buf


def get_menu(io: IOBase):
    io.recvuntil(PROMPT)


def get_enc_flag_and_n(io: IOBase):
    io.sendline(b"1")
    data = io.recvuntil(PROMPT)
    lines = [l for l in data.splitlines() if l.strip()]
    enc_hex = None
    n_val = None
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if n_val is None and line.isdigit():
            n_val = int(line)
            continue
        if enc_hex is None:
            try:
                _ = bytes.fromhex(line.decode())
                enc_hex = line.decode()
                break
            except Exception:
                continue
    if enc_hex is None or n_val is None:
        raise RuntimeError("Failed to parse enc_flag or n from server output")
    return bytes.fromhex(enc_hex), n_val


def get_enc_mod_p(io: IOBase, payload: bytes) -> bytes:
    io.sendline(b"2")
    _ = io.recvuntil(b"> ")
    io.sendline(payload)
    data = io.recvuntil(PROMPT)
    lines = [l for l in data.splitlines() if l.strip()]
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        try:
            out = bytes.fromhex(line.decode())
            return out
        except Exception:
            continue
    raise RuntimeError("Failed to get hex output from option 2")


def recover_lcg_params(states: list[int]):
    for i in range(len(states) - 2):
        x1, x2, x3 = states[i], states[i + 1], states[i + 2]
        d = (x2 - x1) % MOD64
        if d % 2 == 0:
            continue
        inv_d = pow(d, -1, MOD64)
        a = ((x3 - x2) % MOD64) * inv_d % MOD64
        c = (x2 - (a * x1) % MOD64) % MOD64
        ok = True
        for j in range(i, min(i + 5, len(states) - 1)):
            if states[j + 1] != (a * states[j] + c) % MOD64:
                ok = False
                break
        if ok:
            return a, c
    raise RuntimeError("Failed to recover LCG parameters; collect more states")


def backward_state(x_next: int, a: int, c: int) -> int:
    inv_a = pow(a, -1, MOD64)
    return (inv_a * ((x_next - c) % MOD64)) % MOD64


def forward_state(x_curr: int, a: int, c: int) -> int:
    return (a * x_curr + c) % MOD64


def build_keystream_from_states(states: list[int]) -> bytes:
    out = b""
    for x in states:
        out += x.to_bytes(8, "big")
    return out


def solve(io: IOBase):
    get_menu(io)
    enc_flag, n = get_enc_flag_and_n(io)
    states_after_flag = []

    def fetch_zero_chunk():
        out = get_enc_mod_p(io, b"")
        if len(out) % 8 != 0:
            raise RuntimeError("Unexpected keystream length (not multiple of 8)")
        return chunk_u64_be(out)

    while len(states_after_flag) < 8:
        states_after_flag += fetch_zero_chunk()

    a, c = recover_lcg_params(states_after_flag)

    x9 = states_after_flag[0]

    x_vals = [x9]
    for _ in range(8):
        x_prev = backward_state(x_vals[0], a, c)
        x_vals.insert(0, x_prev)
    x1_to_x8 = x_vals[0:8]
    ks_flag = build_keystream_from_states(x1_to_x8)

    if len(ks_flag) != len(enc_flag):
        raise RuntimeError("Keystream length mismatch for flag")
    Cflag = xor_bytes(enc_flag, ks_flag)
    Cflag_int = bytes_to_long(Cflag)

    last_state = states_after_flag[-1]

    def predict_next_keystream(num_states: int) -> tuple[bytes, int]:
        nonlocal last_state
        seq = []
        for _ in range(num_states):
            nxt = forward_state(last_state, a, c)
            seq.append(nxt)
            last_state = nxt
        return build_keystream_from_states(seq), last_state

    known_m = b"A"

    ks_next, _ = predict_next_keystream(4)

    enc_modp_resp = get_enc_mod_p(io, known_m)
    if len(enc_modp_resp) != 32:
        raise RuntimeError("Unexpected mod-p ciphertext length; expected 32 bytes")

    C_modp_bytes = xor_bytes(enc_modp_resp, ks_next)
    C_modp_int = bytes_to_long(C_modp_bytes)

    m_int = bytes_to_long(known_m)
    e = 65537

    r = (pow(m_int, e, n) - C_modp_int) % n
    g = math.gcd(n, r)
    if g in (1, n):
        for trial in [b"B", b"C", b"D", b"E", b"F"]:
            ks_trial, _ = predict_next_keystream(4)
            enc_trial = get_enc_mod_p(io, trial)
            C_trial = bytes_to_long(xor_bytes(enc_trial, ks_trial))
            r = (pow(bytes_to_long(trial), e, n) - C_trial) % n
            g = math.gcd(n, r)
            if g not in (1, n):
                break
        if g in (1, n):
            raise RuntimeError(
                "Failed to factor n; try re-running for a different instance"
            )

    p = g
    q = n // p

    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    m_flag_int = pow(Cflag_int, d, n)
    k_flag = (n.bit_length() + 7) // 8
    m_flag = long_to_bytes(m_flag_int, k_flag).lstrip(b"\x00")

    print(m_flag.decode(errors="ignore"))


def main():
    parser = argparse.ArgumentParser(description="Solver for PwnSec CTF - crypto/opera")
    parser.add_argument("--host", help="remote host")
    parser.add_argument("--port", type=int, help="remote port")
    parser.add_argument(
        "--local", action="store_true", help="run local chall.py in this folder"
    )
    parser.add_argument(
        "--python", default=sys.executable, help="python interpreter for local run"
    )
    parser.add_argument(
        "--ssl",
        action="store_true",
        help="use TLS (useful if the service on 443 expects TLS)",
    )
    args = parser.parse_args()

    if args.local:
        argv = [args.python, "chall.py"]
        if HAVE_PWN:
            tube = process(argv)
            io = PwntoolsIO(tube)
        else:
            io = SubprocessIO(argv)
        try:
            solve(io)
        finally:
            if HAVE_PWN:
                try:
                    tube.close()
                except Exception:
                    pass
    elif args.host and args.port:
        if not HAVE_PWN:
            print(
                "pwntools is required for remote mode. Install with: pip install pwntools",
                file=sys.stderr,
            )
            sys.exit(2)
        try:
            tube = remote(
                args.host,
                args.port,
                ssl=args.ssl,
                sni=(args.host if args.ssl else None),
            )
        except TypeError:
            if args.ssl:
                print(
                    "Your pwntools version may not support ssl=. Try: pip install --upgrade pwntools",
                    file=sys.stderr,
                )
                sys.exit(2)
            tube = remote(args.host, args.port)
        io = PwntoolsIO(tube)
        solve(io)
    else:
        print("Specify --local or --host/--port", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
