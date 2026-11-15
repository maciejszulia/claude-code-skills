#!/usr/bin/env python3
"""Digest of one Claude Code transcript for a drift check: owner prompts, agents, commits, written files, answers.

Usage: session_digest.py TRANSCRIPT [SINCE_ISO] | --selftest
SINCE_ISO (for example 2026-11-15T00:00:00+01:00) keeps prompts, agents, commits and written files from that moment.
"""
import json
import os
import re
import sys
import tempfile
from collections import Counter
from datetime import datetime

NOISE = re.compile(r"^\s*(<system-reminder>|<local-command|Caveat:|\[Request interrupted|<task-notification>"
                   r"|This session is being continued)")
COMMAND = re.compile(r"<command-name>([^<]+)</command-name>.*?(?:<command-args>([^<]*)</command-args>)?", re.S)


def local(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone()


def text_of(content):
    if isinstance(content, str):
        return content
    return "\n".join(b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")


def digest(path, since=None):
    prompts, answers, commits, agents, files = [], [], [], [], Counter()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if not e.get("timestamp") or e.get("isSidechain"):
                continue
            t, content = local(e["timestamp"]), (e.get("message") or {}).get("content")
            if e.get("type") == "user" and not e.get("isMeta") and not e.get("isCompactSummary"):
                if isinstance(content, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
                    continue
                s = text_of(content).strip()
                m = COMMAND.search(s)
                s = f"{m.group(1)} {m.group(2) or ''}".strip() if m else s
                if s and not NOISE.match(s):
                    prompts.append((t, s))
            elif e.get("type") == "assistant" and isinstance(content, list):
                s = text_of(content).strip()
                if s:
                    answers.append((t, s))
                for b in content:
                    if not (isinstance(b, dict) and b.get("type") == "tool_use"):
                        continue
                    inp = b.get("input") or {}
                    if b.get("name") == "Bash" and re.search(r"\bgit\b[^\n]*\b(commit|push)\b", inp.get("command", "")):
                        commits.append((t, " ".join(inp["command"].split())[:230]))
                    elif b.get("name") in ("Write", "Edit", "NotebookEdit") and inp.get("file_path") and (not since or t >= since):
                        files[inp["file_path"]] += 1
                    elif b.get("name") in ("Agent", "Task", "Workflow"):
                        agents.append((t, f"{inp.get('description', '')} | model={inp.get('model', '')} type={inp.get('subagent_type', '')}"))

    def keep(rows):
        return [r for r in rows if not since or r[0] >= since]

    def fmt(t):
        return t.strftime("%m-%d %H:%M")

    out = [f"## {os.path.basename(path)}"]
    if prompts:
        out.append(f"first prompt {fmt(prompts[0][0])}: {prompts[0][1][:300]!r}")
        out.append(f"last activity: prompt {fmt(prompts[-1][0])}; answer {fmt(answers[-1][0]) if answers else '-'}")
    out.append("### owner prompts" + (f" since {fmt(since)}" if since else ""))
    out += [f"- {fmt(t)} {s[:260]!r}" for t, s in keep(prompts)[-18:]]
    out.append("### agents")
    out += [f"- {fmt(t)} {s[:200]}" for t, s in keep(agents)[-8:]]
    out.append("### commits and pushes")
    out += [f"- {fmt(t)} {s}" for t, s in keep(commits)[-14:]]
    out.append("### written files (count)")
    out += [f"- {n} {p}" for p, n in files.most_common(25)]
    out.append("### last answers")
    out += [f"- {fmt(t)} {s[:1100]!r}" for t, s in answers[-2:]]
    return "\n".join(out)


def selftest():
    rows = [
        {"type": "user", "timestamp": "2026-11-15T10:00:00Z", "message": {"content": "zrób X"}},
        {"type": "user", "timestamp": "2026-11-15T10:00:01Z", "isMeta": True, "message": {"content": "meta-only"}},
        {"type": "assistant", "timestamp": "2026-11-15T10:05:00Z", "message": {"content": [
            {"type": "text", "text": "Zrobione."},
            {"type": "tool_use", "name": "Bash", "input": {"command": "git commit -m x"}},
            {"type": "tool_use", "name": "Write", "input": {"file_path": "/r/a.py"}}]}},
    ]
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as fh:
        fh.write("\n".join(json.dumps(r) for r in rows))
    try:
        d = digest(fh.name)
        assert "'zrób X'" in d and "meta-only" not in d, d
        assert "git commit -m x" in d and "- 1 /r/a.py" in d and "'Zrobione.'" in d, d
        late = digest(fh.name, local("2026-11-15T11:00:00Z"))
        assert "/r/a.py" not in late and "git commit" not in late, late   # the SINCE filter
    finally:
        os.unlink(fh.name)
    return "ok"


def main():
    if "--selftest" in sys.argv:
        print(selftest())
        return
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    since = datetime.fromisoformat(sys.argv[2]).astimezone() if len(sys.argv) > 2 else None
    print(digest(sys.argv[1], since))


if __name__ == "__main__":
    main()
