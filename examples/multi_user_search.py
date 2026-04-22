"""Per-user isolation: two users in the same app see only their own memories.

Run:
    pip install "adk-database-memory[sqlite]"
    python examples/multi_user_search.py
"""

from __future__ import annotations

import asyncio

from google.adk.events.event import Event
from google.adk.sessions.session import Session
from google.genai import types

from adk_database_memory import DatabaseMemoryService

DB_URL = "sqlite+aiosqlite:///multi_user_memory.db"
APP_NAME = "shared_app"


def session_for(user_id: str, sid: str, text: str, ts: float) -> Session:
    return Session(
        app_name=APP_NAME,
        user_id=user_id,
        id=sid,
        last_update_time=ts,
        events=[
            Event(
                id=f"{sid}-evt",
                invocation_id=f"inv-{sid}",
                author="user",
                timestamp=ts,
                content=types.Content(parts=[types.Part(text=text)]),
            )
        ],
    )


async def main() -> None:
    async with DatabaseMemoryService(DB_URL) as memory:
        await memory.add_session_to_memory(
            session_for("alice", "a1", "Alice prefers dark roast coffee.", 10.0)
        )
        await memory.add_session_to_memory(
            session_for("bob", "b1", "Bob also drinks coffee, but only decaf.", 20.0)
        )

        for user in ("alice", "bob"):
            result = await memory.search_memory(
                app_name=APP_NAME, user_id=user, query="coffee preferences"
            )
            print(f"\nMemories visible to {user}:")
            for entry in result.memories:
                text = (
                    entry.content.parts[0].text
                    if entry.content and entry.content.parts
                    else ""
                )
                print(f"  - {text}")

        print("\nNote: each user only sees their own session, even though both")
        print("are stored in the same database under the same app_name.")


if __name__ == "__main__":
    asyncio.run(main())
