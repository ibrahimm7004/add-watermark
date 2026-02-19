from pathlib import Path

from PIL import Image

from watermarker.engine import process_single


def test_process_single_writes_output_and_changes_watermark_region(tmp_path: Path) -> None:
    source_path = tmp_path / "source.png"
    watermark_path = tmp_path / "wm.png"
    output_path = tmp_path / "output.png"

    base = Image.new("RGBA", (400, 240), (10, 30, 80, 255))
    base.save(source_path)

    watermark = Image.new("RGBA", (120, 60), (250, 20, 20, 255))
    watermark.save(watermark_path)

    final_path = process_single(
        source_path,
        output_path,
        watermark_path=watermark_path,
        position="tl",
        opacity=100,
        overwrite=True,
    )

    assert final_path.exists()

    with Image.open(source_path) as original_image, Image.open(final_path) as output_image:
        original_pixel = original_image.convert("RGBA").getpixel((30, 30))
        output_pixel = output_image.convert("RGBA").getpixel((30, 30))

    assert original_pixel != output_pixel


def test_process_single_text_watermark_changes_pixels(tmp_path: Path) -> None:
    source_path = tmp_path / "source_text.png"
    output_path = tmp_path / "output_text.png"

    base = Image.new("RGBA", (400, 240), (12, 24, 48, 255))
    base.save(source_path)

    final_path = process_single(
        source_path,
        output_path,
        text="CONFIDENTIAL",
        position="tl",
        opacity=100,
        overwrite=True,
    )

    assert final_path.exists()

    with Image.open(source_path) as original_image, Image.open(final_path) as watermarked_image:
        original_rgba = original_image.convert("RGBA")
        watermarked_rgba = watermarked_image.convert("RGBA")

        changed = any(
            original_rgba.getpixel((x, y)) != watermarked_rgba.getpixel((x, y))
            for x in range(24, 220)
            for y in range(24, 140)
        )

    assert changed


def test_process_single_avoids_collision_when_not_overwriting(tmp_path: Path) -> None:
    source_path = tmp_path / "source_collision.png"
    first_output = tmp_path / "output.png"

    base = Image.new("RGBA", (320, 200), (30, 60, 90, 255))
    base.save(source_path)

    first_path = process_single(
        source_path,
        first_output,
        text="(c) ACME",
        position="br",
        opacity=60,
        overwrite=False,
    )
    second_path = process_single(
        source_path,
        first_output,
        text="(c) ACME",
        position="br",
        opacity=60,
        overwrite=False,
    )

    assert first_path.exists()
    assert second_path.exists()
    assert first_path != second_path
    assert "_watermarked" in second_path.stem
