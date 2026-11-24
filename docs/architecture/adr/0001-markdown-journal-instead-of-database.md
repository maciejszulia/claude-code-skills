# ADR 0001: Markdown journal instead of a database

## Status

Accepted (commit `94b9363`).

## Context

Each Claude Code session starts without memory of earlier sessions. A memory store has to be readable by the owner, searchable from the shell and cheap to keep.

## Decision

The `sb-mem` hooks write one line per session event to a daily Markdown page in a SilverBullet space (`dziennik/YYYY-MM-DD.md`), in the form `- HH:MM:SS | lead <session> | <kind>: <text>`. The read side is `sb-recall.py` (cards of the last 3 days at session start, up to 5 lines about a file before `Read`) and the skill's `search`, `timeline` and `save` with `rg` and `sed`. A one-line summary per session comes from a detached Haiku call at session end. The space path comes from `SB_MEM_SPACE`; any Markdown folder works.

## Consequences

- The owner reads and edits the memory as ordinary pages; git can version the space.
- Search is a text search; there is no ranking and no semantic index.
- A secret in a prompt could reach the page; `dziennik.py` cuts known secret patterns, e-mail addresses and phone numbers before writing.

## Evidence

- `skills/sb-mem/hooks/dziennik.py` (`SPACE`, `OUT`, `SECRET`, `PII`), `skills/sb-mem/hooks/sb-recall.py` (`LINE`, `DAYS, CARDS, HITS = 3, 8, 5`).
- `README.md`, section "sb-mem": "Session memory without a database."
- Commit `94b9363` "Add sb-mem with its hooks; describe every skill and add diagrams".
