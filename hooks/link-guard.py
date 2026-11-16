#!/usr/bin/env python3
"""Stop hook: an answer that says something was saved must carry a link (owner rule of 2026-11-16).

Reads the Stop event JSON on stdin. If the last assistant message contains a "saved" word
(zapisane, zapisałem, zapisał, zapisano ...) and no link, the hook blocks the stop once and asks
for the link. A link is a path with a line number (`~/notes/rules.md:12`) or a URL.

Usage: link-guard.py < event.json
       link-guard.py --selftest
"""
import json
import re
import sys

SAVED = re.compile(r"\bzapisa(?:n(?!i[ea])\w*|ł\w*|li\w*)\b", re.IGNORECASE)
LINK = re.compile(r"https?://\S+|[~/][\w./~-]*\w:\d+")
REASON = ("Reguła ownera 2026-11-16 (~/.claude/CLAUDE.md, sekcja „linki do reguł i do zapisów”): odpowiedź ze słowem "
          "„zapisane” MUSI podać link do miejsca zapisu: `ścieżka:linia` albo adres URL. Dopisz link i zakończ odpowiedź.")


def verdict(event):
    """None lets the answer through; a string is the reason for a block."""
    if event.get("stop_hook_active"):
        return None  # one reminder per stop, never a loop
    text = event.get("last_assistant_message") or ""
    # ponytail: a link anywhere in the answer passes; pair each "saved" word with its own link if that proves too weak
    return REASON if SAVED.search(text) and not LINK.search(text) else None


def selftest():
    say = lambda text, **more: verdict({"last_assistant_message": text, **more})
    assert say("Regułę zapisałem w pamięci.") == REASON
    assert say("Opus zapisał regułę w repo.") == REASON
    assert say("Zapisane: `~/.claude/CLAUDE.md:126`.") is None
    assert say("Commit: https://example.com/c/abc, zapisane.") is None
    assert say("Partia 1 rusza.") is None
    assert say("Zapisanie pliku trwa 2 s.") is None          # the noun is not a claim about a finished save
    assert say("zapisane", stop_hook_active=True) is None    # the second stop always passes
    assert verdict({}) is None
    print("ok")


def main():
    if "--selftest" in sys.argv:
        return selftest()
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return  # malformed input never blocks a session
    reason = verdict(event)
    if reason:
        print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


if __name__ == "__main__":
    main()
