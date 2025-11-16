#!/usr/bin/env python3
import os
import sys
import random
import shutil
from pathlib import Path

def parse_bool(value: str) -> bool:
    """Parse a string into a boolean."""
    v = value.strip().lower()
    return v in ("1", "true", "t", "yes", "y")

def main():
    if len(sys.argv) < 6:
        print("Usage: python3 copy_random_files.py <src_dir> <dst_dir> <count> <search_string> <random_true_false>")
        sys.exit(1)

    src_dir = Path(sys.argv[1])
    dst_dir = Path(sys.argv[2])

    try:
        count = int(sys.argv[3])
    except ValueError:
        print(f"Error: count must be an integer, got '{sys.argv[3]}'.")
        sys.exit(1)

    search_string = sys.argv[4]
    random_flag = parse_bool(sys.argv[5])

    if count <= 0:
        print("Error: count must be a positive integer.")
        sys.exit(1)

    if not src_dir.is_dir():
        print(f"Error: {src_dir} is not a directory.")
        sys.exit(1)

    dst_dir.mkdir(parents=True, exist_ok=True)

    # Collect files matching search_string (case-insensitive)
    search_lower = search_string.lower()
    files = [
        f for f in src_dir.iterdir()
        if f.is_file() and search_lower in f.name.lower()
    ]

    if not files:
        print(f"No files found in source directory matching '{search_string}'.")
        sys.exit(0)

    # Choose files either randomly or deterministically
    if random_flag:
        sample = random.sample(files, min(count, len(files)))
    else:
        # deterministic: sort by name and take first N
        files_sorted = sorted(files, key=lambda p: p.name.lower())
        sample = files_sorted[:count]

    copied_count = 0
    for f in sample:
        dest_file = dst_dir / f.name
        shutil.copy2(f, dest_file)
        copied_count += 1
        print(f"Copied: {f} -> {dest_file}")

    print(f"\n✅ Copied {copied_count} file(s) to {dst_dir}")

if __name__ == "__main__":
    main()
