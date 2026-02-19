# watermarker: Python CLI to watermark images (batch watermark, logo watermark, text watermark)

[![CI](https://github.com/ibrahimm7004/add-watermark/actions/workflows/ci.yml/badge.svg)](https://github.com/ibrahimm7004/add-watermark/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/watermarker.svg)](https://pypi.org/project/watermarker/)
[![Python versions](https://img.shields.io/pypi/pyversions/watermarker.svg)](https://pypi.org/project/watermarker/)
[![License](https://img.shields.io/github/license/ibrahimm7004/add-watermark.svg)](LICENSE)

Python CLI for batch image watermarking with logo or text.

`watermarker` is built for people searching "how to add watermark to image", "add watermark to photo", "put watermark on picture", "add logo to image", "add text watermark to photo", "batch watermark images", "watermark multiple photos at once", and "protect photos with watermark" without uploading files to an online service.

## 20-Second Quickstart: watermark images with a Python CLI

```powershell
pipx install watermarker
watermarker add
# Expert one-liner: add text watermark to photo
watermarker add --input ".\photo.jpg" --text "(c) ACME" --pos br --opacity 40
```

## Install watermarker for batch watermark, logo watermark, and text watermark

### A) Install (Recommended): pipx

```powershell
pipx install watermarker
```

If `pipx` is not on PATH yet:

```powershell
pipx ensurepath
```

### B) Install (Alternative): pip

```powershell
python -m pip install watermarker
```

### C) Install from source (repo clone)

```powershell
git clone https://github.com/ibrahimm7004/add-watermark.git
cd add-watermark
```

Install from this repo with `pipx`:

```powershell
pipx install .
```

Install from this repo with `pip`:

```powershell
python -m pip install .
```

### D) Uninstall (pipx and pip)

```powershell
pipx uninstall watermarker
python -m pip uninstall watermarker
```

## Before and after: put watermark on picture

| Before | After |
| --- | --- |
| ![Before watermark example](examples/before.png) | ![After watermark example](examples/after.png) |

Regenerate both demo images:

```powershell
python examples/generate_examples.py
```

## Add watermark to photo: wizard and expert one-liners

Beginner wizard:

```powershell
watermarker add
```

Single image with text watermark:

```powershell
watermarker add --input ".\photo.jpg" --text "(c) ACME Studio" --pos br --opacity 40
```

Single image with logo watermark:

```powershell
watermarker add --input ".\photo.jpg" --watermark ".\logo.png" --pos tr --opacity 35
```

Batch watermark folder:

```powershell
watermarker add --input ".\photos" --watermark ".\logo.png" --pos br --opacity 35
```

Batch watermark folder recursively:

```powershell
watermarker add --input ".\photos" --recursive --text "(c) ACME" --pos br --opacity 35
```

Glob input:

```powershell
watermarker add --input ".\photos\**\*.png" --watermark ".\logo.png" --opacity 35
```

Dry run (plan only):

```powershell
watermarker add --input ".\photos" --watermark ".\logo.png" --dry-run
```

## Defaults

`watermarker add` defaults (from current implementation):

- Default position: `br`
- Default opacity: `35` (`0` is invisible, `100` is fully visible)
- Default corner margin: `24px`
- Image watermark default scale: target width is about `20%` of base image width, clamped to at least `48px` and at most `80%` of base width
- Text watermark default scale: font size is about `5%` of image width, clamped to `16..256`
- Text watermark style: white text with black stroke and subtle shadow for readability
- Single-image default output: `<input_stem>_watermarked.<ext>` next to input
- Batch default output (folder input): `watermarked/` next to the input folder
- Batch default output (glob input): `./watermarked/` in current working directory
- Batch mode preserves relative folder structure for folder input
- Without `--overwrite`, existing destination paths are not replaced; a `_watermarked` suffix is appended to avoid collisions

## Windows notes

- Quote paths that contain spaces:
  - PowerShell/CMD: `--input "C:\Users\me\My Photos\photo 01.jpg"`
- Quote globs to keep behavior consistent across shells and avoid shell expansion differences:
  - `--input ".\photos\**\*.jpg"`
- PowerShell example:

```powershell
watermarker add --input ".\My Photos\Client A" --recursive --text "(c) ACME" --pos br --opacity 35
```

- CMD example:

```cmd
watermarker add --input ".\My Photos\*.jpg" --watermark ".\brand logo.png" --pos tr --opacity 35
```

## Why offline CLI (vs online watermark tools)

If you are searching for "add watermark to image online free", an offline CLI is often better for production workflows:

- Privacy: images stay on your machine
- Speed: no upload/download loop
- Batch scale: watermark hundreds of files in one command
- Automation: scriptable for product photos, photography delivery, and repeatable pipelines

## Supported formats and behavior

- Input/output formats: `jpg`, `jpeg`, `png`, `webp`, `tiff`, `bmp`, `gif`
- GIF behavior: first frame only
- JPEG output is written as RGB (quality 95)
- PNG/WEBP preserve alpha when present

## Common searches this tool solves

- how to add watermark to image
- add watermark to photo
- put watermark on picture
- how to watermark a photo
- add logo to image
- add text watermark to photo
- batch watermark images
- bulk watermark photos
- watermark multiple photos at once
- add watermark to 100 photos
- signature watermark
- copyright watermark on images

## CLI reference

```text
watermarker add [OPTIONS]

Options:
  --input, -i      File path, folder path, or glob pattern
  --output, -o     Output file (single mode) or output folder (batch mode)
  --watermark, -w  Watermark image path
  --text, -t       Text watermark content
  --pos            Watermark position: tl|tr|bl|br|c
  --opacity        Opacity 0-100 (0 invisible, 100 fully visible)
  --recursive      Recurse subfolders for folder input
  --overwrite      Overwrite existing outputs
  --dry-run        Print planned outputs without writing files
  --verbose        Show traceback/debug details
```

Validation rules:

- Exactly one of `--watermark` or `--text` in non-interactive mode
- If `--input` is missing, wizard prompts for required fields

## Library usage (optional)

CLI is the primary interface. If you need direct Python usage:

```python
from pathlib import Path

from watermarker.engine import process_single

process_single(
    input_path=Path("photo.jpg"),
    output_path=Path("photo_watermarked.jpg"),
    text="(c) ACME",
    position="br",
    opacity=35,
    overwrite=True,
)
```

## Open source trust signals

- CI workflow: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)
- Tests: `pytest` suite for position logic, opacity mapping, and integration behavior
- Lint/format checks: `ruff check .` and `ruff format --check .`
- Contribution guide: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Code of conduct: [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
- Changelog: [`CHANGELOG.md`](CHANGELOG.md)
- License: [`MIT`](LICENSE)

## FAQ and troubleshooting

### `watermarker` command is not found on Windows

- For `pipx` installs, run `pipx ensurepath` and restart terminal.
- For `pip` installs, ensure your Python Scripts directory is on PATH.

### Why does GIF output look static?

- v1 processes only the first GIF frame.

### Why can text look slightly different across machines?

- The tool tries common system fonts first and falls back to Pillow default when needed.

## Development

```powershell
python -m pip install -e .[dev]
ruff check .
ruff format --check .
pytest
```
