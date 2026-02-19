# Contributing

Thanks for contributing to `watermarker`.

## Setup

1. Create and activate a Python 3.10+ virtual environment.
2. Install project in editable mode with dev tools:

```bash
python -m pip install -e .[dev]
```

## Local checks

Run before opening a PR:

```bash
ruff check .
ruff format --check .
pytest
```

## Pull requests

- Keep changes scoped and focused.
- Add or update tests for behavioral changes.
- Update `README.md` and `CHANGELOG.md` when relevant.
- Ensure CI is green.

## Reporting issues

Please include:

- operating system and Python version
- exact command run
- full error output (`--verbose` if relevant)
- minimal repro input files/patterns when possible

