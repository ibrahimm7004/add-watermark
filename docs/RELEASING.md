# Releasing add-watermark

This project uses Semantic Versioning (`MAJOR.MINOR.PATCH`) and Keep a Changelog.

## Release checklist

1. Bump version in `pyproject.toml`.
2. Update `CHANGELOG.md`.
3. Commit release changes:

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "release: vX.Y.Z"
```

4. Create a version tag:

```bash
git tag vX.Y.Z
```

5. Push main:

```bash
git push origin main
```

6. Push tag:

```bash
git push origin vX.Y.Z
```

7. Publishing:
   - Pushing `vX.Y.Z` triggers `.github/workflows/publish.yml`.
   - The workflow builds `dist/` artifacts and publishes to PyPI using Trusted Publishing (OIDC).
