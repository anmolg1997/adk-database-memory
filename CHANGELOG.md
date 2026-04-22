# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-04-21

Initial release.

### Added

- `DatabaseMemoryService`: persistent `BaseMemoryService` for Google ADK Python, backed by any async SQLAlchemy database.
- Backend support: SQLite (via `aiosqlite`), PostgreSQL (via `asyncpg`), MySQL / MariaDB (via `aiomysql`), or any user-supplied async SQLAlchemy driver.
- `DynamicJSON` type decorator: stores JSON content as `JSONB` on PostgreSQL, `LONGTEXT` on MySQL, `TEXT` on SQLite and other dialects.
- Lazy, double-checked async table creation. Single indexed table `adk_memory_entries` with an index on `(app_name, user_id)`.
- Keyword-extraction and matching that mirrors the in-memory and Firestore memory services in ADK core.
- Async context manager support (`async with DatabaseMemoryService(url) as memory:`) and explicit `close()`.
- Configurable stop-words set via the `stop_words=` constructor argument.
- 19 unit tests covering ingestion, search, deduplication, scoping, and lifecycle.
- CI across Python 3.10, 3.11, 3.12, 3.13. Lint (`ruff`), type check (`mypy`), tests (`pytest`).
- PyPI trusted publishing via OIDC, no stored secrets.

### Listed

- Now appears in the official Google ADK integrations catalog: https://google.github.io/adk-docs/integrations/database-memory/

[Unreleased]: https://github.com/anmolg1997/adk-database-memory/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/anmolg1997/adk-database-memory/releases/tag/v0.1.0
