---
name: sb-mem
description: Search and extend the shared session memory kept in SilverBullet (dziennik/, sessions.md, handoffs/, papercuts.md, decisions/, runbooks/) — the SilverBullet replacement for claude-mem's mem-search. Use when the owner asks "czy już to robiliśmy", "jak to zrobiliśmy ostatnio", "co było w poprzedniej sesji", "/sb-mem", or when a milestone should be written to the second brain right away (owner rule 29.08).
---

# sb-mem — session memory in SilverBullet

Space on disk: `~/.local/share/silverbullet/space` (`$S` below). Hooks write there for you
(`~/.claude/hooks/dziennik.py`, `sb-recall.py`, `sb-summarize.py`); this skill is the read side and the manual note.
Everything is plain Markdown: `rg` and `sed` are the whole search engine. Never read a whole directory when one page answers.

## `search <query> [--since YYYY-MM-DD]`

1. `rg -n -i --no-heading -m 5 "<query>" dziennik handoffs papercuts.md decisions runbooks sessions.md` with `cwd=$S`.
   Dates live in file names (`dziennik/2026-09-20.md`, `handoffs/2026-09-16-*.md`): for `--since`, keep only paths whose
   date is not older. Sort hits by path descending so the newest come first.
2. Show the owner at most 10 hits as `path:line — text (≤ 160 chars)`. Journal lines read
   `HH:MM:SS | lead <sid8> | prompt: … / odpowiedź: … / podsumowanie: … / zapis: … / commit: … / zlecenie → …`.
3. Only then open the page or the surrounding lines (`timeline`) for the hits that matter. Answer in Polish with the
   page path as the source; say plainly when nothing was found.

## `timeline <YYYY-MM-DD> [sid8]`

`sed -n '/| lead <sid8> |/p' $S/dziennik/<date>.md` (or the whole page without `sid8`). Present it as the story of that
session: first `prompt:`, the `zlecenie →`/`skill`/`zapis:`/`commit:` lines in between, the last `odpowiedź:` or
`podsumowanie:`. Cross-check the START/END lines in `$S/sessions.md` for model and duration when asked.

## `save <note>`

Milestone, decision or lesson the hooks cannot see. Append one line to today's journal via the writer the hooks use, so
the format and the secret/PII filter stay identical:

```
python3 - <<'EOF'
import sys; sys.path.insert(0, "/home/ms/.claude/hooks"); import dziennik
dziennik.append("notatka: <note>", "lead", "<sid8 of this session>")
EOF
```

Rules: no secrets, no guest personal data, Polish for the owner, IT terms in English, no emoji. A durable rule or
decision also belongs on its canonical page (`decisions/`, `papercuts.md`, `zatwierdzenia.md`) — link it, do not duplicate.

## Not here

Per-agent habits stay in Claude's private memory (`~/.claude/projects/-home-ms/memory/`); claude-mem's own database
(`mem-search` skill) still exists in parallel and holds history from before 2026-09-20.
