---
name: drift-check
description: After a long session, or when receiving a branch from OMX/Codex, narrate in plain words each step the change actually performs, in the order it happens, and bold every place where the current diff, branch or merge request has drifted from the owner's most recently stated intent. Use when the owner says "/drift-check", "sprawdź dryf", "co tu właściwie robimy", "opowiedz po kolei", "czy to jeszcze jest to, co chciałem", or before handing a branch to the owner for merge.
---

# Drift check

Source: tip from an Anthropic engineer (Claude Code newsletter, 2026-09-19). The goal is to find where the owner's mental model and the actual change differ, without the owner re-reading the thread.

1. **Find the intent.** Take the owner's most recent statement of what the change must do: the latest owner message about it in this conversation, else the order file (`docs/orders/…`) the branch was built from. Quote it in one line. If the intent is ambiguous or you cannot find it, say so and stop instead of guessing.
2. **Read what actually exists.** The real diff, not your memory of it: `git diff <base>...HEAD` for a branch (base = the branch it will merge into), `git diff` plus `git diff --staged` for uncommitted work. Read the changed code paths end to end.
3. **Narrate.** In Polish, no jargon (IT terms stay in English), one short paragraph or numbered step per stage, **in the order things happen at run time** (request → validation → write → notification…), not in file order. Each step names the file:line it lives in.
4. **Bold the drift inline.** Wrap in `**…**` every sentence where the change does something the intent did not ask for, skips something it asked for, or does it differently (other scope, other default, other data touched). Do not bold matches.
5. **Close with a list** "Dryf" of the bolded items, one line each, with file:line, and for each one the question the owner has to answer (keep / revert / change). If nothing drifted, write "Dryfu nie znalazłem" and what you compared against.

Rules: read-only, no fixes in this pass. Report only what you checked in the diff; mark anything inferred as unverified. The owner will paste your answer back as a quote and reply to the parts that stand out, so keep every step addressable (numbered).
