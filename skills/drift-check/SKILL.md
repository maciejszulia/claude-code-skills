---
name: drift-check
description: After a long session, or when receiving a branch from OMX/Codex, narrate in plain words each step the change actually performs, in the order it happens, and bold every place where the current diff, branch or merge request has drifted from the owner's most recently stated intent. Use when the owner says "/drift-check", "sprawdź dryf", "co tu właściwie robimy", "opowiedz po kolei", "czy to jeszcze jest to, co chciałem", or before handing a branch to the owner for merge. Also every morning, and when the owner says "drift check wszystkich sesji" or "sprawdź otwarte sesje": the open-sessions mode checks every live Claude Code session on the machine.
---

# Drift check

Source: tip from an Anthropic engineer (Claude Code newsletter, 2026-09-19). The goal is to find where the owner's mental model and the actual change differ, without the owner re-reading the thread.

1. **Find the intent.** Take the owner's most recent statement of what the change must do: the latest owner message about it in this conversation, else the order file (`docs/orders/…`) the branch was built from. Quote it in one line. If the intent is ambiguous or you cannot find it, say so and stop instead of guessing.
2. **Read what actually exists.** The real diff, not your memory of it: `git diff <base>...HEAD` for a branch (base = the branch it will merge into), `git diff` plus `git diff --staged` for uncommitted work. Read the changed code paths end to end.
3. **Narrate.** In Polish, no jargon (IT terms stay in English), one short paragraph or numbered step per stage, **in the order things happen at run time** (request → validation → write → notification…), not in file order. Each step names the file:line it lives in.
4. **Bold the drift inline.** Wrap in `**…**` every sentence where the change does something the intent did not ask for, skips something it asked for, or does it differently (other scope, other default, other data touched). Do not bold matches.
5. **Close with a list** "Dryf" of the bolded items, one line each, with file:line, and for each one the question the owner has to answer (keep / revert / change). If nothing drifted, write "Dryfu nie znalazłem" and what you compared against.

Rules: read-only, no fixes in this pass. Report only what you checked in the diff; mark anything inferred as unverified. The owner will paste your answer back as a quote and reply to the parts that stand out, so keep every step addressable (numbered). In a pair the other hemisphere reviews the report before the owner sees it (step 7 of the open-sessions mode).

## Tryb: otwarte sesje

Owner 2026-11-15: „zrób drift check wszystkich moich sesji które mam teraz otwarte”. Tryb sprawdza każdą sesję Claude Code, której proces żyje na tej maszynie. Lider uruchamia tryb każdego ranka (VSM, system S3*). Tryb tylko czyta pliki.

Wykonaj każdy krok w tej kolejności:

1. Wypisz sesje: `python3 scripts/open_sessions.py` oraz narzędzie `ListAgents`. Pole `entrypoint` równe `cli` albo `claude-desktop` oznacza sesję ownera. Pole `entrypoint` równe `sdk-ts` albo `sdk-cli` oznacza sesję uruchomioną przez narzędzie.
2. Dla każdej sesji ownera uruchom `python3 scripts/session_digest.py <transkrypt> <początek dnia ISO>`. Wynik: polecenia ownera, agenci, commity, zapisane pliki, 2 końcowe odpowiedzi.
3. Sprawdź każdą deklarację z digestu w źródle: `git log`, `git status`, work_state, pliki. Cytat z godziną znajdź komendą `python3 scripts/grep_transcript.py <transkrypt> <wzorzec> [od] [do] [data]`.
4. Dla każdej sesji opisz polecenie ownera, numerowane kroki stanu i pogrubiony dryf. Sesję bez dryfu oznacz zdaniem „Dryfu nie znalazłem”.
5. Zamknij raport listą pytań do ownera. Każde pytanie ma 3 elementy: klasę decyzji, rekomendację i termin. Klasa decyzji to A, B albo C.
6. Zapisz raport w SB: `briefings/RRRR-MM-DD-drift-check-open-sessions.md`.
7. Wyślij raport do oceny, zanim pokażesz raport ownerowi: raport lidera ocenia lewa półkula. Jeżeli druga półkula nie działa, to raport podaje zdanie „bez oceny drugiej półkuli” oraz powód.

NIE WOLNO czytać plików `*.key` z rejestru `~/.claude/sessions/`: pliki zawierają sekrety. Sesja w chmurze i sesja Remote Control offline leżą poza trybem, bo ta maszyna nie ma transkryptów tych sesji.
