import socket
import ssl
import sys
from typing import Tuple, Optional


HOST = "dc9f277b4d0aea88.syndroem.zone.re"
PORT = 443


def build_error_vector(n: int = 3488, weight: int = 4) -> str:
    """
    Build a binary string of length n with exactly `weight` ones.
    We'll just set the first `weight` bits to 1 and the rest to 0.
    """
    if weight > n:
        raise ValueError("weight cannot exceed length")
    return ("1" * weight) + ("0" * (n - weight))


def recv_until(sock: ssl.SSLSocket, marker: bytes, timeout: float = 10.0) -> bytes:
    sock.settimeout(timeout)
    buf = bytearray()
    while marker not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf.extend(chunk)
    return bytes(buf)


def _connect_tls_with_fallback(host: str, port: int, ctx: ssl.SSLContext, per_try_timeout: float = 7.0, connect_ip: Optional[str] = None) -> ssl.SSLSocket:
    """
    Resolve DNS and try all results, preferring IPv4 first, then IPv6.
    """
    if connect_ip:
        # If an explicit IP is provided, build a single addrinfo entry, prefer IPv4 parse
        try:
            sockaddr = (connect_ip, port)
            infos = [(socket.AF_INET, socket.SOCK_STREAM, 0, '', sockaddr)]
        except Exception:
            infos = socket.getaddrinfo(connect_ip, port, 0, socket.SOCK_STREAM)
    else:
        infos = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)
    # Prefer IPv4
    infos = sorted(infos, key=lambda x: 0 if x[0] == socket.AF_INET else 1)
    last_exc = None
    for family, socktype, proto, _canonname, sockaddr in infos:
        raw = None
        try:
            raw = socket.socket(family, socktype, proto)
            raw.settimeout(per_try_timeout)
            raw.connect(sockaddr)
            s = ctx.wrap_socket(raw, server_hostname=host)
            return s
        except Exception as e:
            last_exc = e
            try:
                if raw is not None:
                    raw.close()
            except Exception:
                pass
            continue
    if last_exc:
        raise last_exc
    raise OSError("No usable addresses resolved for host")


def connect_and_solve(host: str = HOST, port: int = PORT, n: int = 3488, weight: int = 4, insecure_tls: bool = False, per_try_timeout: float = 7.0, retries: int = 3, backoff: float = 0.5, connect_ip: Optional[str] = None) -> Tuple[bytes, bytes]:
    """
    Connects via TLS, reads until the input prompt, sends a valid error vector,
    then returns (banner_bytes, response_bytes).
    """
    ctx = ssl.create_default_context()
    # For CTF-y endpoints that may not have a public CA cert, you can loosen verification.
    if insecure_tls:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    last_exc = None
    import time
    for attempt in range(1, max(1, retries) + 1):
        try:
            with _connect_tls_with_fallback(host, port, ctx, per_try_timeout=per_try_timeout, connect_ip=connect_ip) as s:
                banner = recv_until(s, b"Enter the error:")
                payload = build_error_vector(n, weight).encode() + b"\n"
                s.sendall(payload)
                s.settimeout(5.0)
                try:
                    resp_parts = []
                    while True:
                        chunk = s.recv(4096)
                        if not chunk:
                            break
                        resp_parts.append(chunk)
                except (socket.timeout, ssl.SSLWantReadError):
                    pass
                response = b"".join(resp_parts)
                return banner, response
        except Exception as e:
            last_exc = e
            if attempt < retries:
                time.sleep(backoff * attempt)
            continue
    assert last_exc is not None
    raise last_exc


def main():
    host = HOST
    port = PORT
    n = 3488
    weight = 4
    insecure = False
    per_try_timeout = 7.0
    retries = 3
    backoff = 0.5
    connect_ip = None

    args = sys.argv[1:]
    # Simple positional/flag parsing: host port [n] [weight] [--insecure]
    if len(args) >= 1 and not args[0].startswith("-"):
        host = args[0]
    if len(args) >= 2 and not args[1].startswith("-"):
        port = int(args[1])
    if len(args) >= 3 and not args[2].startswith("-"):
        n = int(args[2])
    if len(args) >= 4 and not args[3].startswith("-"):
        weight = int(args[3])
    if any(a == "--insecure" for a in args):
        insecure = True
    for i, a in enumerate(args):
        if a == "--try-timeout" and i + 1 < len(args):
            try:
                per_try_timeout = float(args[i + 1])
            except ValueError:
                pass
        if a == "--retries" and i + 1 < len(args):
            try:
                retries = int(args[i + 1])
            except ValueError:
                pass
        if a == "--backoff" and i + 1 < len(args):
            try:
                backoff = float(args[i + 1])
            except ValueError:
                pass
        if a == "--connect-ip" and i + 1 < len(args):
            connect_ip = args[i + 1]

    banner, response = connect_and_solve(
        host,
        port,
        n=n,
        weight=weight,
        insecure_tls=insecure,
        per_try_timeout=per_try_timeout,
        retries=retries,
        backoff=backoff,
        connect_ip=connect_ip,
    )
    try:
        print(banner.decode(errors="ignore"))
    except Exception:
        print(repr(banner))
    print("----- server response -----")
    try:
        print(response.decode(errors="ignore"))
    except Exception:
        print(repr(response))


if __name__ == "__main__":
    main()
