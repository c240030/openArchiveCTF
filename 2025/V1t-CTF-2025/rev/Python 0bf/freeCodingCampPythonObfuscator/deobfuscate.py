"""
Deobfuscate FreeCodingTools/FreeCodingCamp Python obfuscator output.

It reverses the steps used by the obfuscator:
  1) Reverse the bytes literal (__[::-1])
  2) Base64 decode
  3) zlib decompress

Usage (Windows PowerShell):
    python .\\deobfuscate.py .\\output.txt -o recovered.py

If no input file is provided, it defaults to 'output.txt' in the current directory.
"""

from __future__ import annotations

import argparse
import base64
import re
import sys
import zlib
from pathlib import Path


def extract_payload(src: str) -> str:
    """Extract the bytes literal payload from the obfuscated Python source.

    Looks for the longest occurrence of b'...base64...' or b"...base64...".
    Returns the raw inner string (without the b'' quotes).
    Raises ValueError if nothing plausible is found.
    """

    # Accept only base64-ish characters. The payload is reversed, but charset stays the same.
    pat_single = re.compile(r"b'([A-Za-z0-9+/=]+)'", re.DOTALL)
    pat_double = re.compile(r"b\"([A-Za-z0-9+/=]+)\"", re.DOTALL)

    candidates = [m.group(1) for m in pat_single.finditer(src)] + [
        m.group(1) for m in pat_double.finditer(src)
    ]

    if not candidates:
        raise ValueError(
            "Could not find a bytes literal payload. Make sure the input is the obfuscated file."
        )

    # Choose the longest match to be robust if there are accidental smaller matches.
    payload = max(candidates, key=len)
    # Basic sanity check: base64 length should be a multiple of 4 after reversing; we can't know yet,
    # but lengths are typically large. We'll proceed and let decoding validate.
    return payload


def deobfuscate_one(src: str) -> bytes:
    """Perform a single decode round on the given obfuscated source text."""
    payload = extract_payload(src)
    try:
        reversed_payload = payload[::-1]
        decoded = base64.b64decode(reversed_payload, validate=True)
        plain = zlib.decompress(decoded)
        return plain
    except Exception as e:
        # Try a couple of fallbacks that sometimes differ across obfuscators
        # 1) Some variants may store raw DEFLATE (no zlib header); try that
        try:
            import zlib as _z

            # -15 window bits = raw DEFLATE
            plain = _z.decompress(decoded, -15)  # type: ignore[name-defined]
            return plain
        except Exception:
            pass
        raise RuntimeError(
            "Failed to decode payload. The file may not be from this obfuscator or is corrupted."
        ) from e


def deobfuscate_all(src: str, max_rounds: int = 100) -> bytes:
    """Iteratively peel all obfuscation layers until plain source is reached.

    Stops when a round fails to find a payload (ValueError) or max_rounds is reached.
    """
    current_text = src
    last_bytes: bytes | None = None
    for _ in range(max_rounds):
        try:
            last_bytes = deobfuscate_one(current_text)
        except ValueError:
            # No more layers detected
            break
        # Prepare for next round
        try:
            current_text = last_bytes.decode("utf-8", errors="replace")
        except Exception:
            # If the result isn't text, return the raw bytes
            return last_bytes
    if last_bytes is None:
        raise RuntimeError("No obfuscation payloads found in the input file.")
    return last_bytes


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", nargs="?", default="output.txt", help="Path to obfuscated Python file")
    p.add_argument("-o", "--out", default="recovered.py", help="Path to write recovered source")
    p.add_argument("--stdout", action="store_true", help="Also print recovered code to STDOUT")
    args = p.parse_args(argv)

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"Input file not found: {in_path}", file=sys.stderr)
        return 2

    try:
        text = in_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"Failed to read input: {e}", file=sys.stderr)
        return 2

    try:
        recovered = deobfuscate_all(text)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 1

    out_path = Path(args.out)
    try:
        out_path.write_bytes(recovered)
    except Exception as e:
        print(f"Failed to write output: {e}", file=sys.stderr)
        return 2

    try:
        preview = recovered.decode("utf-8", errors="replace")
    except Exception:
        preview = "<binary output>"

    print(f"Recovered source written to: {out_path}")
    # Show a short preview to confirm success
    lines = preview.splitlines()
    head = "\n".join(lines[:10])
    print("\nPreview (first 10 lines):\n" + head)

    if args.stdout:
        print("\nFull recovered source:\n")
        try:
            # Ensure we don't double-print binary gibberish
            sys.stdout.write(preview)
            if not preview.endswith("\n"):
                print()
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
