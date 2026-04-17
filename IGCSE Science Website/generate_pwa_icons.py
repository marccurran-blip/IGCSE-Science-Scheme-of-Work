#!/usr/bin/env python3
"""
Generate PWA icons from SVG files.

This script reads SVG icon files and generates PNG versions at multiple sizes
suitable for Progressive Web App manifest files.

Supported sizes: 72, 96, 128, 144, 152, 192, 384, 512 pixels

Dependencies:
- cairosvg (preferred for SVG rendering)
- Pillow (fallback for PNG generation)
"""

import os
import sys
from pathlib import Path

# Icon sizes to generate
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# Icons to generate: (name, svg_file)
ICONS = [
    ("student", "icon_student.svg"),
    ("teacher", "icon_teacher.svg"),
]


def create_icons_directory(base_dir):
    """Create the icons subdirectory if it doesn't exist."""
    icons_dir = os.path.join(base_dir, "icons")
    os.makedirs(icons_dir, exist_ok=True)
    return icons_dir


def generate_with_cairosvg(svg_path, output_path, size):
    """Generate PNG from SVG using cairosvg."""
    try:
        import cairosvg
        cairosvg.svg2png(
            url=svg_path,
            write_to=output_path,
            output_width=size,
            output_height=size,
        )
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"  Error with cairosvg: {e}")
        return False


def generate_with_pillow(svg_path, output_path, size):
    """Generate PNG from SVG using Pillow (simplified rasterization)."""
    try:
        from PIL import Image
        import io

        # Try to use cairosvg to render SVG to PNG bytes first
        try:
            import cairosvg
            png_bytes = io.BytesIO()
            cairosvg.svg2png(url=svg_path, write_to=png_bytes, output_width=size, output_height=size)
            png_bytes.seek(0)
            img = Image.open(png_bytes)
            img = img.convert("RGBA")
            img.save(output_path, "PNG")
            return True
        except ImportError:
            # Fallback: render at 512px and resize
            print(f"    Note: cairosvg not available, using Pillow resize method")
            # Use a simple approach: render large and resize
            import subprocess
            try:
                # Try using ImageMagick or another tool if available
                subprocess.run(
                    ["convert", svg_path, "-resize", f"{size}x{size}", "-background", "none", output_path],
                    check=True,
                    capture_output=True,
                )
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Last resort: create a placeholder
                print(f"    Warning: Could not render SVG. Creating placeholder image.")
                placeholder = Image.new("RGBA", (size, size), (200, 100, 150, 255))
                placeholder.save(output_path, "PNG")
                return True

    except ImportError:
        return False
    except Exception as e:
        print(f"  Error with Pillow: {e}")
        return False


def generate_icons(base_dir):
    """Generate all icon variants from SVG sources."""
    icons_dir = create_icons_directory(base_dir)

    print(f"Generating PWA icons in: {icons_dir}\n")

    for icon_name, svg_filename in ICONS:
        svg_path = os.path.join(base_dir, svg_filename)

        if not os.path.exists(svg_path):
            print(f"Error: {svg_filename} not found at {svg_path}")
            continue

        print(f"Processing {icon_name} icon from {svg_filename}:")

        for size in ICON_SIZES:
            output_filename = f"{icon_name}-{size}x{size}.png"
            output_path = os.path.join(icons_dir, output_filename)

            # Try cairosvg first (best quality)
            if generate_with_cairosvg(svg_path, output_path, size):
                print(f"  {size}x{size}px: ✓ (cairosvg)")
            # Fall back to Pillow
            elif generate_with_pillow(svg_path, output_path, size):
                print(f"  {size}x{size}px: ✓ (Pillow)")
            else:
                print(f"  {size}x{size}px: ✗ (Failed)")

        print()

    print(f"Icon generation complete!")
    print(f"Icons saved to: {icons_dir}")
    print(f"\nExample manifest entry:")
    print("""  "icons": [
    {
      "src": "icons/student-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "icons/student-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]""")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    if not os.path.isdir(base_dir):
        print(f"Error: Directory {base_dir} does not exist")
        sys.exit(1)

    try:
        generate_icons(base_dir)
    except KeyboardInterrupt:
        print("\nIcon generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
