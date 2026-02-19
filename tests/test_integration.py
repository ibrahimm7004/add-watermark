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

