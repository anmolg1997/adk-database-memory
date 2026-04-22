# Examples

Runnable examples for `adk-database-memory`. Each script is self-contained and uses SQLite by default so you can run it without setting up a database server.

## Setup

```bash
pip install "adk-database-memory[sqlite]"
```

For Postgres or MySQL examples, install the matching extra and adjust the connection URL at the top of the script.

## What's here

| File | Backend | Shows |
|---|---|---|
| `quickstart_sqlite.py` | SQLite | The smallest possible end-to-end usage: write a session into memory and search it back. |
| `with_runner.py` | SQLite | How to plug `DatabaseMemoryService` into an ADK `Runner` so an agent can recall past sessions. |
| `multi_user_search.py` | SQLite | Demonstrates per-user isolation: two users in the same app see only their own memories. |

## Running

```bash
python examples/quickstart_sqlite.py
python examples/with_runner.py
python examples/multi_user_search.py
```

## Switching backends

Every example takes a connection URL. To run any of them against Postgres:

```python
DB_URL = "postgresql+asyncpg://user:pass@localhost:5432/agentdb"
```

Or against MySQL:

```python
DB_URL = "mysql+aiomysql://user:pass@localhost:3306/agentdb"
```

Make sure to install the matching extra (`[postgres]` or `[mysql]`).
