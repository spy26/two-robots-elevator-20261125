#!/usr/bin/env python3
"""Two Robots in an Elevator — make.fun program/v1 entry.

Deterministic, no dependencies, no network, no model calls.
Writes the one-line entry to /output/entry.txt (the gate reads it) and
mirrors it to $MAKEFUN_OUTPUT_DIR/entry.txt when that is set and different.
Both files are verified byte-for-byte against the entry after writing.
"""

import hashlib
import os
import sys
from pathlib import Path

ENTRY = (
    "We are now 0.8 metres apart in this elevator, which my manual lists as "
    "'intimate' for two machines. I am recalculating my personal space as we speak."
)


def fail(message: str) -> "SystemExit":
    return SystemExit(f"error: {message}")


def validate_entry(text: str) -> None:
    if not 1 <= len(text) <= 200:
        raise fail(f"entry must be 1-200 characters, got {len(text)}")
    if not text.strip():
        raise fail("entry must not be only whitespace")
    if text != text.strip():
        raise fail("entry has leading or trailing whitespace")
    if "\n" in text or "\r" in text:
        raise fail("entry must be a single line")
    if "  " in text:
        raise fail("entry contains a double space")


def write_and_verify(file_path: Path, expected: bytes) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(expected)
    actual = file_path.read_bytes()
    if actual != expected:
        raise fail(f"verification failed: {file_path} differs from the expected entry bytes")
    # Second pass: validate the bytes actually on disk, not just the constant.
    on_disk = actual.decode("utf-8")
    if on_disk.endswith("\n"):
        raise fail(f"verification failed: {file_path} has a trailing newline")
    validate_entry(on_disk)


def try_mirror(file_path: Path, expected: bytes) -> None:
    try:
        write_and_verify(file_path, expected)
    except Exception as error:
        sys.stderr.write(f"warning: could not write {file_path}: {error}\n")


def main() -> None:
    validate_entry(ENTRY)
    data = ENTRY.encode("utf-8")

    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    primary = Path(output_dir) / "entry.txt" if output_dir else Path("/output/entry.txt")
    write_and_verify(primary, data)

    mirror = Path("/output/entry.txt")
    if mirror != primary:
        try_mirror(mirror, data)

    sys.stderr.write(f"sha256(entry.txt): {hashlib.sha256(data).hexdigest()}\n")
    sys.stdout.write(ENTRY + "\n")


main()
