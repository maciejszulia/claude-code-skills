#!/usr/bin/env python3
"""limit-guard: owner rule of 2026-11-15 ("zrób hooka który pyta czy ustawić prace dalej gdy limit jest pod 90%
czy przekazać pracę gdzieś indziej. i od razu po limicie jest drift-check").

UserPromptSubmit and PostToolUse, lead session only (subagent transcripts live under /subagents/):
1. When the 5-hour or the 7-day window of ~/.claude/rate_limits.json reaches 90 %, inject once per window an
   instruction to ask the owner whether to keep working here or hand the work elsewhere.
2. When that window has reset, inject once an instruction to run the drift-check skill before any further work.
3. When a window newly reaches 90 %, push an alarm to the owner's phone with ntfy-push (algedonic channel of the
   Viable System Model, owner rule of 2026-11-15). No ntfy-push on the machine means no alarm.
Never blocks: every error is silent and the exit code is 0. `--selftest` runs the self-check.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

LIMITS = os.environ.get("LIMIT_GUARD_LIMITS", os.path.expanduser("~/.claude/rate_limits.json"))
STATE = os.environ.get("LIMIT_GUARD_STATE", os.path.expanduser("~/.claude/state/limit-guard.json"))
ROTATION = os.environ.get("LIMIT_GUARD_ROTATION",
                          os.path.expanduser("~/.local/share/silverbullet/space/projects/brain-systems.md"))
THRESHOLD = 90
NAMES = {"five_hour": "5 h", "seven_day": "7 d"}

ASK = ("LIMIT-GUARD: limit {name} wynosi {pct} % (próg {thr} %, reset {reset}). Zanim wykonasz kolejny krok, zapytaj ownera "
       "narzędziem AskUserQuestion, co dalej. Opcje: 1) kontynuuj tutaj aż do limitu; 2) wstrzymaj pracę do resetu o {reset}; "
       "3) przekaż pracę Hermesowi (darmowe modele) z handoffem w SB; 4) zaplanuj rutynę w chmurze na czas po resecie; "
       "5) przekaż lead Fable 5.2 (effort max): skill lead-handoff, tryb WYDAJ. "
       "Nie proponuj Codeksa ani OMX (reguła ownera z 2026-10-06). Po resecie hook każe uruchomić drift-check. "
       "Lider wysyła wynik do oceny drugiej półkuli przed pokazaniem ownerowi. Jeżeli druga półkula nie działa, to raport "
       "podaje zdanie „bez oceny drugiej półkuli” oraz powód.")
DRIFT = ("LIMIT-GUARD: limit {name} odnowił się o {reset}. Zanim podejmiesz dalszą pracę, uruchom skill drift-check "
         "(/drift-check) dla bieżącej pracy, pokaż wynik ownerowi i dopiero potem kontynuuj.")


def hhmm(epoch):
    return time.strftime("%H:%M", time.localtime(epoch)) if epoch else "?"


def decide(limits, state, now, todo=lambda: ""):
    """Returns (messages, new_state). state: {"asked": {window: resets_at}, "drift": {window: resets_at}}.
    todo() gives the rotation line added to the drift-check message; it runs only when that message is due."""
    asked, drift = dict(state.get("asked", {})), dict(state.get("drift", {}))
    out = []
    for key, name in NAMES.items():
        w = limits.get(key) or {}
        pct, reset = w.get("used_percentage"), w.get("resets_at")
        pending = drift.get(key)
        if pending and (now >= pending or (reset and reset != pending)):
            line = todo()
            out.append(DRIFT.format(name=name, reset=hhmm(pending)) + (" " + line if line else ""))
            drift.pop(key)
            asked.pop(key, None)
        if pct is not None and reset and pct >= THRESHOLD and asked.get(key) != reset:
            out.append(ASK.format(name=name, pct=round(pct), thr=THRESHOLD, reset=hhmm(reset)))
            asked[key] = reset
            drift[key] = reset
    return out, {"asked": asked, "drift": drift}


def rotation_todo(path=ROTATION):
    """First row with the state "todo" in the table under "## Rotacja co okno limitu", as 1 line; "" when the page,
    the section or such a row is missing. Columns: order, system, task, completion criterion, state, result."""
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return ""
    parts = text.split("## Rotacja co okno limitu", 1)
    for row in (parts[1].split("\n## ", 1)[0].splitlines() if len(parts) == 2 else []):
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if row.lstrip().startswith("|") and len(cells) >= 5 and cells[4] == "todo":
            return f"Rotacja: pozycja {cells[0]}, system {cells[1]}. Zadanie okna: {cells[2]} Kryterium: {cells[3]}"
    return ""


def newly_asked(old, new):
    """Windows whose 90 % question was raised by this call (their reset time in "asked" changed)."""
    before = old.get("asked", {})
    return [k for k, v in new.get("asked", {}).items() if before.get(k) != v]


def alarm(body):
    """Push one alarm with ntfy-push (default topic of the owner's ntfy rule). Silent when ntfy-push is missing."""
    # ponytail: only the limit signal is automatic. Secret in a public repo, deadline in < 24 h and an employer reply
    # rely on the agent calling ntfy-push; upgrade path: a hook on `gh repo create/edit` and a check in the inbox script.
    cmd = shutil.which("ntfy-push") or os.path.expanduser("~/.local/bin/ntfy-push")
    if os.access(cmd, os.X_OK):
        subprocess.run([cmd, "ALARM: limit Claude", body], capture_output=True, timeout=15)


def selftest():
    t0 = 1_800_000_000
    lim = {"five_hour": {"used_percentage": 95, "resets_at": t0 + 600}, "seven_day": {"used_percentage": 60, "resets_at": t0 + 9999}}
    msgs, st = decide(lim, {}, t0)
    assert len(msgs) == 1 and "5 h" in msgs[0] and "AskUserQuestion" in msgs[0], msgs
    assert "druga półkula" in msgs[0] and "bez oceny drugiej półkuli" in msgs[0], msgs  # owner 2026-11-15, 22:43
    msgs, st = decide(lim, st, t0 + 60)
    assert msgs == [], msgs                                   # asked once per window
    after = {"five_hour": {"used_percentage": 3, "resets_at": t0 + 600 + 18000}, "seven_day": lim["seven_day"]}
    msgs, st = decide(after, st, t0 + 700)
    assert len(msgs) == 1 and "drift-check" in msgs[0], msgs  # drift-check right after the reset
    msgs, st = decide(after, st, t0 + 800)
    assert msgs == [] and st == {"asked": {}, "drift": {}}, (msgs, st)
    _, s2 = decide(lim, {}, t0)
    msgs, _ = decide(after, s2, t0 + 700, todo=lambda: "Rotacja: pozycja 3.")
    assert len(msgs) == 1 and msgs[0].endswith(" Rotacja: pozycja 3."), msgs    # the window's rotation task follows
    with tempfile.TemporaryDirectory() as tmp:
        page = os.path.join(tmp, "brain-systems.md")
        assert rotation_todo(page) == ""                                            # no page: no line
        with open(page, "w", encoding="utf-8") as fh:
            fh.write("## Mapa\n\n| 1 | x | y | z | todo | w |\n\n## Rotacja co okno limitu\n\n"
                     "| Kolejność | System | Zadanie okna | Kryterium ukończenia | Stan | Wynik |\n|---|---|---|---|---|---|\n"
                     "| 1 | sen (6) | A. | B. | done | C. |\n| 3 | ciało migdałowate (11) | Skan. | Raport. | todo | brak. |\n"
                     "\n## Niesprawdzone\n\n| 9 | a | b | c | todo | d |\n")
        assert rotation_todo(page) == ("Rotacja: pozycja 3, system ciało migdałowate (11). Zadanie okna: Skan. "
                                       "Kryterium: Raport."), rotation_todo(page)
        with open(page, "w", encoding="utf-8") as fh:
            fh.write("## Rotacja co okno limitu\n\n| 1 | sen (6) | A. | B. | done | C. |\n")
        assert rotation_todo(page) == ""                                            # no todo row: no line
    assert newly_asked({}, {"asked": {"five_hour": 5}}) == ["five_hour"]
    assert newly_asked({"asked": {"five_hour": 5}}, {"asked": {"five_hour": 5}}) == []    # no repeat alarm
    with tempfile.TemporaryDirectory() as tmp:                                           # fake ntfy-push, no real push
        fake, log = os.path.join(tmp, "ntfy-push"), os.path.join(tmp, "argv")
        with open(fake, "w") as fh:
            fh.write(f'#!/bin/sh\nprintf "%s|" "$@" > "{log}"\n')
        os.chmod(fake, 0o755)
        path = os.environ.get("PATH", "")
        os.environ["PATH"] = tmp + os.pathsep + path
        try:
            alarm("5 h: 95 %, reset 10:00")
        finally:
            os.environ["PATH"] = path
        assert open(log).read() == "ALARM: limit Claude|5 h: 95 %, reset 10:00|", open(log).read()
    return "ok"


def main():
    if "--selftest" in sys.argv:
        print(selftest())
        return
    try:
        hook = json.load(sys.stdin)
        if "/subagents/" in str(hook.get("transcript_path", "")):
            return
        with open(LIMITS, encoding="utf-8") as fh:
            limits = json.load(fh)
        try:
            with open(STATE, encoding="utf-8") as fh:
                state = json.load(fh)
        except (OSError, ValueError):
            state = {}
        msgs, new_state = decide(limits, state, time.time(), rotation_todo)
        if new_state != state:
            os.makedirs(os.path.dirname(STATE), exist_ok=True)
            with open(STATE, "w", encoding="utf-8") as fh:
                json.dump(new_state, fh)
        if msgs:
            event = hook.get("hook_event_name") or "PostToolUse"
            print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": "\n".join(msgs)}}, ensure_ascii=False))
            sys.stdout.flush()
        for key in newly_asked(state, new_state):
            w = limits.get(key) or {}
            alarm(f"Limit {NAMES[key]}: {round(w.get('used_percentage', 0))} %, reset {hhmm(w.get('resets_at'))}. "
                  "Sesja lidera pyta, co dalej.")
    except Exception:
        pass


if __name__ == "__main__":
    main()
