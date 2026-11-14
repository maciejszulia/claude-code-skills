#!/usr/bin/env python3
"""sb-mem — streszczenie sesji przez haiku (decyzja ownera 20.09.2026: hooki deterministyczne + haiku na SessionEnd).

SessionEnd (stdin JSON): bierze linie tej sesji z dziennika SB (dziś i wczoraj); gdy ≥ 3 nowe linie, odpala ODŁĄCZONE
dziecko `sb-summarize.py --run <sid>` i kończy się natychmiast (kod 0). Dziecko woła `claude -p --model haiku` bez
settings (bez hooków i pluginów), dopisuje jedną linię `podsumowanie:` do dziennika i `temat:` do linii END w sessions.md.
`--dry-run <sid>` drukuje prompt bez modelu. SB_MEM_CLAUDE=<ścieżka> podmienia binarkę (selftest). Nigdy nie blokuje.
ponytail: dziecko czyta ~60 k tokenów cache (CLAUDE.md + MEMORY.md); gdy za drogo — CLAUDE_CONFIG_DIR z minimalnym profilem."""
import datetime
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dziennik  # noqa: E402

SPACE = dziennik.SPACE
CLAUDE = os.environ.get("SB_MEM_CLAUDE", "claude")
PROMPT = ("Streść w JEDNEJ linii (≤ 400 znaków, po polsku, bez markdownu, bez emoji, terminy IT po angielsku): co zlecono, "
          "co zrobiono, co zostało otwarte. Bez danych osobowych i sekretów. Odpowiedz tylko tą linią.\n"
          "Dziennik sesji Claude Code {sid8}:\n{lines}")


def session_lines(sid8):
    """Linie sesji z dziś i wczoraj; puste, gdy od ostatniego podsumowania nic nie doszło."""
    today = datetime.date.today()
    out = []
    for day in (today - datetime.timedelta(days=1), today):
        path = os.path.join(SPACE, "dziennik", f"{day:%Y-%m-%d}.md")
        if os.path.exists(path):
            out += [l.rstrip("\n") for l in open(path, encoding="utf-8", errors="replace") if f"| lead {sid8} |" in l]
    if out and "| podsumowanie:" in out[-1]:
        return []
    return [l for l in out if "| podsumowanie:" not in l][-80:]


def build_prompt(sid8):
    lines = session_lines(sid8)
    return (PROMPT.format(sid8=sid8, lines="\n".join(l[:200] for l in lines)) if len(lines) >= 3 else "")


def run(sid):
    sid8 = sid[:8]
    prompt = build_prompt(sid8)
    if not prompt:
        return
    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}
    env["SB_MEM_CHILD"] = "1"
    # --setting-sources "": bez settings.json (hooki, pluginy, model ownera) — z settings `--model haiku` poszło na sonnet-5 (20.09)
    r = subprocess.run([CLAUDE, "-p", "--setting-sources", "", "--model", "haiku", "--max-turns", "1", "--tools", "",
                        "--no-session-persistence", "--output-format", "json", prompt],
                       cwd="/", env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=180)
    try:
        res = json.loads(r.stdout)
        text = next((l.strip() for l in str(res.get("result") or "").split("\n") if l.strip()), "")
        usage = ", ".join(f"{m} in {u['inputTokens']} cache {u['cacheReadInputTokens']} out {u['outputTokens']} ${u['costUSD']:.4f}"
                          for m, u in (res.get("modelUsage") or {}).items())
    except Exception:
        text, usage = "", f"rc {r.returncode}: {r.stderr.strip()[:200]}"
    if not os.environ.get("SB_MEM_CLAUDE"):  # selftest z podstawioną binarką nie śmieci w logu kosztów
      with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sb-summarize.log"), "a", encoding="utf-8") as log:
        log.write(f"{datetime.datetime.now():%Y-%m-%dT%H:%M:%S} {sid8} {usage} | {'ok' if text else 'brak wyniku'}\n")
    if r.returncode != 0 or not text:
        return
    text = dziennik.one_line(text, 400)
    dziennik.append("podsumowanie: " + text, "lead", sid8)
    path = os.path.join(SPACE, "sessions.md")
    if not os.path.exists(path):
        return
    lines = open(path, encoding="utf-8").read().split("\n")
    for i in range(len(lines) - 1, -1, -1):
        if "| END |" in lines[i] and f"session {sid} |" in lines[i]:
            if "| temat:" not in lines[i]:
                lines[i] += " | temat: " + dziennik.one_line(text, 120)
                open(path, "w", encoding="utf-8").write("\n".join(lines))
            break


def main():
    if os.environ.get("SB_MEM_CHILD"):
        return
    if len(sys.argv) == 3 and sys.argv[1] == "--run":
        return run(sys.argv[2])
    if len(sys.argv) == 3 and sys.argv[1] == "--dry-run":
        print(build_prompt(sys.argv[2][:8]))
        return
    d = json.load(sys.stdin)
    sid = str(d.get("session_id", ""))
    if not sid or "/subagents/" in str(d.get("transcript_path", "")) or not build_prompt(sid[:8]):
        return
    subprocess.Popen([sys.executable, os.path.abspath(__file__), "--run", sid], start_new_session=True,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
