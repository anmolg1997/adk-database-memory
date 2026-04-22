"""Smallest end-to-end example: persist a session to SQLite, then search it back.

Run:
    pip install "adk-database-memory[sqlite]"
    python examples/quickstart_sqlite.py
"""

from __future__ import annotations

import asyncio

from google.adk.events.event import Event
from google.adk.sessions.session import Session
from google.genai import types

from adk_database_memory import DatabaseMemoryService

DB_URL = "sqlite+aiosqlite:///quickstart_memory.db"
APP_NAME = "quickstart_app"
USER_ID = "alice"


def make_session() -> Session:
    return Session(
        app_name=APP_NAME,
        user_id=USER_ID,
        id="session-001",
        last_update_time=1.0,
        events=[
            Event(
                id="e1",
                invocation_id="inv-1",
                author="user",
                timestamp=1.0,
                content=types.Content(
                    parts=[types.Part(text="We agreed the launch date is November 15.")]
                ),
            ),
            Event(
                id="e2",
                invocation_id="inv-2",
                author="model",
                timestamp=2.0,
                content=types.Content(
                    parts=[types.Part(text="Confirmed: launch on November 15.")]
                ),
            ),
        ],
    )


async def main() -> None:
    async with DatabaseMemoryService(DB_URL) as memory:
        await memory.add_session_to_memory(make_session())

        result = await memory.search_memory(
            app_name=APP_NAME,
            user_id=USER_ID,
            query="when is the launch date?",
        )

        print(f"Found {len(result.memories)} matching memory entries:")
        for entry in result.memories:
            text = entry.content.parts[0].text if entry.content and entry.content.parts else ""
            print(f"  [{entry.author} @ {entry.timestamp}] {text}")


if __name__ == "__main__":
    asyncio.run(main())
