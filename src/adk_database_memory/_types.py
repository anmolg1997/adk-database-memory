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

"""SQLAlchemy type decorators used by adk-database-memory.

These are inlined here to avoid depending on private modules inside
``google.adk``.
"""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import Dialect, Text
from sqlalchemy.dialects import mysql, postgresql
from sqlalchemy.types import TypeDecorator


class DynamicJSON(TypeDecorator):
    """JSON column that uses JSONB on Postgres, LONGTEXT on MySQL, TEXT elsewhere."""

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.JSONB())
        if dialect.name == "mysql":
            return dialect.type_descriptor(mysql.LONGTEXT())
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value: Any, dialect: Dialect) -> Any:
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        return json.dumps(value)

    def process_result_value(self, value: Any, dialect: Dialect) -> Any:
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        return json.loads(value)
