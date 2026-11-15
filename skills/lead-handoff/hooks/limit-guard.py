#!/usr/bin/env python3
"""limit-guard: owner rule of 2026-11-15 ("zrób hooka który pyta czy ustawić prace dalej gdy limit jest pod 90%
czy przekazać pracę gdzieś indziej. i od razu po limicie jest drift-check").

UserPromptSubmit and PostToolUse, lead session only (subagent transcripts live under /subagents/):
1. When the 5-hour or the 7-day window of ~/.claude/rate_limits.json reaches 90 %, inject once per window an
   instruction to ask the owner whether to keep working here or hand the work elsewhere.
2. When that window has reset, inject once an instruction to run the drift-check skill before any further work.
Never blocks: every error is silent and the exit code is 0. `--selftest` runs the self-check.
"""
import json
import os
import sys
import time

LIMITS = os.environ.get("LIMIT_GUARD_LIMITS", os.path.expanduser("~/.claude/rate_limits.json"))
STATE = os.environ.get("LIMIT_GUARD_STATE", os.path.expanduser("~/.claude/state/limit-guard.json"))
THRESHOLD = 90
NAMES = {"five_hour": "5 h", "seven_day": "7 d"}

ASK = ("LIMIT-GUARD: limit {name} wynosi {pct} % (próg {thr} %, reset {reset}). Zanim wykonasz kolejny krok, zapytaj ownera "
       "narzędziem AskUserQuestion, co dalej. Opcje: 1) kontynuuj tutaj aż do limitu; 2) wstrzymaj pracę do resetu o {reset}; "
       "3) przekaż pracę Hermesowi (darmowe modele) z handoffem w SB; 4) zaplanuj rutynę w chmurze na czas po resecie; "
       "5) przekaż lead Fable 5.2 (effort max): skill lead-handoff, tryb WYDAJ. "
       "Nie proponuj Codeksa ani OMX (reguła ownera z 2026-10-06). Po resecie hook każe uruchomić drift-check.")
DRIFT = ("LIMIT-GUARD: limit {name} odnowił się o {reset}. Zanim podejmiesz dalszą pracę, uruchom skill drift-check "
         "(/drift-check) dla bieżącej pracy, pokaż wynik ownerowi i dopiero potem kontynuuj.")


def hhmm(epoch):
    return time.strftime("%H:%M", time.localtime(epoch)) if epoch else "?"


def decide(limits, state, now):
    """Returns (messages, new_state). state: {"asked": {window: resets_at}, "drift": {window: resets_at}}."""
    asked, drift = dict(state.get("asked", {})), dict(state.get("drift", {}))
    out = []
    for key, name in NAMES.items():
        w = limits.get(key) or {}
        pct, reset = w.get("used_percentage"), w.get("resets_at")
        pending = drift.get(key)
        if pending and (now >= pending or (reset and reset != pending)):
            out.append(DRIFT.format(name=name, reset=hhmm(pending)))
            drift.pop(key)
            asked.pop(key, None)
        if pct is not None and reset and pct >= THRESHOLD and asked.get(key) != reset:
            out.append(ASK.format(name=name, pct=round(pct), thr=THRESHOLD, reset=hhmm(reset)))
            asked[key] = reset
            drift[key] = reset
    return out, {"asked": asked, "drift": drift}


def selftest():
    t0 = 1_800_000_000
    lim = {"five_hour": {"used_percentage": 95, "resets_at": t0 + 600}, "seven_day": {"used_percentage": 60, "resets_at": t0 + 9999}}
    msgs, st = decide(lim, {}, t0)
    assert len(msgs) == 1 and "5 h" in msgs[0] and "AskUserQuestion" in msgs[0], msgs
    msgs, st = decide(lim, st, t0 + 60)
    assert msgs == [], msgs                                   # asked once per window
    after = {"five_hour": {"used_percentage": 3, "resets_at": t0 + 600 + 18000}, "seven_day": lim["seven_day"]}
    msgs, st = decide(after, st, t0 + 700)
    assert len(msgs) == 1 and "drift-check" in msgs[0], msgs  # drift-check right after the reset
    msgs, st = decide(after, st, t0 + 800)
    assert msgs == [] and st == {"asked": {}, "drift": {}}, (msgs, st)
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
        msgs, new_state = decide(limits, state, time.time())
        if new_state != state:
            os.makedirs(os.path.dirname(STATE), exist_ok=True)
            with open(STATE, "w", encoding="utf-8") as fh:
                json.dump(new_state, fh)
        if msgs:
            event = hook.get("hook_event_name") or "PostToolUse"
            print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": "\n".join(msgs)}}, ensure_ascii=False))
    except Exception:
        pass


if __name__ == "__main__":
    main()
