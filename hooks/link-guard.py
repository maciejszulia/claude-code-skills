#!/usr/bin/env python3
"""Stop hook: an answer that says something was saved must carry a link (owner rule of 2026-11-16).

Reads the Stop event JSON on stdin. If the last assistant message contains a "saved" word
(zapisane, zapisałem, zapisał, zapisano ...) and no link, the hook blocks the stop once and asks
for the link. A link is a path with a line number (`~/notes/rules.md:12`) or a URL.
A "saved" word that only describes ("nie zapisałem", "czy jest zapisane", "zapisana tak, żeby") does not count.

Usage: link-guard.py < event.json
       link-guard.py --selftest
"""
import json
import re
import sys

# A finished save: zapisałem, zapisał, zapisaliśmy, zapisano, the nominative participle (zapisany, zapisana, zapisane)
# and the genitive after a numeral ("15 wiadomości jest zapisanych"). Other cases of the participle only describe.
SAVED = re.compile(r"\bzapisa(?:ł\w*|li\w*|n[aeoy])\b|\b(?:jest|było|zostało)\s+zapisanych\b", re.IGNORECASE)
# The same words when they claim nothing: a negation, a question, the quoted word itself, the manner of writing.
# ponytail: a word list, measured on 10 days of answers; "zapisane w Lean" or "zapisane CV" still ask for a link.
# Parse the sentence (a tagger such as Morfeusz) if the false blocks start to cost more than one extra turn.
DESCRIBES = re.compile(
    r"\bnie\s+(?:\w+\s+){0,2}zapisa"
    r"|\bczy\b[^,;.!?\n]*\bzapisa"
    r"|[„\"`]zapisa\w+[”\"`]"
    r"|\bzapisan\w+\s+(?:tak,?\s+(?:żeby|aby|by)|inaczej|poprawnie|błędnie|źle|w\s+formacie)\b"
    r"|\b(?:poprawnie|błędnie|źle|inaczej)\s+zapisan",
    re.IGNORECASE)
LINK = re.compile(r"https?://\S+|[~/][\w./~-]*\w:\d+")
REASON = ("Reguła ownera 2026-11-16 (~/.claude/CLAUDE.md, sekcja „linki do reguł i do zapisów”): odpowiedź ze słowem "
          "„zapisane” MUSI podać link do miejsca zapisu: `ścieżka:linia` albo adres URL. Dopisz link i zakończ odpowiedź.")


def verdict(event):
    """None lets the answer through; a string is the reason for a block."""
    if event.get("stop_hook_active"):
        return None  # one reminder per stop, never a loop
    text = event.get("last_assistant_message") or ""
    described = [m.span() for m in DESCRIBES.finditer(text)]
    claims = any(not any(a <= m.start() < b for a, b in described) for m in SAVED.finditer(text))
    # ponytail: a link anywhere in the answer passes; pair each "saved" word with its own link if that proves too weak
    return REASON if claims and not LINK.search(text) else None


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
    # the participle as a claim still needs a link
    assert say("Stan jest zapisany w SB.") == REASON
    assert say("15 wiadomości jest zapisanych.") == REASON
    assert say("Tego nie było w pamięci, więc zapisałem regułę.") == REASON  # a negation elsewhere excuses nothing
    # the same words when they only describe
    assert say("Proces to dawna indukcja zapisana tak, żeby inni mogli z niej dedukować.") is None
    assert say("Reguła nie jest jeszcze zapisana w pamięci.") is None
    assert say("Sprawdzam, czy problem jest już zapisany w papercuts.") is None
    assert say("Hook reaguje na słowo „zapisane”.") is None
    assert say("Obszedłem to skryptem zapisanym w pliku.") is None
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
