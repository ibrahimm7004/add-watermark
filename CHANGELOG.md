# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed

- Changed PyPI distribution name to `add-watermark`; updated README install instructions and badges.
- Fixed project metadata URLs in `pyproject.toml` to point to the real GitHub repository.
- Added Windows CI coverage (`windows-latest`) alongside Linux with Python 3.10, 3.11, and 3.12.
- Improved GIF output saving by palette-converting composited RGBA images before writing GIF files.
- Clarified the wizard opacity prompt to explicitly state `0=invisible` and `100=fully visible`.
- Clarified README glob-output behavior for how folder structure is preserved relative to CWD.

### Added

- New text watermark integration test.
- New collision naming test for non-overwrite output behavior.

## [0.1.0] - 2026-02-19

### Added

- Initial release of `watermarker` CLI.
- `add` command with interactive wizard and expert flag mode.
- Image and text watermark support.
- Single image, folder batch, and glob input handling.
- EXIF orientation normalization.
- Dry-run and verbose error modes.
- Test suite for positioning, opacity mapping, and integration watermarking.
- GitHub Actions CI for lint, format checks, and tests.

