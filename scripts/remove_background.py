#!/usr/bin/env python3
"""
Meow Ping RTS - Background Removal Script
Removes backgrounds from concept art for sprite processing.

Usage:
    python remove_background.py <input_image> [output_image]
    python remove_background.py --batch <input_folder> <output_folder>

Requirements:
    pip install rembg pillow

Note: First run will download the U2Net model (~170MB)
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    missing = []
    try:
        from PIL import Image
    except ImportError:
        missing.append("pillow")

    try:
        from rembg import remove
    except ImportError:
        missing.append("rembg")

    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    return True

def remove_background_single(input_path: str, output_path: str = None) -> str:
    """
    Remove background from a single image.

    Args:
        input_path: Path to input image
        output_path: Path for output (optional, defaults to _nobg suffix)

    Returns:
        Path to output image
    """
    from PIL import Image
    from rembg import remove

    input_path = Path(input_path)

    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_nobg.png"
    else:
        output_path = Path(output_path)

    print(f"Processing: {input_path.name}")

    # Load image
    with Image.open(input_path) as img:
        # Convert to RGBA if needed
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Remove background
        output = remove(img)

        # Save as PNG (preserves transparency)
        output.save(output_path, 'PNG')

    print(f"Saved: {output_path}")
    return str(output_path)

def remove_background_batch(input_folder: str, output_folder: str) -> list:
    """
    Remove backgrounds from all images in a folder.

    Args:
        input_folder: Path to folder with input images
        output_folder: Path for output images

    Returns:
        List of output paths
    """
    from PIL import Image
    from rembg import remove

    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    # Supported image formats
    extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}

    images = [f for f in input_folder.iterdir()
              if f.suffix.lower() in extensions]

    if not images:
        print(f"No images found in {input_folder}")
        return []

    print(f"Found {len(images)} images to process")
    outputs = []

    for i, img_path in enumerate(images, 1):
        print(f"[{i}/{len(images)}] Processing: {img_path.name}")

        output_path = output_folder / f"{img_path.stem}_nobg.png"

        try:
            with Image.open(img_path) as img:
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                output = remove(img)
                output.save(output_path, 'PNG')

            outputs.append(str(output_path))
            print(f"    Saved: {output_path.name}")
        except Exception as e:
            print(f"    Error: {e}")

    print(f"\nCompleted: {len(outputs)}/{len(images)} images processed")
    return outputs

def main():
    if not check_dependencies():
        sys.exit(1)

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    if sys.argv[1] == '--batch':
        if len(sys.argv) < 4:
            print("Usage: python remove_background.py --batch <input_folder> <output_folder>")
            sys.exit(1)
        remove_background_batch(sys.argv[2], sys.argv[3])
    else:
        input_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        remove_background_single(input_path, output_path)

if __name__ == '__main__':
    main()
