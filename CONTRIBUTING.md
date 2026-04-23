# Contributing

Thanks for taking the time to look at this. A few notes so you don't have to guess.

## What lands easily

- Bug fixes with a failing test that the fix makes pass.
- New backends or dialects (anything async SQLAlchemy can talk to), with at least one integration test path.
- Docs and example improvements.
- Small API ergonomics fixes, if discussed in an issue first.

## What I'd rather discuss before you write code

- Changes to the `BaseMemoryService` method signatures or behavioural contract. These have to stay compatible with upstream ADK.
- New dependencies in the base install. The base install is deliberately driver-free.
- Anything that changes the `adk_memory_entries` schema.

Open an issue first so we don't have a sad PR-close conversation.

## Local setup

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

The `dev` extra pulls in `aiosqlite`, `pytest`, `pytest-asyncio`, `ruff`, and `mypy`. That's enough to run the full suite locally against SQLite.

To run tests against Postgres or MySQL you'll need those drivers and a reachable instance. The CI only exercises SQLite; integration tests against Postgres / MySQL are run manually.

## Running checks

```bash
pytest                # unit tests
ruff check .          # lint
mypy src              # type check
```

These three run in CI on Python 3.10, 3.11, 3.12, and 3.13, along with a package build step. A PR can only merge when all of them are green.

Ruff formatting is not currently enforced in CI but is handy locally: `ruff format .` to format, `ruff format --check .` to verify.

## Opening a PR

- Branch off `main`.
- Keep commits small and focused. Squash-merge is enabled on the repo so internal commit hygiene matters less than the final squash commit message.
- Reference the issue number in the PR description if one exists.
- If you're adding a user-visible change, update `CHANGELOG.md` under `[Unreleased]`.

## Releasing (maintainer note)

Release flow is documented in [`PUBLISHING.md`](./PUBLISHING.md). It uses PyPI trusted publishing, no stored tokens.
