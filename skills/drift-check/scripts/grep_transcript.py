#!/usr/bin/env python3
"""Search one Claude Code transcript, including tool calls and tool results; print local time and context.

Usage: grep_transcript.py TRANSCRIPT REGEX [FROM_HH:MM] [TO_HH:MM] [DATE] | --selftest
DATE has the form YYYY-MM-DD and defaults to today. One match per transcript entry, at most 40 matches.
"""
import json
import os
import re
import sys
import tempfile
from datetime import datetime

WIDTH, LIMIT = 260, 40


def flat(content):
    if isinstance(content, str):
        return content
    out = []
    for b in content or []:
        if not isinstance(b, dict):
            continue
        if b.get("type") == "text":
            out.append(b.get("text", ""))
        elif b.get("type") == "tool_use":
            out.append(f"[{b.get('name')}] " + json.dumps(b.get("input"), ensure_ascii=False))
        elif b.get("type") == "tool_result":
            out.append("[result] " + flat(b.get("content")))
    return "\n".join(out)


def search(path, rx, lo="00:00", hi="23:59", day=None):
    day = day or datetime.now().strftime("%Y-%m-%d")
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if not e.get("timestamp") or e.get("isSidechain"):
                continue
            t = datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")).astimezone()
            if t.strftime("%Y-%m-%d") != day or not lo <= t.strftime("%H:%M") <= hi:
                continue
            s = flat((e.get("message") or {}).get("content"))
            m = rx.search(s)
            if m:
                a, b = max(0, m.start() - WIDTH), min(len(s), m.end() + WIDTH)
                out.append(f"{t:%H:%M:%S} {e.get('type')}: …{' '.join(s[a:b].split())}…")
                if len(out) >= LIMIT:
                    out.append("[limit reached]")
                    break
    return out


def selftest():
    ts = "2026-11-15T12:00:00Z"
    t = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone()
    row = {"type": "user", "timestamp": ts,
           "message": {"content": [{"type": "tool_result", "content": [{"type": "text", "text": "abc needle xyz"}]}]}}
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as fh:
        fh.write(json.dumps(row) + "\n")
    try:
        day = t.strftime("%Y-%m-%d")
        hits = search(fh.name, re.compile("needle"), day=day)
        assert len(hits) == 1 and "[result] abc needle xyz" in hits[0], hits
        assert search(fh.name, re.compile("needle"), day="2000-01-01") == []      # the DATE filter
        assert search(fh.name, re.compile("absent"), day=day) == []
    finally:
        os.unlink(fh.name)
    return "ok"


def main():
    if "--selftest" in sys.argv:
        print(selftest())
        return
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    args = sys.argv[3:]
    lo = args[0] if len(args) > 0 else "00:00"
    hi = args[1] if len(args) > 1 else "23:59"
    day = args[2] if len(args) > 2 else None
    for hit in search(sys.argv[1], re.compile(sys.argv[2], re.I), lo, hi, day):
        print(hit)


if __name__ == "__main__":
    main()
