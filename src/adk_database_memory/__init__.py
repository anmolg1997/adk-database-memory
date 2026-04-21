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

"""SQL-backed memory service for the Google Agent Development Kit (ADK).

See :class:`DatabaseMemoryService` for usage.
"""

from .service import DEFAULT_STOP_WORDS, DatabaseMemoryService

__all__ = ["DatabaseMemoryService", "DEFAULT_STOP_WORDS"]

__version__ = "0.1.0"
