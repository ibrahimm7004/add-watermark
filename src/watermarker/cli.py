"""CLI entrypoint for watermarker."""

from __future__ import annotations

from pathlib import Path

import click
import typer
from rich.console import Console

from watermarker.engine import (
    DEFAULT_OPACITY,
    DEFAULT_POSITION,
    BatchResult,
    ValidationError,
    WatermarkerError,
    default_single_output,
    ensure_unique_path,
    process_batch,
    process_single,
    resolve_input,
)

app = typer.Typer(
    name="watermarker",
    help="Python CLI for batch image watermarking with logo or text.",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


@app.callback()
def root() -> None:
    """Watermarker command group."""


def _prompt_choice(prompt: str, options: list[str], default: str) -> str:
    choice = typer.prompt(
        prompt,
        type=click.Choice(options, case_sensitive=False),
        default=default,
        show_choices=True,
    )
    return choice.lower()


def _run_wizard(
    input_value: str | None,
    output: str | None,
    watermark: Path | None,
    text: str | None,
    pos: str | None,
    opacity: int | None,
    recursive: bool,
) -> tuple[str, str | None, Path | None, str | None, str, int, bool]:
    if input_value is None:
        mode = _prompt_choice("Select mode", ["single", "batch"], "single")
        if mode == "single":
            input_value = typer.prompt("Input image path")
        else:
            input_value = typer.prompt("Input folder path or glob pattern")
            if not recursive:
                recursive = typer.confirm("Search folders recursively?", default=True)

    if watermark is None and text is None:
        watermark_type = _prompt_choice("Watermark type", ["image", "text"], "image")
        if watermark_type == "image":
            watermark = Path(typer.prompt("Watermark image path"))
        else:
            text = typer.prompt("Watermark text")

    if pos is None:
        pos = _prompt_choice("Position", ["tl", "tr", "bl", "br", "c"], DEFAULT_POSITION)

    if opacity is None:
        opacity = typer.prompt("Opacity (0-100)", type=int, default=DEFAULT_OPACITY)

    if output is None:
        output_value = typer.prompt("Output path (leave blank for default)", default="")
        output = output_value.strip() or None

    return input_value, output, watermark, text, pos, opacity, recursive


def _single_output_path(input_path: Path, output: str | None, overwrite: bool) -> Path:
    if output is None:
        target = default_single_output(input_path)
    else:
        output_path = Path(output)
        if output_path.exists() and output_path.is_dir():
            target = output_path / default_single_output(input_path).name
        elif output_path.suffix:
            target = output_path
        else:
            target = output_path / default_single_output(input_path).name

    if overwrite:
        return target
    return ensure_unique_path(target)


def _batch_output_root(mode: str, input_value: str, output: str | None, source_root: Path | None) -> Path:
    if output:
        return Path(output)

    if mode == "folder" and source_root is not None:
        return source_root.parent / "watermarked"

    return Path.cwd() / "watermarked"


def _print_batch_summary(result: BatchResult, dry_run: bool) -> None:
    label = "planned" if dry_run else "processed"
    console.print(f"{label}: {result.processed}")
    console.print(f"skipped: {result.skipped}")
    console.print(f"failed: {result.failed}")
    if result.output_root is not None:
        console.print(f"output: {result.output_root}")


@app.command()
def add(
    input_value: str | None = typer.Option(
        None,
        "--input",
        "-i",
        help="Input image file, folder path, or glob pattern.",
    ),
    output: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file (single mode) or output folder (batch mode).",
    ),
    watermark: Path | None = typer.Option(
        None,
        "--watermark",
        "-w",
        help="Watermark image path.",
    ),
    text: str | None = typer.Option(
        None,
        "--text",
        "-t",
        help="Text watermark content.",
    ),
    pos: str | None = typer.Option(
        None,
        "--pos",
        help="Watermark position: tl, tr, bl, br, c.",
    ),
    opacity: int | None = typer.Option(
        None,
        "--opacity",
        min=0,
        max=100,
        help="Watermark opacity from 0 (invisible) to 100 (fully visible).",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        help="Process subfolders recursively when --input points to a folder.",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite output files when they already exist.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Print planned outputs without writing files.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Show traceback details for errors.",
    ),
) -> None:
    """Add image or text watermarks to single images or batches."""
    interactive = input_value is None or (watermark is None and text is None)

    try:
        if interactive:
            input_value, output, watermark, text, pos, opacity, recursive = _run_wizard(
                input_value,
                output,
                watermark,
                text,
                pos,
                opacity,
                recursive,
            )

        if input_value is None:
            raise ValidationError("--input is required.")

        if watermark is not None and text is not None:
            raise ValidationError("Use exactly one of --watermark or --text.")

        if watermark is None and text is None:
            raise ValidationError("Provide one of --watermark or --text.")

        if pos is None:
            pos = DEFAULT_POSITION

        if opacity is None:
            opacity = DEFAULT_OPACITY

        mode, files, source_root = resolve_input(input_value, recursive=recursive)
        if not files:
            raise ValidationError("No supported input images were found.")

        if mode == "single":
            source = files[0]
            target = _single_output_path(source, output=output, overwrite=overwrite)
            final_path = process_single(
                source,
                target,
                watermark_path=watermark,
                text=text,
                position=pos,
                opacity=opacity,
                overwrite=True,
                dry_run=dry_run,
            )
            if dry_run:
                console.print(f"DRY-RUN: {source} -> {final_path}")
            else:
                console.print(final_path)
            raise typer.Exit(code=0)

        output_root = _batch_output_root(mode, input_value, output, source_root)
        result = process_batch(
            files,
            output_root=output_root,
            watermark_path=watermark,
            text=text,
            position=pos,
            opacity=opacity,
            overwrite=overwrite,
            dry_run=dry_run,
            source_root=source_root if mode == "folder" else Path.cwd(),
        )

        for source, destination in result.planned:
            if dry_run:
                console.print(f"DRY-RUN: {source} -> {destination}")

        _print_batch_summary(result, dry_run=dry_run)

        if result.failed:
            raise typer.Exit(code=1)

        raise typer.Exit(code=0)

    except ValidationError as exc:
        console.print(f"[red]Error:[/] {exc}")
        if verbose:
            console.print_exception(show_locals=False)
        raise typer.Exit(code=2) from exc
    except WatermarkerError as exc:
        console.print(f"[red]Error:[/] {exc}")
        if verbose:
            console.print_exception(show_locals=False)
        raise typer.Exit(code=1) from exc
    except typer.Exit:
        raise
    except Exception as exc:  # pragma: no cover - defensive fallback for CLI
        console.print(f"[red]Unexpected error:[/] {exc}")
        if verbose:
            console.print_exception(show_locals=True)
        else:
            console.print("Run with --verbose to see traceback details.")
        raise typer.Exit(code=1) from exc


def main() -> None:
    """Run the Typer app."""
    app()


if __name__ == "__main__":
    main()

