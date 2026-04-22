# Publishing

This package is published to PyPI via GitHub Actions trusted publishing (OIDC). No API tokens or secrets are stored anywhere.

- PyPI project: https://pypi.org/project/adk-database-memory/
- PyPI account: `anmolg1997`
- Trigger: pushing a Git tag matching `v*` to `main`

## Cut a release

1. Bump the version in two places (must match):

   - `pyproject.toml` -> `[project] version = "x.y.z"`
   - `src/adk_database_memory/__init__.py` -> `__version__ = "x.y.z"`

2. Commit, tag, and push both the commit and the tag:

   ```bash
   git commit -am "release: vX.Y.Z"
   git tag -a vX.Y.Z -m "vX.Y.Z"
   git push origin main
   git push origin vX.Y.Z
   ```

   Note: `git push --tags` only pushes tags, not commits. Push both explicitly.

3. Watch the workflow:

   ```bash
   gh run watch --repo anmolg1997/adk-database-memory --exit-status
   ```

   The workflow at `.github/workflows/release.yml` builds sdist + wheel and publishes via `pypa/gh-action-pypi-publish`.

4. Cut a GitHub Release on the same tag with notes:

   ```bash
   gh release create vX.Y.Z --repo anmolg1997/adk-database-memory \
     --title "vX.Y.Z" --notes-file RELEASE_NOTES.md
   ```

5. Verify:

   ```bash
   curl -s https://pypi.org/pypi/adk-database-memory/json | jq '.info.version'
   pip install --upgrade adk-database-memory
   ```

## Re-publishing the same version

PyPI does not allow re-uploading a version once it has been published, even if you delete the release. To "fix" a published version you must bump and release a new one (e.g. `0.1.0` -> `0.1.1`). The only exception is before the first successful upload, where you can delete the tag, fix, and re-tag the same version:

```bash
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z
# fix things, then re-tag and push as in step 2
```

## Trusted publisher (one-time setup, already done)

Already configured for this repo. Documented here so the same setup can be reproduced for forks or new packages.

On https://pypi.org/manage/account/publishing/, under "Add a pending publisher" (for a brand-new project) or the project's "Publishing" tab (after the first release), add a Trusted Publisher with these exact fields:

- PyPI Project Name: `adk-database-memory`
- Owner: `anmolg1997`
- Repository name: `adk-database-memory`
- Workflow name: `release.yml`
- Environment name: *(leave blank)*

No matching GitHub Actions environment exists in this repo; the workflow grants OIDC via `permissions: id-token: write` at the job level. If you add an environment constraint here, you must also add it on the PyPI side, and vice versa - mismatches produce `invalid-publisher` errors.

## Manual fallback

If trusted publishing is broken (e.g. PyPI outage), publish from a local machine using a project-scoped API token:

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine upload dist/*
```

You will be prompted for a username (`__token__`) and password (the API token from https://pypi.org/manage/account/token/). Do not commit the token.
