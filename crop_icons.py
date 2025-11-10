#!/usr/bin/env python3
import sys
from pathlib import Path
from PIL import Image

CROP_PCT = 0.10  # 10% on each side

def crop_10_percent(img: Image.Image) -> Image.Image:
    w, h = img.size
    # pixels to remove from each edge
    dx = int(round(w * CROP_PCT))
    dy = int(round(h * CROP_PCT))
    # ensure at least 1px remains in each dimension
    left   = min(max(0, dx), w - 1)
    top    = min(max(0, dy), h - 1)
    right  = max(min(w - dx, w), left + 1)
    bottom = max(min(h - dy, h), top + 1)
    return img.crop((left, top, right, bottom))

def main():
    if len(sys.argv) != 3:
        print("Usage: python crop_icons_10pct.py <input_folder> <output_folder>")
        print("Example: python crop_icons_10pct.py src-tauri/icons cropped-icons")
        sys.exit(1)

    in_dir = Path(sys.argv[1]).expanduser()
    out_dir = Path(sys.argv[2]).expanduser()

    if not in_dir.is_dir():
        print(f"Error: input folder not found: {in_dir}")
        sys.exit(2)

    out_dir.mkdir(parents=True, exist_ok=True)

    png_paths = [p for p in in_dir.iterdir() if p.is_file() and p.suffix.lower() == ".png"]
    if not png_paths:
        print("No PNG files found in the input folder.")
        sys.exit(0)

    for p in png_paths:
        try:
            with Image.open(p) as im:
                im = im.convert("RGBA")  # preserve transparency
                cropped = crop_10_percent(im)
                out_path = out_dir / p.name
                cropped.save(out_path, format="PNG", optimize=True)
                print(f"Cropped: {p.name} -> {out_path}")
        except Exception as e:
            print(f"Failed: {p.name} ({e})")

    print("Done.")

if __name__ == "__main__":
    main()
