#!/usr/bin/env python3
"""lead-takeover (SessionStart): remind a new lead session of a pending lead handoff (skill lead-handoff).

Owner rule of 2026-11-15: after a usage limit, Fable 5.2 (effort max) takes over the lead, runs drift-check first
and commands the other models. Subagent sessions (/subagents/ in transcript_path) are skipped.
Never blocks: every error is silent and the exit code is 0. `--selftest` runs the self-check.
"""
import json
import os
import sys

PENDING = os.environ.get("LEAD_HANDOFF_PENDING", os.path.expanduser("~/.local/state/lead-handoff/pending"))
MSG = ("LEAD-HANDOFF: czeka handoff lidera {path}. Jeżeli twój model zgadza się z polem „Dla” w handoffie, "
       "uruchom skill lead-handoff w trybie PRZEJMIJ: najpierw przeczytaj handoff, potem drift-check, potem rozdziel kolejkę. "
       "Jeżeli twój model się nie zgadza, kontynuuj zwykłą pracę.")


def message(hook, pending_path):
    if "/subagents/" in str(hook.get("transcript_path", "")):
        return None
    try:
        with open(pending_path, encoding="utf-8") as fh:
            target = fh.read().strip()
    except OSError:
        return None
    return MSG.format(path=target) if target else None


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "pending")
        assert message({}, p) is None                                  # nothing pending
        open(p, "w").write("/x/handoffs/2026-11-15-1700-lead.md\n")
        assert "PRZEJMIJ" in message({"transcript_path": "/s/main.jsonl"}, p)
        assert message({"transcript_path": "/s/subagents/a.jsonl"}, p) is None
    return "ok"


def main():
    if "--selftest" in sys.argv:
        print(selftest())
        return
    try:
        msg = message(json.load(sys.stdin), PENDING)
        if msg:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": msg}}, ensure_ascii=False))
    except Exception:
        pass


if __name__ == "__main__":
    main()
