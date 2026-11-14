#!/usr/bin/env python3
"""Dziennik leada (owner 29.08 07:1x: „rób sobie ciągle notatki, co robisz, co sobie zleciłeś — niech to będzie twój hook").

PostToolUse: jedna linia na wywołanie Agent / Workflow / Skill / Artifact (Bash wyłączony 29.08 14:5x) do
~/.local/share/silverbullet/space/dziennik/YYYY-MM-DD.md (SB widzi katalog). Nigdy nie blokuje: każdy błąd = cicho, kod 0.
Sekrety: linia przechodzi przez ten sam filtr co Panel AI ([sudo] password, tokeny).

sb-mem (owner 20.09.2026: „zrób z SilverBulleta claude-mem”) — dziennik jest strumieniem obserwacji sesji:
UserPromptSubmit → `prompt:`, Stop → `odpowiedź:` (last_assistant_message), PostToolUse Write/Edit → `zapis:` (jedna
linia na plik na sesję), PostToolUse Bash tylko `git commit`/`git push` → `commit:`/`push:`. Czyta to sb-recall.py
(karty sesji na starcie), streszcza sb-summarize.py. Dane gości nie wchodzą do SB: e-mail i telefon → [wycięte]."""
import datetime
import json
import os
import re
import sys

SPACE = os.environ.get("SB_MEM_SPACE", os.path.expanduser("~/.local/share/silverbullet/space"))
OUT = os.path.join(SPACE, "dziennik")
SECRET = re.compile(r"(\[sudo\] password|password for|passwd|(glpat|glrt|sk|xox[bp])-[A-Za-z0-9_-]{8,})", re.I)
# ponytail: e-mail + polski numer (9 cyfr w trójkach, opcjonalne +48); PESEL/adresy nie — dopisać, gdy trafią do promptów
PII = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+|(?<![\w.-])(?:\+48[ -]?)?(?:\d{3}[ -]?){2}\d{3}(?![\w.-])")


def one_line(s, n=160):
    s = " ".join(str(s or "").split())
    s = SECRET.sub("[wycięte]", s)
    s = PII.sub("[wycięte]", s)
    return s[:n] + ("…" if len(s) > n else "")


def day_path(now=None):
    now = now or datetime.datetime.now().astimezone()
    return os.path.join(OUT, now.strftime("%Y-%m-%d") + ".md")


def append(what, sub="lead", sid=""):
    """Dopisz jedną linię do dziennika dnia (nagłówek strony przy pierwszym wpisie)."""
    now = datetime.datetime.now().astimezone()
    os.makedirs(OUT, exist_ok=True)
    path = day_path(now)
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8") as f:
        if new:
            f.write(f"---\ntitle: \"Dziennik leada {now:%Y-%m-%d}\"\ntags: [dziennik, auto]\n---\n\n# Dziennik leada {now:%Y-%m-%d}\n\nJedna linia na wywołanie narzędzia (hook `~/.claude/hooks/dziennik.py`).\n\n")
        f.write(f"- {now:%H:%M:%S} | {sub} {sid} | {what}\n")


def last_assistant(transcript_path, tail_bytes=262144):
    """Fallback dla Stop bez last_assistant_message: tekst ostatniej odpowiedzi z końca transkryptu JSONL."""
    try:
        size = os.path.getsize(transcript_path)
        with open(transcript_path, "r", errors="replace") as fh:
            fh.seek(max(0, size - tail_bytes))
            lines = fh.read().split("\n")
    except Exception:
        return ""
    for line in reversed(lines):
        try:
            d = json.loads(line)
        except Exception:
            continue
        msg = d.get("message") or {}
        if d.get("type") != "assistant" and msg.get("role") != "assistant":
            continue
        content = msg.get("content")
        if isinstance(content, str):
            return content
        text = " ".join(b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")
        if text.strip():
            return text
    return ""


def main():
    if os.environ.get("SB_MEM_CHILD"):  # dziecko sb-summarize: jego prompt nie jest obserwacją
        return
    try:
        d = json.load(sys.stdin)
    except Exception:
        return
    ev = d.get("hook_event_name", "")
    tool = d.get("tool_name", "")
    inp = d.get("tool_input") or {}
    sub = "subagent" if "/subagents/" in str(d.get("transcript_path", "")) else "lead"
    sid = str(d.get("session_id", ""))[:8]
    if ev == "UserPromptSubmit":
        p = str(d.get("prompt", "")).strip()
        if not p or p.startswith("/") or "[bez-sb]" in p:
            return
        what = "prompt: " + one_line(p)
    elif ev == "Stop":
        msg = d.get("last_assistant_message") or last_assistant(d.get("transcript_path", ""))
        if not str(msg).strip():
            return
        what = "odpowiedź: " + one_line(msg, 200)
    elif tool == "Agent":
        what = f"zlecenie → {inp.get('subagent_type') or 'agent'}[{inp.get('model') or 'domyślny'}]: {one_line(inp.get('description') or inp.get('prompt'))}"
    elif tool == "Workflow":
        what = f"flota (Workflow): {one_line(inp.get('name') or inp.get('scriptPath') or (inp.get('script') or '')[:200])}"
    elif tool == "Skill":
        what = f"skill /{inp.get('skill', '')} {one_line(inp.get('args', ''), 80)}"
    elif tool == "Artifact":
        what = f"artefakt {inp.get('action') or 'publish'}: {one_line(os.path.basename(inp.get('file_path') or inp.get('url') or ''), 80)}"
    elif tool in ("Write", "Edit", "MultiEdit"):
        path = str(inp.get("file_path") or "")
        if not path:
            return
        what = "zapis: " + path
        try:  # jedna linia na plik na sesję (dzień)
            if f"| {sub} {sid} | {what}\n" in open(day_path(), encoding="utf-8").read():
                return
        except Exception:
            pass
    elif tool == "Bash":
        # Bash celowo NIE jest logowany poza commit/push: komendy subagentów floty zalewały dziennik (29.08: ~1 400 linii/h),
        # a „co robisz” pokazuje Panel AI z transkryptów; dziennik = delegacje, skille, artefakty, prompty, zapisy, commity.
        cmd = str(inp.get("command") or "")
        m = re.search(r"\bgit\b[^|;&\n]*\bcommit\b.*?-m\s+(['\"])(.*?)\1", cmd, re.S)
        if m:
            what = "commit: " + one_line(m.group(2), 120)
        elif re.search(r"\bgit\b[^|;&\n]*\bpush\b", cmd):
            what = "push: " + one_line(re.search(r"\bgit\b[^|;&\n]*\bpush\b(.*)", cmd).group(0), 100)
        else:
            return
    else:
        return
    append(what, sub, sid)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
