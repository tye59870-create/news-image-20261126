#!/usr/bin/env python3
"""Entry for make.fun bounty news-image-20261126.

Writes the front-page image for Thursday 26 November 2026 to
/output/entry.png. The image ships in the repository as base64 text
(entry.png.b64) so the tree stays plain text; this program only decodes
it, checks the PNG header, and writes the bytes out. Standard library
only, no network, no randomness: every run writes identical bytes.

Usage: python3 main.py [--out PATH]   (default: /output/entry.png)
"""
import argparse
import base64
import hashlib
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLED = HERE / "entry.png.b64"
DEFAULT_OUT = Path("/output/entry.png")

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
EXPECTED_SIZE = (1024, 1024)
MAX_BYTES = 1024 * 1024


def read_bundled(path):
    """Return the raw PNG bytes stored as base64 in path."""
    text = path.read_text(encoding="utf-8").strip()
    return base64.b64decode(text, validate=True)


def png_dimensions(data):
    """Read (width, height) out of a PNG's IHDR chunk, without Pillow."""
    if len(data) < 33 or data[:8] != PNG_MAGIC:
        raise ValueError("not a PNG file")
    chunk_len, chunk_type = struct.unpack(">I4s", data[8:16])
    if chunk_type != b"IHDR" or chunk_len != 13:
        raise ValueError("PNG has no IHDR chunk first")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def check_image(data):
    """Refuse anything that is not our 1024x1024 PNG under 1 MiB."""
    if len(data) > MAX_BYTES:
        raise ValueError(f"image is {len(data)} bytes, over the 1 MiB cap")
    size = png_dimensions(data)
    if size != EXPECTED_SIZE:
        raise ValueError(f"image is {size[0]}x{size[1]}, expected 1024x1024")
    return size


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Write the bundled front-page PNG to disk.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help="where to write entry.png (default: %(default)s)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    data = read_bundled(BUNDLED)
    size = check_image(data)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    digest = hashlib.sha256(args.out.read_bytes()).hexdigest()
    print(f"wrote {args.out} ({size[0]}x{size[1]}, {len(data)} bytes, "
          f"sha256={digest})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
