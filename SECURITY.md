# Security Policy

## Supported versions

Only the latest minor release on PyPI receives security fixes. For now that means the `0.1.x` line.

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |
| older   | No        |

## Reporting a vulnerability

Please do not file public GitHub issues for security problems. Use GitHub's private vulnerability reporting flow:

https://github.com/anmolg1997/adk-database-memory/security/advisories/new

Include a short description, the affected version, and steps to reproduce if you have them. A minimal code snippet is more useful than a long write-up.

## What to expect

I'm the sole maintainer. Response times are best-effort, but I aim to:

- Acknowledge the report within 3 business days.
- Share a first assessment (accepted, needs more info, out of scope) within 7 business days.
- Ship a patch release and disclose within 30 days of a confirmed issue.

If you don't hear back in a week, feel free to ping the advisory.

## Scope

In scope:

- The `adk_database_memory` package source under `src/`.
- The published sdist and wheels on PyPI.

Out of scope:

- Third-party drivers (`asyncpg`, `aiomysql`, `aiosqlite`, SQLAlchemy itself). Report to them directly.
- Misconfiguration of your own database (credentials, network exposure, TLS).
