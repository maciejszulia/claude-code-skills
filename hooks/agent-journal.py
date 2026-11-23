#!/usr/bin/env python3
"""agent-journal: a tamper-evident event journal for Claude Code sessions and their subagents.

Hook (every event): reads the hook JSON from stdin and appends 1 line to ~/.local/state/agent-journal/YYYY-MM-DD.jsonl.
Each line holds the hash of the line before it, so an edited or deleted line breaks the chain (`--verify`).
The journal stores what happened, not what was said: the prompt only as a SHA-256, a command with secrets and e-mail
addresses cut out, never a tool's output. It never blocks a tool call: every error exits 0.

    agent-journal.py                  hook mode (stdin = hook JSON)
    agent-journal.py --verify [FILE]  check the hash chain of a day file (default: today)
    agent-journal.py --lifecycle [FILE]  1 line per subagent: start, stop, minutes, type
    agent-journal.py --self-check     write, verify and tamper in a temporary folder

Settings (~/.claude/settings.json): the same command under SessionStart, UserPromptSubmit, PreToolUse, PostToolUse,
PostToolUseFailure, SubagentStart, SubagentStop, Stop and SessionEnd.
"""
import datetime
import fcntl
import hashlib
import json
import os
import re
import sys
import tempfile

DIR = os.environ.get("AGENT_JOURNAL_DIR", os.path.expanduser("~/.local/state/agent-journal"))
SECRET = re.compile(r"(gh[opsu]_|github_pat_|glpat-|sk-|xox[bp]-)[A-Za-z0-9_-]{8,}|(password|passwd|token)=\S+", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
GENESIS = "0" * 64


def clean(text, n=200):
    text = " ".join(str(text or "").split())
    return EMAIL.sub("[email]", SECRET.sub("[secret]", text))[:n]


def action(data):
    """A short, redacted description of what the event does."""
    tool, inp = data.get("tool_name") or "", data.get("tool_input") or {}
    if tool == "Bash":
        return clean(inp.get("command"))
    if tool in ("Write", "Edit", "Read", "NotebookEdit"):
        return clean(inp.get("file_path"))
    if tool == "Agent":
        return clean("%s %s %s: %s" % (inp.get("subagent_type", ""), inp.get("model", ""), inp.get("effort", ""),
                                       inp.get("description", "")))
    if data.get("prompt"):
        return "prompt sha256 " + hashlib.sha256(data["prompt"].encode()).hexdigest()[:16]
    return clean(inp.get("url") or inp.get("skill") or inp.get("query") or "")


def last_hash(path):
    """Hash of the newest line: today's file, else the newest older day file, else GENESIS."""
    # ponytail: reads the whole day file for its last line; seek from the end once a day file passes 50 MB
    days = sorted(f for f in os.listdir(os.path.dirname(path)) if f.endswith(".jsonl") and f <= os.path.basename(path))
    for name in reversed(days):
        with open(os.path.join(os.path.dirname(path), name), "rb") as fh:
            lines = fh.read().splitlines()
        if lines:
            return json.loads(lines[-1])["h"]
    return GENESIS


def seal(record, prev):
    record = dict(record, prev=prev)
    record["h"] = hashlib.sha256(json.dumps(record, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return record


def append(data, now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc)
    os.makedirs(DIR, exist_ok=True)
    path = os.path.join(DIR, now.strftime("%Y-%m-%d") + ".jsonl")
    record = {"t": now.isoformat(timespec="seconds"), "session": (data.get("session_id") or "")[:8],
              "event": data.get("hook_event_name", ""), "agent": data.get("agent_id") or "",
              "agent_type": data.get("agent_type") or "", "tool": data.get("tool_name") or "", "action": action(data)}
    with open(os.path.join(DIR, ".lock"), "w") as lock:  # sessions write at the same time; the chain needs 1 writer
        fcntl.flock(lock, fcntl.LOCK_EX)
        line = json.dumps(seal(record, last_hash(path)), sort_keys=True, ensure_ascii=False)
        with open(path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(line + "\n")


def verify(path):
    """Return None when the chain holds, else the number of the first broken line (1-based)."""
    prev = None
    for n, raw in enumerate(open(path, encoding="utf-8"), 1):
        rec = json.loads(raw)
        h = rec.pop("h")
        if (prev is not None and rec["prev"] != prev) or seal(rec, rec.pop("prev"))["h"] != h:
            return n
        prev = h
    return None


def lifecycle(path):
    starts = {}
    for raw in open(path, encoding="utf-8"):
        rec = json.loads(raw)
        if rec["event"] == "SubagentStart":
            starts[rec["agent"]] = rec
        elif rec["event"] == "SubagentStop" and rec["agent"] in starts:
            a, b = starts.pop(rec["agent"]), rec
            minutes = (datetime.datetime.fromisoformat(b["t"]) - datetime.datetime.fromisoformat(a["t"])).total_seconds() / 60
            print("%s  %s -> %s  %5.1f min  %s" % (rec["agent"][:12], a["t"][11:19], b["t"][11:19], minutes, a["agent_type"]))
    for agent, a in starts.items():
        print("%s  %s -> running  %s" % (agent[:12], a["t"][11:19], a["agent_type"]))


def self_check():
    global DIR
    with tempfile.TemporaryDirectory() as DIR:
        t0 = datetime.datetime(2026, 11, 23, 20, 0, tzinfo=datetime.timezone.utc)
        append({"hook_event_name": "SubagentStart", "agent_id": "a1", "agent_type": "Minimal Change Engineer"}, t0)
        append({"hook_event_name": "PreToolUse", "tool_name": "Bash",
                "tool_input": {"command": "git push https://x:ghp_abcdefghijkl@github.com mail me@example.org"}},
               t0 + datetime.timedelta(minutes=1))
        append({"hook_event_name": "SubagentStop", "agent_id": "a1"}, t0 + datetime.timedelta(minutes=6))
        path = os.path.join(DIR, "2026-11-23.jsonl")
        lines = open(path, encoding="utf-8").read().splitlines()
        assert "ghp_" not in lines[1] and "example.org" not in lines[1], lines[1]
        assert verify(path) is None
        tampered = lines[1].replace("PreToolUse", "PostToolUse")
        open(path, "w", encoding="utf-8").write("\n".join([lines[0], tampered, lines[2]]) + "\n")
        assert verify(path) == 2, verify(path)
    print("self-check OK")


def main(argv):
    day = os.path.join(DIR, datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d") + ".jsonl")
    if argv[:1] == ["--self-check"]:
        return self_check()
    if argv[:1] in (["--verify"], ["--lifecycle"]):
        path = argv[1] if len(argv) > 1 else day
        if argv[0] == "--lifecycle":
            return lifecycle(path)
        broken = verify(path)
        print("chain OK: %s" % path if broken is None else "chain BROKEN at line %d: %s" % (broken, path))
        return 0 if broken is None else 1
    try:
        append(json.load(sys.stdin))
    except Exception:  # a journal must never stop the session
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
