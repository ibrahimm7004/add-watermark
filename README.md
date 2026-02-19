# watermarker

Python CLI for batch image watermarking with logo or text.

`watermarker` is a production-focused command-line tool for applying image or text watermarks to single images, folders, or glob matches.

## Features

- CLI-first workflow using Typer
- Beginner-friendly interactive wizard (`watermarker add`)
- Expert one-liner mode with full flags
- Image watermark or text watermark
- Supported inputs: `jpg`, `jpeg`, `png`, `webp`, `tiff`, `bmp`, `gif`
- GIF support processes the first frame only
- EXIF orientation correction on load
- Batch output summary with processed/skipped/failed counts
- Dry-run planning mode (`--dry-run`)

## Install

### pipx (recommended for CLI tools)

```bash
pipx install .
```

### pip

```bash
python -m pip install .
```

For development:

```bash
python -m pip install -e .[dev]
```

## Quickstart (Beginner Wizard)

Run without required arguments and the wizard will prompt for everything:

```bash
watermarker add
```

You will be prompted for:

- single vs batch mode
- input path/pattern
- watermark type (image or text)
- watermark image path or text content
- position (`tl`, `tr`, `bl`, `br`, `c`)
- opacity (`0-100`, where `100` is fully visible)
- output path

## Expert One-Liners

Single image + image watermark:

```bash
watermarker add --input .\photo.jpg --watermark .\logo.png --pos br --opacity 40
```

Single image + text watermark:

```bash
watermarker add --input .\photo.png --text "(c) ACME" --pos tr --opacity 60
```

Folder batch (non-recursive):

```bash
watermarker add --input .\images --watermark .\logo.png --opacity 35
```

Folder batch (recursive):

```bash
watermarker add --input .\images --recursive --text "CONFIDENTIAL" --pos c --opacity 25
```

Glob input:

```bash
watermarker add --input ".\images\**\*.png" --watermark .\logo.png --opacity 30
```

Dry-run planning:

```bash
watermarker add --input .\images --watermark .\logo.png --dry-run
```

## CLI Reference

```text
watermarker add [OPTIONS]

Options:
  --input, -i      File, folder, or glob pattern
  --output, -o     Output file (single) or output folder (batch)
  --watermark, -w  Watermark image path
  --text, -t       Text watermark content
  --pos            Watermark position: tl|tr|bl|br|c
  --opacity        Opacity 0-100 (0 invisible, 100 fully visible)
  --recursive      Recurse subfolders for folder input
  --overwrite      Overwrite existing outputs
  --dry-run        Print planned outputs without writing
  --verbose        Show traceback/debug details on errors
```

Validation:

- Exactly one of `--watermark` or `--text` must be provided in non-interactive mode.
- If `--input` is missing, the wizard prompts for it.

## Output Rules

Single input defaults:

- Output path defaults to `<input_stem>_watermarked.<ext>` next to input.

Batch defaults:

- Folder input defaults to `watermarked/` next to the input folder.
- Glob input defaults to `./watermarked/` in the current working directory.
- Folder mode preserves relative folder structure under output.

Overwrite behavior:

- Without `--overwrite`, output collisions are avoided by adding `_watermarked` (and incrementing if needed).
- With `--overwrite`, existing output paths are replaced.

## Watermark Defaults (v1)

- Corner margin: `24px`
- Image watermark scale: target width is ~20% of base image width (with clamp)
- Text watermark font size: derived from image width (~5% with clamp)
- Text styling: white text with subtle black stroke/shadow for readability

Font behavior:

- `watermarker` attempts common system fonts first.
- If unavailable, it falls back to Pillow's default font.

## Supported Formats

Input and output formats:

- `jpg`, `jpeg`, `png`, `webp`, `tiff`, `bmp`, `gif`

Notes:

- GIF processing uses only the first frame.
- JPEG output is saved as RGB (quality 95).
- PNG/WEBP preserve alpha when present.

## Exit Codes

- `0`: success
- `1`: processing/runtime error
- `2`: argument/validation error

## Troubleshooting (FAQ)

### `watermarker` command is not found on Windows

- If you installed with pip, make sure your Python scripts directory is on `PATH`.
- With pipx, run `pipx ensurepath` and restart the terminal.

### Pillow install issues

- Upgrade pip first: `python -m pip install --upgrade pip`
- Then reinstall: `python -m pip install -e .[dev]`

### Why does my GIF output look static?

- v1 intentionally processes only the first frame of GIFs.

### Why is text font different across machines?

- The tool tries common system fonts and falls back to Pillow default if needed.

## Development

Run checks locally:

```bash
ruff check .
ruff format --check .
pytest
```

