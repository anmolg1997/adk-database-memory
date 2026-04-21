# adk-database-memory

SQL-backed memory service for the [Google Agent Development Kit (ADK)](https://github.com/google/adk-python).

Drop-in durable replacement for `InMemoryMemoryService`. Works with any async SQLAlchemy dialect: SQLite, PostgreSQL, MySQL/MariaDB, and more.

[![PyPI](https://img.shields.io/pypi/v/adk-database-memory.svg)](https://pypi.org/project/adk-database-memory/)
[![Python](https://img.shields.io/pypi/pyversions/adk-database-memory.svg)](https://pypi.org/project/adk-database-memory/)
[![CI](https://github.com/anmolg1997/adk-database-memory/actions/workflows/ci.yml/badge.svg)](https://github.com/anmolg1997/adk-database-memory/actions/workflows/ci.yml)
[![Downloads](https://img.shields.io/pypi/dm/adk-database-memory.svg)](https://pypi.org/project/adk-database-memory/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](./LICENSE)

## Why

ADK ships an in-memory memory service for development and a Vertex-hosted one for production on GCP. If you want durable memory on your own Postgres/SQLite/MySQL, there was no built-in option. This package fills that gap with the same `BaseMemoryService` contract, so you can swap it in without changing agent code.

## Install

```bash
pip install adk-database-memory[sqlite]       # SQLite (via aiosqlite)
pip install adk-database-memory[postgres]     # PostgreSQL (via asyncpg)
pip install adk-database-memory[mysql]        # MySQL / MariaDB (via aiomysql)
```

The base install does not pull any database driver. Pick the extra that matches your backend, or install your own async SQLAlchemy driver separately.

## Quick start

```python
import asyncio
from adk_database_memory import DatabaseMemoryService

async def main():
    # SQLite, zero-config
    async with DatabaseMemoryService("sqlite+aiosqlite:///memory.db") as memory:
        await memory.add_session_to_memory(session)

        result = await memory.search_memory(
            app_name="my_app",
            user_id="u1",
            query="what did we decide about the pricing model?",
        )
        for entry in result.memories:
            print(entry.author, entry.timestamp, entry.content)

asyncio.run(main())
```

### With an ADK `Runner`

```python
from google.adk.runners import Runner
from adk_database_memory import DatabaseMemoryService

memory = DatabaseMemoryService(
    "postgresql+asyncpg://user:pass@localhost:5432/agentdb"
)

runner = Runner(
    app_name="my_app",
    agent=my_agent,
    memory_service=memory,
    session_service=session_service,
)
```

## Supported backends

| Backend | URL example | Extra |
|---|---|---|
| SQLite | `sqlite+aiosqlite:///memory.db` | `[sqlite]` |
| SQLite (in-memory) | `sqlite+aiosqlite:///:memory:` | `[sqlite]` |
| PostgreSQL | `postgresql+asyncpg://user:pass@host/db` | `[postgres]` |
| MySQL / MariaDB | `mysql+aiomysql://user:pass@host/db` | `[mysql]` |
| Any async SQLAlchemy dialect | depends on driver | bring your own |

## API

The service implements `google.adk.memory.base_memory_service.BaseMemoryService`, so it exposes the same three methods used everywhere else in ADK:

- `add_session_to_memory(session)` - index every event of a session.
- `add_events_to_memory(app_name, user_id, events, ...)` - index a delta slice of events (useful for streaming ingestion).
- `search_memory(app_name, user_id, query)` - return `MemoryEntry`s whose indexed keywords overlap with the query, scoped to the given app and user.

Constructor:

```python
DatabaseMemoryService(
    db_url: str,
    *,
    stop_words: set[str] | None = None,   # override the default English stop-words list
    **engine_kwargs,                       # forwarded to create_async_engine
)
```

Lifecycle:

```python
async with DatabaseMemoryService(db_url) as memory:
    ...
# equivalent to:
memory = DatabaseMemoryService(db_url)
try:
    ...
finally:
    await memory.close()
```

## How it works

- On first write, a single table `adk_memory_entries` is created (lazy, with an async double-checked lock) with an index on `(app_name, user_id)`.
- Each event's text content is lower-cased, tokenized (`[A-Za-z]+`), and filtered against the stop-words set to produce a keyword bag.
- Search extracts keywords from the query the same way and returns rows where the bags overlap, scoped by `app_name` and `user_id`, then de-duplicates on `(author, text, timestamp)`.
- JSON content is stored as `JSONB` on PostgreSQL, `LONGTEXT` on MySQL, and `TEXT` on SQLite/others via a `DynamicJSON` type decorator.

This is intentionally the same keyword-matching approach as the in-memory and Firestore memory services in ADK; it is a durable, zero-infra starting point, not a semantic retriever. If you need embedding-based recall, pair this package with Vertex AI Memory Bank or a vector store.

## Development

```bash
git clone https://github.com/anmolg1997/adk-database-memory
cd adk-database-memory
pip install -e ".[dev]"
pytest
ruff check .
mypy src
```

## License

Apache 2.0 - see [LICENSE](./LICENSE).

## Related

- [google/adk-python](https://github.com/google/adk-python) - core Agent Development Kit.
- [`FirestoreSessionService` (PR #5088)](https://github.com/google/adk-python/pull/5088) - the sibling Firestore session service this memory service's keyword-index approach mirrors.
