"""
Sprite Sheet Assembler with Faction Color Variant Support
Combines 8-direction sprites into organized sprite sheets with faction recoloring

Usage:
    python assemble_spritesheet.py --input sprites/cat/ --output sheets/cat_sheet.png
    python assemble_spritesheet.py --input sprites/cat/ --output sheets/ --factions red,blue,green

Layouts:
    4x2: 4 columns, 2 rows (N,NE,E,SE / S,SW,W,NW)
    8x1: 8 columns, 1 row (N,NE,E,SE,S,SW,W,NW)
    2x4: 2 columns, 4 rows (vertical layout)

Author: VULCAN (Elite Art Team - VFX Artist)
Project: Ziggie AI Game Dev System / MeowPing RTS
"""

import argparse
import colorsys
import math
from pathlib import Path
from typing import List, Tuple, Dict, Optional

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow is required for sprite sheet creation")
    print("Install with: pip install Pillow")
    exit(1)


# Standard 8 directions in clockwise order
DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

# Faction color HSV hue shifts (0-1 range)
FACTION_COLORS = {
    "neutral": 0.0,     # No shift (original colors)
    "red": 0.0,         # Red faction (base hue)
    "blue": 0.55,       # Blue faction (~200 degrees)
    "green": 0.33,      # Green faction (~120 degrees)
    "gold": 0.12,       # Gold/Yellow faction (~45 degrees)
    "purple": 0.75,     # Purple faction (~270 degrees)
    "cyan": 0.50,       # Cyan faction (~180 degrees)
    "orange": 0.08,     # Orange faction (~30 degrees)
}

# Layout presets
LAYOUTS = {
    "4x2": (4, 2),      # Standard RTS layout
    "8x1": (8, 1),      # Horizontal strip
    "2x4": (2, 4),      # Vertical layout
    "1x8": (1, 8),      # Vertical strip
}


def shift_hue(r: int, g: int, b: int, hue_shift: float) -> Tuple[int, int, int]:
    """
    Shift the hue of an RGB color while preserving saturation and value

    Args:
        r, g, b: RGB values (0-255)
        hue_shift: Hue shift amount (0-1 range, wraps around)

    Returns:
        Tuple of shifted RGB values (0-255)
    """
    # Convert to HSV
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

    # Apply hue shift (wrap around 0-1)
    new_h = (h + hue_shift) % 1.0

    # Convert back to RGB
    new_r, new_g, new_b = colorsys.hsv_to_rgb(new_h, s, v)

    return (int(new_r * 255), int(new_g * 255), int(new_b * 255))


def apply_faction_color(image: Image.Image, faction: str) -> Image.Image:
    """
    Apply faction color variant to an image using HSV hue shift

    Args:
        image: PIL Image (RGBA)
        faction: Faction name from FACTION_COLORS

    Returns:
        Recolored image
    """
    if faction not in FACTION_COLORS:
        print(f"  WARNING: Unknown faction '{faction}', using neutral")
        return image

    hue_shift = FACTION_COLORS[faction]

    if hue_shift == 0.0:
        return image  # No shift needed

    # Convert to RGBA if needed
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Create a copy to modify
    result = image.copy()
    pixels = result.load()

    width, height = result.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]

            # Skip fully transparent pixels
            if a == 0:
                continue

            # Skip grayscale pixels (preserve metals, shadows)
            if r == g == b:
                continue

            # Apply hue shift
            new_r, new_g, new_b = shift_hue(r, g, b, hue_shift)
            pixels[x, y] = (new_r, new_g, new_b, a)

    return result


def find_direction_sprites(input_dir: Path, model_name: Optional[str] = None) -> Dict[str, Path]:
    """
    Find sprite files for each direction

    Args:
        input_dir: Directory containing sprite files
        model_name: Optional model name prefix to filter

    Returns:
        Dictionary mapping direction names to file paths
    """
    direction_files = {}

    for direction in DIRECTIONS:
        # Try various naming patterns
        patterns = [
            f"*_{direction}.png",           # cat_N.png
            f"*_{direction.lower()}.png",   # cat_n.png
            f"{direction}.png",             # N.png
            f"{direction.lower()}.png",     # n.png
        ]

        if model_name:
            patterns = [
                f"{model_name}_{direction}.png",
                f"{model_name}_{direction.lower()}.png",
            ] + patterns

        for pattern in patterns:
            matches = list(input_dir.glob(pattern))
            if matches:
                direction_files[direction] = matches[0]
                break

    return direction_files


def create_sprite_sheet(
    direction_files: Dict[str, Path],
    output_path: Path,
    layout: Tuple[int, int] = (4, 2),
    padding: int = 0,
    faction: Optional[str] = None
) -> bool:
    """
    Create a sprite sheet from direction sprites

    Args:
        direction_files: Dictionary mapping directions to file paths
        output_path: Output file path
        layout: (columns, rows) tuple
        padding: Pixels between sprites
        faction: Optional faction for color variant

    Returns:
        True if successful
    """
    columns, rows = layout

    # Check we have all 8 directions
    missing = [d for d in DIRECTIONS if d not in direction_files]
    if missing:
        print(f"  WARNING: Missing directions: {', '.join(missing)}")

    # Load first sprite to get dimensions
    first_direction = next(iter(direction_files.values()))
    first_sprite = Image.open(first_direction)
    sprite_width, sprite_height = first_sprite.size

    print(f"  Sprite dimensions: {sprite_width}x{sprite_height}")
    print(f"  Layout: {columns}x{rows} = {columns * rows} cells")

    # Calculate sheet dimensions
    sheet_width = (sprite_width + padding) * columns - padding
    sheet_height = (sprite_height + padding) * rows - padding

    # Create sprite sheet with transparent background
    sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))

    # Paste sprites in order
    for idx, direction in enumerate(DIRECTIONS):
        if direction not in direction_files:
            print(f"    SKIP: {direction} (not found)")
            continue

        # Load sprite
        sprite = Image.open(direction_files[direction])
        if sprite.mode != 'RGBA':
            sprite = sprite.convert('RGBA')

        # Apply faction color if specified
        if faction and faction != "neutral":
            sprite = apply_faction_color(sprite, faction)

        # Calculate position
        col = idx % columns
        row = idx // columns

        if row >= rows:
            print(f"    WARNING: {direction} exceeds layout capacity")
            continue

        x = col * (sprite_width + padding)
        y = row * (sprite_height + padding)

        # Paste with transparency
        sprite_sheet.paste(sprite, (x, y), sprite)
        print(f"    [{direction:2s}] -> ({col}, {row})")

    # Save sprite sheet
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sprite_sheet.save(output_path, 'PNG')

    print(f"  Output: {output_path} ({sheet_width}x{sheet_height})")
    return True


def create_faction_variants(
    direction_files: Dict[str, Path],
    output_dir: Path,
    model_name: str,
    factions: List[str],
    layout: Tuple[int, int] = (4, 2),
    padding: int = 0
) -> List[Path]:
    """
    Create sprite sheets for multiple faction color variants

    Args:
        direction_files: Dictionary mapping directions to file paths
        output_dir: Output directory
        model_name: Base name for output files
        factions: List of faction names
        layout: (columns, rows) tuple
        padding: Pixels between sprites

    Returns:
        List of created file paths
    """
    created_files = []

    for faction in factions:
        faction_lower = faction.lower()
        output_path = output_dir / f"{model_name}_{faction_lower}_sheet.png"

        print(f"\nCreating {faction} variant...")
        if create_sprite_sheet(direction_files, output_path, layout, padding, faction_lower):
            created_files.append(output_path)

    return created_files


def parse_layout(layout_str: str) -> Tuple[int, int]:
    """Parse layout string (e.g., '4x2') into tuple"""
    if layout_str in LAYOUTS:
        return LAYOUTS[layout_str]

    try:
        cols, rows = layout_str.lower().split('x')
        return (int(cols), int(rows))
    except ValueError:
        print(f"WARNING: Invalid layout '{layout_str}', using 4x2")
        return (4, 2)


def main():
    parser = argparse.ArgumentParser(
        description='Assemble 8-direction sprites into sprite sheets with faction color variants',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic sprite sheet (4x2 layout)
    python assemble_spritesheet.py --input sprites/cat/ --output sheets/cat_sheet.png

    # All faction variants
    python assemble_spritesheet.py --input sprites/cat/ --output sheets/ --factions all

    # Specific factions with 8x1 layout
    python assemble_spritesheet.py --input sprites/cat/ --output sheets/ --factions red,blue,green --layout 8x1

Available factions: neutral, red, blue, green, gold, purple, cyan, orange
Available layouts: 4x2, 8x1, 2x4, 1x8 (or custom like 3x3)
        """
    )

    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Input directory containing 8-direction sprite files'
    )

    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output file path (PNG) or directory for faction variants'
    )

    parser.add_argument(
        '--model',
        type=str,
        help='Model name prefix (auto-detected if not specified)'
    )

    parser.add_argument(
        '--layout',
        type=str,
        default='4x2',
        help='Sprite sheet layout (default: 4x2). Options: 4x2, 8x1, 2x4, 1x8, or custom NxM'
    )

    parser.add_argument(
        '--padding',
        type=int,
        default=0,
        help='Pixels between sprites (default: 0)'
    )

    parser.add_argument(
        '--factions',
        type=str,
        help='Faction color variants to generate (comma-separated or "all")'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("VULCAN - Sprite Sheet Assembler")
    print("Elite Art Team - Ziggie AI Game Dev System")
    print("=" * 60)
    print()

    input_dir = Path(args.input)
    output_path = Path(args.output)
    layout = parse_layout(args.layout)

    if not input_dir.exists():
        print(f"ERROR: Input directory not found: {input_dir}")
        return

    # Find direction sprites
    direction_files = find_direction_sprites(input_dir, args.model)

    if not direction_files:
        print(f"ERROR: No direction sprites found in {input_dir}")
        print("Expected files like: cat_N.png, cat_NE.png, cat_E.png, etc.")
        return

    print(f"Found {len(direction_files)} direction sprites:")
    for direction, path in direction_files.items():
        print(f"  {direction}: {path.name}")
    print()

    # Determine model name
    model_name = args.model
    if not model_name:
        # Extract from first file name
        first_file = next(iter(direction_files.values()))
        name_parts = first_file.stem.rsplit('_', 1)
        model_name = name_parts[0] if len(name_parts) > 1 else first_file.stem

    print(f"Model name: {model_name}")
    print(f"Layout: {layout[0]}x{layout[1]}")
    print()

    # Generate faction variants or single sheet
    if args.factions:
        if args.factions.lower() == 'all':
            factions = list(FACTION_COLORS.keys())
        else:
            factions = [f.strip() for f in args.factions.split(',')]

        # Ensure output is a directory
        output_dir = output_path if output_path.is_dir() or not output_path.suffix else output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        created = create_faction_variants(
            direction_files,
            output_dir,
            model_name,
            factions,
            layout,
            args.padding
        )

        print()
        print("=" * 60)
        print(f"Created {len(created)} faction variant sheets:")
        for path in created:
            print(f"  - {path}")

    else:
        # Single sheet
        if output_path.is_dir():
            output_file = output_path / f"{model_name}_sheet.png"
        else:
            output_file = output_path

        print("Creating sprite sheet...")
        create_sprite_sheet(direction_files, output_file, layout, args.padding)

    print("=" * 60)
    print("Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
