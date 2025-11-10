#!/usr/bin/env python3
import os
import sys
import random
import shutil
from pathlib import Path

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 copy_random_files.py <src_dir> <dst_dir> [count=100]")
        sys.exit(1)

    src_dir = Path(sys.argv[1])
    dst_dir = Path(sys.argv[2])
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 100

    if not src_dir.is_dir():
        print(f"Error: {src_dir} is not a directory.")
        sys.exit(1)

    dst_dir.mkdir(parents=True, exist_ok=True)

    files = [f for f in src_dir.iterdir() if f.is_file()]
    if not files:
        print("No files found in source directory.")
        sys.exit(0)

    sample = random.sample(files, min(count, len(files)))

    for f in sample:
        dest_file = dst_dir / f.name
        shutil.copy2(f, dest_file)
        print(f"Copied: {f.name}")

    print(f"\n✅ Copied {len(sample)} files to {dst_dir}")

if __name__ == "__main__":
    main()
