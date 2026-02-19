"""Core image processing engine for watermarker."""

from __future__ import annotations

from dataclasses import dataclass, field
from glob import glob, has_magic
from pathlib import Path
from typing import Literal

from PIL import Image, ImageDraw, ImageFont, ImageOps

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp", ".gif"}
DEFAULT_POSITION = "br"
DEFAULT_OPACITY = 35
DEFAULT_MARGIN = 24

Position = Literal["tl", "tr", "bl", "br", "c"]


class WatermarkerError(Exception):
    """Base exception for all watermarking errors."""


class ValidationError(WatermarkerError):
    """Raised when user input is invalid."""


class ProcessingError(WatermarkerError):
    """Raised when image processing fails."""


@dataclass
class BatchResult:
    """Processing summary for batch mode."""

    processed: int = 0
    skipped: int = 0
    failed: int = 0
    output_root: Path | None = None
    planned: list[tuple[Path, Path]] = field(default_factory=list)
    failures: list[tuple[Path, str]] = field(default_factory=list)


def clamp(value: int, minimum: int, maximum: int) -> int:
    """Clamp an integer into the inclusive range [minimum, maximum]."""
    return max(minimum, min(value, maximum))


def is_supported_image(path: Path) -> bool:
    """Return True if path extension is supported."""
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def normalize_orientation(image: Image.Image) -> Image.Image:
    """Apply EXIF orientation transform when present."""
    return ImageOps.exif_transpose(image)


def load_image(path: Path) -> Image.Image:
    """Load an image from disk and normalize EXIF orientation.

    GIF files are read as their first frame only.
    """
    if not path.exists():
        raise ValidationError(f"Input file does not exist: {path}")
    if not path.is_file():
        raise ValidationError(f"Input is not a file: {path}")

    try:
        with Image.open(path) as image:
            if (image.format or "").upper() == "GIF":
                image.seek(0)
                return image.convert("RGBA")

            normalized = normalize_orientation(image)
            return normalized.copy()
    except OSError as exc:
        raise ProcessingError(f"Failed to read image '{path}': {exc}") from exc


def opacity_to_alpha(opacity: int) -> int:
    """Convert opacity percentage (0-100) to alpha channel value (0-255)."""
    if not 0 <= opacity <= 100:
        raise ValidationError("Opacity must be between 0 and 100.")
    return round((opacity / 100) * 255)


def apply_opacity(image: Image.Image, opacity: int) -> Image.Image:
    """Apply a global opacity multiplier to the image alpha channel."""
    alpha_target = opacity_to_alpha(opacity)

    image_rgba = image.convert("RGBA")
    if alpha_target == 255:
        return image_rgba

    multiplier = alpha_target / 255
    _, _, _, a = image_rgba.split()
    a = a.point(lambda value: int(round(value * multiplier)))
    image_rgba.putalpha(a)
    return image_rgba


def compute_position(
    base_size: tuple[int, int],
    overlay_size: tuple[int, int],
    position: Position,
    margin: int = DEFAULT_MARGIN,
) -> tuple[int, int]:
    """Compute top-left placement for a watermark overlay."""
    base_w, base_h = base_size
    overlay_w, overlay_h = overlay_size

    if position == "tl":
        x, y = margin, margin
    elif position == "tr":
        x, y = base_w - overlay_w - margin, margin
    elif position == "bl":
        x, y = margin, base_h - overlay_h - margin
    elif position == "br":
        x, y = base_w - overlay_w - margin, base_h - overlay_h - margin
    elif position == "c":
        x, y = (base_w - overlay_w) // 2, (base_h - overlay_h) // 2
    else:
        raise ValidationError(f"Unsupported position '{position}'. Use tl, tr, bl, br, or c.")

    if overlay_w >= base_w:
        x = 0
    else:
        x = clamp(x, 0, base_w - overlay_w)

    if overlay_h >= base_h:
        y = 0
    else:
        y = clamp(y, 0, base_h - overlay_h)

    return x, y


def _load_font(font_size: int, font_path: Path | None = None) -> ImageFont.ImageFont:
    if font_path is not None and font_path.exists():
        try:
            return ImageFont.truetype(str(font_path), font_size)
        except OSError:
            pass

    for candidate in ("DejaVuSans.ttf", "Arial.ttf", "arial.ttf", "LiberationSans-Regular.ttf"):
        try:
            return ImageFont.truetype(candidate, font_size)
        except OSError:
            continue

    return ImageFont.load_default()


def _build_image_stamp(base_size: tuple[int, int], watermark_path: Path) -> Image.Image:
    if not watermark_path.exists():
        raise ValidationError(f"Watermark image does not exist: {watermark_path}")

    watermark = load_image(watermark_path).convert("RGBA")
    base_w, _ = base_size
    max_target = max(48, int(base_w * 0.8))
    target_w = clamp(int(base_w * 0.2), 48, max_target)

    if watermark.width != target_w:
        target_h = max(1, int(watermark.height * (target_w / watermark.width)))
        watermark = watermark.resize((target_w, target_h), Image.Resampling.LANCZOS)

    return watermark


def _build_text_stamp(base_size: tuple[int, int], text: str, font_path: Path | None = None) -> Image.Image:
    clean_text = text.strip()
    if not clean_text:
        raise ValidationError("Text watermark cannot be empty.")

    base_w, _ = base_size
    font_size = clamp(int(base_w * 0.05), 16, 256)
    font = _load_font(font_size, font_path=font_path)
    stroke = max(1, font_size // 20)
    shadow_offset = max(1, font_size // 14)

    dummy = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    draw_dummy = ImageDraw.Draw(dummy)
    bbox = draw_dummy.textbbox((0, 0), clean_text, font=font, stroke_width=stroke)
    text_w = max(1, bbox[2] - bbox[0])
    text_h = max(1, bbox[3] - bbox[1])

    stamp = Image.new("RGBA", (text_w + shadow_offset, text_h + shadow_offset), (0, 0, 0, 0))
    draw = ImageDraw.Draw(stamp)

    draw.text(
        (shadow_offset, shadow_offset),
        clean_text,
        font=font,
        fill=(0, 0, 0, 180),
        stroke_width=stroke,
        stroke_fill=(0, 0, 0, 200),
    )
    draw.text(
        (0, 0),
        clean_text,
        font=font,
        fill=(255, 255, 255, 255),
        stroke_width=stroke,
        stroke_fill=(0, 0, 0, 220),
    )

    return stamp


def build_watermark_layer(
    base_size: tuple[int, int],
    watermark_path: Path | None = None,
    text: str | None = None,
    position: Position = DEFAULT_POSITION,
    opacity: int = DEFAULT_OPACITY,
    margin: int = DEFAULT_MARGIN,
    font_path: Path | None = None,
) -> Image.Image:
    """Build a full-size RGBA watermark layer ready to composite."""
    if (watermark_path is None) == (text is None):
        raise ValidationError("Exactly one of watermark_path or text must be provided.")

    if watermark_path is not None:
        stamp = _build_image_stamp(base_size, watermark_path)
    else:
        stamp = _build_text_stamp(base_size, text or "", font_path=font_path)

    stamp = apply_opacity(stamp, opacity)
    layer = Image.new("RGBA", base_size, (0, 0, 0, 0))
    x, y = compute_position(base_size, stamp.size, position, margin=margin)
    layer.alpha_composite(stamp, dest=(x, y))
    return layer


def composite(base_image: Image.Image, watermark_layer: Image.Image) -> Image.Image:
    """Composite watermark layer onto base image using alpha compositing."""
    base_rgba = base_image.convert("RGBA")
    if base_rgba.size != watermark_layer.size:
        raise ValidationError("Base image and watermark layer must have the same size.")
    return Image.alpha_composite(base_rgba, watermark_layer)


def infer_output_format(path: Path) -> str:
    """Infer Pillow save format from output file extension."""
    extension = path.suffix.lower()
    mapping = {
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".png": "PNG",
        ".webp": "WEBP",
        ".tiff": "TIFF",
        ".bmp": "BMP",
        ".gif": "GIF",
    }
    if extension not in mapping:
        raise ValidationError(f"Unsupported output format '{extension}'.")
    return mapping[extension]


def save_image(image: Image.Image, path: Path) -> None:
    """Save image to disk, handling format-specific mode requirements."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fmt = infer_output_format(path)

    if fmt == "JPEG":
        image.convert("RGB").save(path, format=fmt, quality=95)
    elif fmt == "GIF":
        image.convert("RGBA").save(path, format=fmt)
    else:
        image.save(path, format=fmt)


def default_single_output(input_path: Path) -> Path:
    """Compute default output path for single-file mode."""
    suffix = input_path.suffix.lower()
    return input_path.with_name(f"{input_path.stem}_watermarked{suffix}")


def ensure_unique_path(path: Path, suffix: str = "_watermarked") -> Path:
    """Create a non-colliding output path by appending a suffix when needed."""
    if not path.exists():
        return path

    candidate = path.with_name(f"{path.stem}{suffix}{path.suffix}")
    counter = 2
    while candidate.exists():
        candidate = path.with_name(f"{path.stem}{suffix}{counter}{path.suffix}")
        counter += 1

    return candidate


def resolve_input(
    input_value: str,
    recursive: bool = False,
) -> tuple[Literal["single", "folder", "glob"], list[Path], Path | None]:
    """Resolve input argument into mode, file list, and source root (when applicable)."""
    candidate = Path(input_value)

    if candidate.exists():
        resolved = candidate.resolve()
        if resolved.is_file():
            if not is_supported_image(resolved):
                raise ValidationError(
                    f"Unsupported input format '{resolved.suffix}'. Supported: "
                    + ", ".join(sorted(SUPPORTED_EXTENSIONS))
                )
            return "single", [resolved], resolved.parent

        if resolved.is_dir():
            pattern = "**/*" if recursive else "*"
            files = sorted(
                file.resolve()
                for file in resolved.glob(pattern)
                if file.is_file() and is_supported_image(file)
            )
            return "folder", files, resolved

        raise ValidationError(f"Input path is not a file or folder: {input_value}")

    if has_magic(input_value):
        matches = sorted({Path(path).resolve() for path in glob(input_value, recursive=True)})
        files = [path for path in matches if path.is_file() and is_supported_image(path)]
        return "glob", files, None

    raise ValidationError(
        "Input does not exist and is not a valid glob pattern. "
        "Provide a file, folder, or glob such as './images/*.png'."
    )


def process_single(
    input_path: Path,
    output_path: Path,
    watermark_path: Path | None = None,
    text: str | None = None,
    position: Position = DEFAULT_POSITION,
    opacity: int = DEFAULT_OPACITY,
    overwrite: bool = False,
    dry_run: bool = False,
    margin: int = DEFAULT_MARGIN,
    font_path: Path | None = None,
) -> Path:
    """Process one image and return the final output path."""
    final_output = output_path if overwrite else ensure_unique_path(output_path)

    if dry_run:
        return final_output

    base_image = load_image(input_path)
    watermark_layer = build_watermark_layer(
        base_image.size,
        watermark_path=watermark_path,
        text=text,
        position=position,
        opacity=opacity,
        margin=margin,
        font_path=font_path,
    )
    composed = composite(base_image, watermark_layer)
    save_image(composed, final_output)
    return final_output


def process_batch(
    input_files: list[Path],
    output_root: Path,
    watermark_path: Path | None = None,
    text: str | None = None,
    position: Position = DEFAULT_POSITION,
    opacity: int = DEFAULT_OPACITY,
    overwrite: bool = False,
    dry_run: bool = False,
    margin: int = DEFAULT_MARGIN,
    source_root: Path | None = None,
    font_path: Path | None = None,
) -> BatchResult:
    """Process a list of images and return batch summary."""
    result = BatchResult(output_root=output_root)

    for input_file in input_files:
        if not input_file.exists() or not input_file.is_file():
            result.skipped += 1
            result.failures.append((input_file, "Input file does not exist."))
            continue

        try:
            if source_root is not None:
                try:
                    relative_path = input_file.resolve().relative_to(source_root.resolve())
                except ValueError:
                    relative_path = Path(input_file.name)
            else:
                relative_path = Path(input_file.name)

            destination = output_root / relative_path
            final_destination = process_single(
                input_file,
                destination,
                watermark_path=watermark_path,
                text=text,
                position=position,
                opacity=opacity,
                overwrite=overwrite,
                dry_run=dry_run,
                margin=margin,
                font_path=font_path,
            )

            result.planned.append((input_file, final_destination))
            result.processed += 1
        except WatermarkerError as exc:
            result.failed += 1
            result.failures.append((input_file, str(exc)))
        except Exception as exc:  # pragma: no cover - defensive catch for CLI behavior
            result.failed += 1
            result.failures.append((input_file, f"Unexpected error: {exc}"))

    return result

