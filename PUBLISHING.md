# Publishing

## First-time PyPI setup (one-time, ~2 minutes)

1. Go to https://pypi.org/manage/account/publishing/ and add a "Pending Publisher":
   - PyPI Project Name: `adk-database-memory`
   - Owner: `anmolg1997`
   - Repository name: `adk-database-memory`
   - Workflow name: `release.yml`
   - Environment name: `pypi`
2. In GitHub, create an environment named `pypi` for the repo (Settings > Environments > New). No secrets needed; trusted publishing uses OIDC.

## Cut a release

```bash
# bump version in src/adk_database_memory/__init__.py and pyproject.toml
git commit -am "release: v0.1.0"
git tag v0.1.0
git push --tags
```

The `.github/workflows/release.yml` workflow runs on tag push, builds the sdist + wheel, and uses `pypa/gh-action-pypi-publish` with OIDC to publish.

## Manual fallback

```bash
python -m build
twine upload dist/*
```
