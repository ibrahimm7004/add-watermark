"""Generate README demo images (before/after) using the watermarker CLI."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "examples"
BEFORE_PATH = EXAMPLES_DIR / "before.png"
AFTER_PATH = EXAMPLES_DIR / "after.png"


def create_before_image(path: Path) -> None:
    """Create a deterministic demo image for README screenshots."""
    width, height = 960, 540
    image = Image.new("RGB", (width, height), (28, 38, 56))
    draw = ImageDraw.Draw(image)

    # Draw a simple gradient-like backdrop with horizontal lines.
    for y in range(height):
        shade = int(48 + (y / height) * 120)
        draw.line([(0, y), (width, y)], fill=(shade // 2, shade, min(255, shade + 25)))

    draw.rectangle([(70, 90), (890, 450)], outline=(255, 255, 255), width=4)
    draw.ellipse([(740, 80), (900, 240)], fill=(255, 160, 60), outline=(255, 255, 255), width=3)
    draw.rectangle([(120, 140), (420, 410)], fill=(255, 255, 255), outline=(0, 0, 0), width=2)

    image.save(path, format="PNG", optimize=True)


def run_cli_watermark(before_path: Path, after_path: Path) -> None:
    """Generate after image by calling the CLI, not internals."""
    env = os.environ.copy()
    src_path = ROOT / "src"
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(src_path) if not existing else f"{src_path}{os.pathsep}{existing}"

    cmd = [
        sys.executable,
        "-m",
        "watermarker",
        "add",
        "--input",
        str(before_path),
        "--output",
        str(after_path),
        "--text",
        "(c) watermarker demo",
        "--pos",
        "br",
        "--opacity",
        "45",
        "--overwrite",
    ]

    subprocess.run(cmd, cwd=ROOT, env=env, check=True)


def main() -> None:
    EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    create_before_image(BEFORE_PATH)
    run_cli_watermark(BEFORE_PATH, AFTER_PATH)
    print(f"Generated: {BEFORE_PATH}")
    print(f"Generated: {AFTER_PATH}")


if __name__ == "__main__":
    main()
