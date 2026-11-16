#!/usr/bin/env python3
"""sb-mem (owner 20.09.2026: „zrób z SilverBulleta claude-mem”) — część czytająca.

SessionStart: karty ostatnich sesji z dziennika SB (3 dni, grupowane po sesji: pierwszy prompt → podsumowanie albo
ostatnia odpowiedź), 3 ostatnie papercuts, najnowszy handoff — na stdout, Claude Code dokłada to do kontekstu.
PreToolUse Read: linie dziennika/handoffów/papercuts/decisions/runbooks wspominające czytany plik (≤ 5, najnowsze
najpierw) jako additionalContext — odpowiednik „This file has prior observations” z claude-mem.
Nigdy nie blokuje: każdy błąd = cicho, kod 0. Sesje subagentów i dziecko sb-summarize (SB_MEM_CHILD=1) pomijane."""
import datetime
import json
import os
import re
import sqlite3
import subprocess
import sys

SPACE = os.environ.get("SB_MEM_SPACE", os.path.expanduser("~/.local/share/silverbullet/space"))
LINE = re.compile(r"^- (\d\d:\d\d:\d\d) \| (lead|subagent) (\w+) \| (.*)$")
DAYS, CARDS, HITS = 3, 8, 5
GENERIC = {"index.md", "readme.md", "skill.md", "settings.json", "package.json", "main.py", "__init__.py", "claude.md", "agents.md"}


def cut(s, n):
    s = " ".join(str(s).split())
    return s[:n] + ("…" if len(s) > n else "")


def sessions(skip_sid):
    """[(date, sid, first_time, last_time, n, first_prompt, last_summary)] z ostatnich DAYS dni, najnowsze na końcu."""
    today = datetime.date.today()
    out = {}
    for i in range(DAYS - 1, -1, -1):
        day = today - datetime.timedelta(days=i)
        path = os.path.join(SPACE, "dziennik", f"{day:%Y-%m-%d}.md")
        if not os.path.exists(path):
            continue
        for raw in open(path, encoding="utf-8", errors="replace"):
            m = LINE.match(raw.rstrip("\n"))
            if not m or m.group(2) != "lead" or m.group(3) == skip_sid:
                continue
            t, sid, what = m.group(1), m.group(3), m.group(4)
            s = out.setdefault((day, sid), {"first": t, "last": t, "n": 0, "prompt": "", "sum": "", "ans": ""})
            s["last"], s["n"] = t, s["n"] + 1
            if what.startswith("prompt:") and not s["prompt"]:
                s["prompt"] = what[7:].strip()
            elif what.startswith("podsumowanie:"):
                s["sum"] = what[13:].strip()
            elif what.startswith("odpowiedź:"):
                s["ans"] = what[10:].strip()
            elif not s["prompt"] and not s["ans"]:
                s["ans"] = what  # sesja bez promptu (stare wpisy): pokaż cokolwiek
    return sorted(out.items(), key=lambda kv: (kv[0][0], kv[1]["last"]))[-CARDS:]


def papercuts():
    path = os.path.join(SPACE, "papercuts.md")
    lines, on = [], False
    for raw in open(path, encoding="utf-8", errors="replace") if os.path.exists(path) else []:
        if raw.startswith("## "):
            on = raw.startswith("## Log")
        elif on and raw.startswith("- "):
            lines.append(raw[2:].strip())
    return lines[-3:]


def newest_handoff():
    d = os.path.join(SPACE, "handoffs")
    files = [f for f in os.listdir(d) if f.endswith(".md")] if os.path.isdir(d) else []
    return max(files, key=lambda f: os.path.getmtime(os.path.join(d, f)))[:-3] if files else ""


def codex_recent(project):
    """Obserwacje claude-mem z sesji Codeksa (7 dni) — start claude-mem filtruje po platform_source='claude'."""
    try:
        db = sqlite3.connect("file:" + os.path.expanduser("~/.claude-mem/claude-mem.db") + "?mode=ro", uri=True, timeout=1)
        since = int((datetime.datetime.now() - datetime.timedelta(days=7)).timestamp() * 1000)
        rows = db.execute("select o.created_at_epoch, o.type, o.title from observations o join sdk_sessions s"
                          " on s.memory_session_id = o.memory_session_id where s.platform_source = 'codex'"
                          " and o.project = ? and o.created_at_epoch >= ? order by o.created_at_epoch desc limit 12",
                          (project, since)).fetchall()
        db.close()
    except Exception:
        return []
    return [f"- {datetime.datetime.fromtimestamp(t / 1000):%d.%m %H:%M} {k}: {cut(title, 110)}" for t, k, title in reversed(rows)]


def session_start(d):
    codex = codex_recent(os.path.basename(str(d.get("cwd") or os.getcwd())))
    if codex:
        print("\n".join(["# Codex (claude-mem, ostatnie 7 dni)"] + codex))
    cards = sessions(str(d.get("session_id", ""))[:8])
    if not cards:
        return
    now = datetime.datetime.now()
    out = [f"# SB pamięć (sb-recall) — ostatnie sesje z dziennika/, stan {now:%Y-%m-%d %H:%M}"]
    for (day, sid), s in cards:
        head = cut(s["prompt"], 110) or "(bez promptu)"
        tail = ("podsumowanie: " + cut(s["sum"], 220)) if s["sum"] else ("→ " + cut(s["ans"], 120) if s["ans"] else "")
        out.append(f"- {day:%d.%m} {s['first'][:5]}–{s['last'][:5]} {sid} ({s['n']} linii): {head} {tail}".rstrip())
    pc = papercuts()
    if pc:
        out.append("Papercuts (3 ostatnie): " + " ‖ ".join(cut(p, 140) for p in pc))
    h = newest_handoff()
    if h:
        out.append(f"Ostatni handoff: handoffs/{h}")
    out.append(f"Szukaj w pamięci: /sb-mem search <fraza>; pełna strona dnia: dziennik/{now:%Y-%m-%d}")
    print("\n".join(out))


def file_context(d):
    path = str((d.get("tool_input") or {}).get("file_path") or "")
    base = os.path.basename(path)
    if len(base) < 5 or base.lower() in GENERIC or "/dziennik/" in path:
        return
    try:
        r = subprocess.run(["rg", "-n", "-F", "--no-heading", "-m", "3", base, "dziennik", "handoffs", "papercuts.md",
                            "decisions", "runbooks"], cwd=SPACE, capture_output=True, text=True, timeout=5)
    except Exception:
        return
    hits = sorted((l for l in r.stdout.split("\n") if l.strip()), reverse=True)[:HITS]  # nazwy z datą: najnowsze najpierw
    if not hits:
        return
    ctx = f"Ten plik w pamięci SB ({base}):\n" + "\n".join(cut(h, 200) for h in hits)
    print(json.dumps({"suppressOutput": True, "hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": ctx}}))


def main():
    if os.environ.get("SB_MEM_CHILD"):
        return
    try:
        d = json.load(sys.stdin)
    except Exception:
        return
    if "/subagents/" in str(d.get("transcript_path", "")):
        return
    ev = d.get("hook_event_name", "")
    if ev == "SessionStart":
        session_start(d)
    elif ev == "PreToolUse" and d.get("tool_name") == "Read":
        file_context(d)


def selftest():
    """Cards, papercuts and the newest handoff come from a temporary SB space; a Read of a known file gets its lines."""
    import contextlib
    import io
    import tempfile
    import time
    global SPACE, codex_recent
    codex_recent = lambda project: []                                     # the real claude-mem database stays out
    with tempfile.TemporaryDirectory() as tmp:
        SPACE = tmp
        for d in ("dziennik", "handoffs"):
            os.makedirs(os.path.join(tmp, d))
        with open(os.path.join(tmp, "dziennik", f"{datetime.date.today():%Y-%m-%d}.md"), "w", encoding="utf-8") as f:
            f.write("- 09:00:00 | lead aaaa1111 | prompt: napisz raport\n- 09:05:00 | lead aaaa1111 | zapis: /x/plik-testowy.py\n"
                    "- 09:10:00 | lead aaaa1111 | podsumowanie: raport gotowy\n- 10:00:00 | lead bbbb2222 | prompt: ta sesja\n"
                    "- 10:01:00 | subagent cccc3333 | zapis: /x/y.py\n")
        with open(os.path.join(tmp, "papercuts.md"), "w", encoding="utf-8") as f:
            f.write("# Papercuts\n\n## Log\n\n- p1\n- p2\n- p3\n- p4\n\n## Inne\n\n- p5\n")
        for name, age in (("2026-11-01-lead.md", 100), ("2026-11-02-lead.md", 10)):
            path = os.path.join(tmp, "handoffs", name)
            open(path, "w").close()
            os.utime(path, (time.time() - age, time.time() - age))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            session_start({"session_id": "bbbb2222xyz", "cwd": tmp})          # the current session gets no card
        text = out.getvalue()
        assert "aaaa1111 (3 linii): napisz raport podsumowanie: raport gotowy" in text, text
        assert "bbbb2222" not in text and "cccc3333" not in text and "p2 ‖ p3 ‖ p4" in text and "p1" not in text, text
        assert "Ostatni handoff: handoffs/2026-11-02-lead" in text, text
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            file_context({"tool_input": {"file_path": "/x/plik-testowy.py"}})
            file_context({"tool_input": {"file_path": "/x/README.md"}})        # a generic name gets no context
        ctx = json.loads(out.getvalue())["hookSpecificOutput"]["additionalContext"]
        assert "zapis: /x/plik-testowy.py" in ctx and ctx.count("\n") == 1, ctx
    return "ok"


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        print(selftest())
        sys.exit(0)
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
