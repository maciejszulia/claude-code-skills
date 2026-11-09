---
name: reload
description: Re-read the working rules mid-session when quality drifts — global CLAUDE.md, the project's CLAUDE.md/AGENTS.md, the MEMORY.md index and the current order or plan file — then restate the rules that govern the current task before continuing. Use when the owner says "/reload", "przeładuj reguły", "reload rules", or after a /compact in a long session.
---

# Reload rules

Long contexts dilute instructions that sit far from the end. This skill puts them back in front of you.

1. Read, in this order: `~/.claude/CLAUDE.md`; the project's `CLAUDE.md` and `AGENTS.md` if the cwd has them; `~/.claude/projects/-home-ms/memory/MEMORY.md`; the current order, brief or plan file if one is named in the conversation.
2. Write at most five lines titled "Reguły, których pilnuję teraz" — only the rules that bear on the task at hand, each in one sentence, in Polish. No summary of the files.
3. Continue the task from where it stopped. Do not restart work already verified.
