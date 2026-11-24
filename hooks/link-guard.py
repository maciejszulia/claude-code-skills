#!/usr/bin/env python3
"""Stop hook: an answer that says something was saved must carry a link (owner rule of 2026-11-16).

Reads the Stop event JSON on stdin. If the last assistant message contains a "saved" word
(zapisane, zapisałem, zapisano, dopisałem ...) and no link, the hook blocks the stop once and asks
for the link. A link is a path with a line number (`~/notes/rules.md:12`) or a URL.
A "saved" word that only describes ("nie zapisałem", "czy jest zapisane", "zapisana tak, żeby") does not count.

Usage: link-guard.py < event.json
       link-guard.py --selftest
"""
import json
import re
import sys

# A finished save: zapisałem, zapisał, zapisaliśmy, zapisano, the nominative participle (zapisany, zapisana, zapisane)
# and the genitive next to a numeral ("15 wiadomości jest zapisanych", "zapisanych zostało 15"). Other cases describe.
# The saving verbs. "Wpisać" stays out: on 10 days of answers it added 6 right blocks and 13 wrong ones,
# because "wpisałem" mostly means typing into a form.
VERB = r"(?:za|do)pisa"
SAVED = re.compile(rf"\b{VERB}(?:ł\w*|li\w*|n[aeoy])\b"
                   rf"|\b(?:jest|było|zostało)\s+{VERB}nych\b|\b{VERB}nych\s+(?:jest|było|zostało)\b", re.IGNORECASE)
# The same words when they claim nothing: a negation, a question, the quoted word itself, the manner of writing.
# Each alternative reaches only as far as the word it excuses: "nie" across auxiliary words, "czy" up to the next
# conjunction and 80 characters, so "sprawdziłem, czy test przechodzi i zapisałem wynik" stays a claim.
# ponytail: a word list, measured on 10 days of answers; "zapisane w Lean" or "zapisane CV" still ask for a link.
# Parse the sentence (a tagger such as Morfeusz) if the false blocks start to cost more than one extra turn.
DESCRIBES = re.compile(
    rf"\bnie\s+(?:(?:jest|są|był\w*|został\w*|jeszcze|już)\s+){{0,2}}{VERB}"
    rf"|(?<!\btak\s)\bczy\b(?:(?!\b(?:i|oraz|a|ale|więc|potem)\b)[^,;.!?\n]){{0,80}}\b{VERB}"
    rf"|[„\"`]{VERB}\w+[”“\"`]"
    rf"|\b{VERB}n\w+\s+(?:tak,?\s+(?:żeby|aby|by)|inaczej|poprawnie|błędnie|źle)\b"
    rf"|\b(?:poprawnie|błędnie|źle|inaczej)\s+{VERB}n"
    rf"|\bdopisa(?:ł|li)\w*by\w*",  # conditional mood, e.g. dopisałbym
    re.IGNORECASE)
LINK = re.compile(r"https?://\S+|[~/][\w./~-]*\w:\d+")
REASON = ("Reguła ownera 2026-11-16 (~/.claude/CLAUDE.md, sekcja „linki do reguł i do zapisów”): odpowiedź ze słowem "
          "„zapisane” albo „dopisałem” MUSI podać link do miejsca zapisu: `ścieżka:linia` albo adres URL. "
          "Dopisz link i zakończ odpowiedź.")


def verdict(event):
    """None lets the answer through; a string is the reason for a block."""
    if event.get("stop_hook_active"):
        return None  # one reminder per stop, never a loop
    text = event.get("last_assistant_message") or ""
    saved = list(SAVED.finditer(text))
    described = [m.span() for m in DESCRIBES.finditer(text)] if saved else []
    claims = any(not any(a <= m.start() < b for a, b in described) for m in saved)
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
    assert say("Sprawdzam, czy Opus zapisał wynik.") is None
    assert say("Hook reaguje na słowo „zapisane“.") is None                  # the German-style closing quote
    # a claim next to "nie", "czy" or a conjunction is still a claim
    assert say("Nie tylko zapisałem regułę, ale też dodałem test.") == REASON
    assert say("Sprawdziłem, czy test przechodzi i zapisałem wynik w SB.") == REASON
    assert say("Tak czy inaczej zapisałem notatkę.") == REASON
    assert say("Zapisanych zostało 15 wiadomości.") == REASON
    assert say("Reguła jest zapisana w formacie YAML w pamięci.") == REASON  # a format can come with a place
    assert say("Dopisałem regułę do pamięci.") == REASON
    assert say("Dopisanych zostało 5 wierszy.") == REASON
    assert say("W rejestrze jest dopisanych 5 wierszy.") == REASON
    assert say("Testu nie dopisałem.") is None
    assert say("Sprawdzam, czy wiersz jest dopisany.") is None
    assert say("Hook nie rozpoznaje słowa „dopisałem”.") is None
    assert say("Linia jest dopisana tak, żeby test przeszedł.") is None
    assert say("Daty są poprawnie dopisane.") is None
    assert say("Poprawka: dopisałbym 1 zdanie.") is None
    assert say("Wpisałem wynik do rejestru.") is None  # "wpisać" stays out
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
