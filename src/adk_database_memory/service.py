# Copyright 2026 Anmol Jaiswal
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A durable memory service backed by any SQLAlchemy-compatible async database.

Supported dialects include SQLite (via ``aiosqlite``), PostgreSQL (via
``asyncpg``), MySQL / MariaDB, and any other database for which an async
SQLAlchemy driver is available.
"""

from __future__ import annotations

import asyncio
import logging
import re
from collections.abc import AsyncIterator, Mapping, Sequence
from contextlib import asynccontextmanager
from datetime import datetime
from typing import TYPE_CHECKING, Any

from google.adk.memory.base_memory_service import BaseMemoryService, SearchMemoryResponse
from google.adk.memory.memory_entry import MemoryEntry
from sqlalchemy import select
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.asyncio import AsyncSession as DatabaseSessionFactory
from sqlalchemy.pool import StaticPool
from typing_extensions import override

from ._schemas import Base, StorageMemoryEntry

if TYPE_CHECKING:
    from google.adk.events.event import Event
    from google.adk.sessions.session import Session

logger = logging.getLogger(__name__)

_SQLITE_DIALECT = "sqlite"

DEFAULT_STOP_WORDS: frozenset[str] = frozenset(
    {
        "a", "about", "above", "after", "again", "against", "all", "am", "an",
        "and", "any", "are", "as", "at", "be", "because", "been", "before",
        "being", "below", "between", "both", "but", "by", "can", "could",
        "did", "do", "does", "doing", "don", "down", "during", "each", "else",
        "few", "for", "from", "further", "had", "has", "have", "having", "he",
        "her", "here", "hers", "herself", "him", "himself", "his", "how", "i",
        "if", "in", "into", "is", "it", "its", "itself", "just", "may", "me",
        "might", "more", "most", "must", "my", "myself", "no", "nor", "not",
        "now", "of", "off", "on", "once", "only", "or", "other", "our", "ours",
        "ourselves", "out", "over", "own", "s", "same", "shall", "she",
        "should", "so", "some", "such", "t", "than", "that", "the", "their",
        "theirs", "them", "themselves", "then", "there", "these", "they",
        "this", "those", "through", "to", "too", "under", "until", "up",
        "very", "was", "we", "were", "what", "when", "where", "which", "who",
        "whom", "why", "will", "with", "would", "you", "your", "yours",
        "yourself", "yourselves",
    }
)


def _format_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).isoformat()


class DatabaseMemoryService(BaseMemoryService):  # type: ignore[misc]
    """Memory service backed by any SQLAlchemy-compatible async database.

    Uses keyword extraction to index session events, and keyword overlap to
    search for relevant memories.

    Example::

        from adk_database_memory import DatabaseMemoryService

        # SQLite (zero-config)
        memory = DatabaseMemoryService("sqlite+aiosqlite:///memory.db")

        # PostgreSQL
        memory = DatabaseMemoryService(
            "postgresql+asyncpg://user:pass@host/dbname"
        )

        async with memory:
            await memory.add_session_to_memory(session)
            result = await memory.search_memory(
                app_name="my_app", user_id="u1", query="agent tool usage"
            )
    """

    def __init__(
        self,
        db_url: str,
        *,
        stop_words: set[str] | None = None,
        **engine_kwargs: Any,
    ) -> None:
        """Initializes the database memory service.

        Args:
          db_url: A SQLAlchemy-compatible async database URL. For example:
            ``sqlite+aiosqlite:///memory.db``,
            ``postgresql+asyncpg://user:pass@host/db``,
            ``mysql+aiomysql://user:pass@host/db``.
          stop_words: Words to ignore when extracting keywords. Defaults to a
            standard English stop-words list.
          **engine_kwargs: Additional keyword arguments forwarded to
            ``sqlalchemy.ext.asyncio.create_async_engine``.
        """
        try:
            url = make_url(db_url)
            if url.get_backend_name() == _SQLITE_DIALECT and url.database == ":memory:":
                engine_kwargs.setdefault("poolclass", StaticPool)
                connect_args = dict(engine_kwargs.get("connect_args", {}))
                connect_args.setdefault("check_same_thread", False)
                engine_kwargs["connect_args"] = connect_args
            elif url.get_backend_name() != _SQLITE_DIALECT:
                engine_kwargs.setdefault("pool_pre_ping", True)

            self._engine: AsyncEngine = create_async_engine(db_url, **engine_kwargs)
        except Exception as e:
            if isinstance(e, ArgumentError):
                raise ValueError(
                    f"Invalid database URL format or argument '{db_url}'."
                ) from e
            if isinstance(e, ImportError):
                raise ValueError(
                    f"Database related module not found for URL '{db_url}'. "
                    f"Install the matching async driver (e.g. aiosqlite, asyncpg, aiomysql)."
                ) from e
            raise ValueError(
                f"Failed to create database engine for URL '{db_url}'."
            ) from e

        self._session_factory: async_sessionmaker[DatabaseSessionFactory] = (
            async_sessionmaker(bind=self._engine, expire_on_commit=False)
        )

        self._tables_created = False
        self._table_creation_lock = asyncio.Lock()

        self.stop_words: set[str] = (
            set(stop_words) if stop_words is not None else set(DEFAULT_STOP_WORDS)
        )

    # -- lifecycle helpers ----------------------------------------------------

    @asynccontextmanager
    async def _db_session(self) -> AsyncIterator[DatabaseSessionFactory]:
        """Yields a DB session with guaranteed rollback on errors."""
        async with self._session_factory() as sql_session:
            try:
                yield sql_session
            except BaseException:
                await sql_session.rollback()
                raise

    async def _prepare_tables(self) -> None:
        """Lazily create the memory table (double-checked locking)."""
        if self._tables_created:
            return
        async with self._table_creation_lock:
            if self._tables_created:
                return
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            self._tables_created = True

    async def close(self) -> None:
        """Disposes the SQLAlchemy engine and closes pooled connections."""
        await self._engine.dispose()

    async def __aenter__(self) -> DatabaseMemoryService:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        await self.close()

    # -- keyword helpers ------------------------------------------------------

    def _extract_keywords(self, text: str) -> set[str]:
        """Extract keywords from *text*, ignoring stop words."""
        words = re.findall(r"[A-Za-z]+", text.lower())
        return {word for word in words if word not in self.stop_words}

    def _build_entry(
        self,
        *,
        app_name: str,
        user_id: str,
        event: Event,
    ) -> StorageMemoryEntry | None:
        """Build a row from an event, or None if it has no indexable content."""
        if not event.content or not event.content.parts:
            return None

        text = " ".join(part.text for part in event.content.parts if part.text)
        if not text:
            return None

        keywords = self._extract_keywords(text)
        if not keywords:
            return None

        return StorageMemoryEntry(
            app_name=app_name,
            user_id=user_id,
            keywords=" ".join(sorted(keywords)),
            author=event.author,
            content=event.content.model_dump(exclude_none=True, mode="json"),
            timestamp=event.timestamp,
        )

    # -- BaseMemoryService implementation -------------------------------------

    @override
    async def add_session_to_memory(self, session: Session) -> None:
        """Extract keywords from session events and persist them."""
        await self._prepare_tables()
        entries = [
            entry
            for event in session.events
            if (
                entry := self._build_entry(
                    app_name=session.app_name,
                    user_id=session.user_id,
                    event=event,
                )
            )
            is not None
        ]
        if not entries:
            return

        async with self._db_session() as sql_session:
            sql_session.add_all(entries)
            await sql_session.commit()

    @override
    async def add_events_to_memory(
        self,
        *,
        app_name: str,
        user_id: str,
        events: Sequence[Event],
        session_id: str | None = None,
        custom_metadata: Mapping[str, object] | None = None,
    ) -> None:
        """Add an explicit list of events as memory entries (delta ingestion)."""
        del session_id, custom_metadata  # Not used by the keyword index.
        await self._prepare_tables()
        entries = [
            entry
            for event in events
            if (
                entry := self._build_entry(
                    app_name=app_name,
                    user_id=user_id,
                    event=event,
                )
            )
            is not None
        ]
        if not entries:
            return

        async with self._db_session() as sql_session:
            sql_session.add_all(entries)
            await sql_session.commit()

    @override
    async def search_memory(
        self,
        *,
        app_name: str,
        user_id: str,
        query: str,
    ) -> SearchMemoryResponse:
        """Search memory for entries whose keywords overlap with *query*."""
        keywords = self._extract_keywords(query)
        if not keywords:
            return SearchMemoryResponse()

        await self._prepare_tables()
        async with self._db_session() as sql_session:
            stmt = (
                select(StorageMemoryEntry)
                .filter(StorageMemoryEntry.app_name == app_name)
                .filter(StorageMemoryEntry.user_id == user_id)
            )
            result = await sql_session.execute(stmt)
            all_rows = result.scalars().all()

        seen: set[tuple[str | None, str, str]] = set()
        memories: list[MemoryEntry] = []

        for row in all_rows:
            stored_keywords = set(row.keywords.split())
            if not stored_keywords.intersection(keywords):
                continue

            try:
                from google.genai import types  # Imported lazily to avoid cost at import time.

                content = types.Content.model_validate(row.content)
            except Exception as e:
                logger.warning("Failed to parse memory entry: %s", e)
                continue

            content_text = ""
            if content.parts:
                content_text = " ".join(
                    part.text for part in content.parts if part.text
                )

            timestamp_str = _format_timestamp(row.timestamp or 0.0)
            dedup_key = (row.author, content_text, timestamp_str)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            memories.append(
                MemoryEntry(
                    content=content,
                    author=row.author or "",
                    timestamp=timestamp_str,
                )
            )

        return SearchMemoryResponse(memories=memories)
