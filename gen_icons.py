#!/usr/bin/env python3
import sys
import os
from pathlib import Path
from PIL import Image

# name -> (width, height)
PNG_TARGETS = {
    "32x32.png": (32, 32),
    "128x128.png": (128, 128),
    "128x128@2x.png": (256, 256),  # 2x of 128
}

def make_square_icon(src: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Return an RGBA image of `size` with `src` fitted (contain) and centered on transparent bg."""
    w, h = size
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    # Ensure we work with RGBA
    img = src.convert("RGBA")

    # Scale to fit within box while preserving aspect ratio (contain)
    img_w, img_h = img.size
    if img_w == 0 or img_h == 0:
        return canvas

    scale = min(w / img_w, h / img_h)
    new_w = max(1, int(round(img_w * scale)))
    new_h = max(1, int(round(img_h * scale)))
    img_resized = img.resize((new_w, new_h), Image.LANCZOS)

    # Center on canvas
    offset = ((w - new_w) // 2, (h - new_h) // 2)
    canvas.paste(img_resized, offset, mask=img_resized)
    return canvas

def main():
    if len(sys.argv) != 3:
        print("Usage: python gen_icons.py <source_image> <output_folder>")
        print("Example: python gen_icons.py branding/app-icon.png src-tauri/icons")
        sys.exit(1)

    src_path = Path(sys.argv[1]).expanduser()
    out_dir = Path(sys.argv[2]).expanduser()

    if not src_path.exists():
        print(f"Error: source image not found: {src_path}")
        sys.exit(2)

    out_dir.mkdir(parents=True, exist_ok=True)

    # Load once
    try:
        src_img = Image.open(src_path)
    except Exception as e:
        print(f"Error: failed to open source image: {e}")
        sys.exit(3)

    for filename, size in PNG_TARGETS.items():
        try:
            icon = make_square_icon(src_img, size)
            out_path = out_dir / filename
            # Overwrite unconditionally
            icon.save(out_path, format="PNG", optimize=True)
            print(f"Wrote {out_path} ({size[0]}x{size[1]})")
        except Exception as e:
            print(f"Failed to write {filename}: {e}")
            sys.exit(4)

    print("Done.")

if __name__ == "__main__":
    main()
