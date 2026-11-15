#!/usr/bin/env python3
"""List the Claude Code sessions whose process is alive: pid, session id, name, status, entrypoint, transcript.

Source: the session registry ~/.claude/sessions/<pid>.json. Only *.json files are read; the *.key files hold
secrets and are never opened. Entrypoint "cli" or "claude-desktop" marks an owner session; "sdk-ts" or "sdk-cli"
marks a session started by a tool.

Usage: open_sessions.py [--selftest]
"""
import glob
import json
import os
import sys
import tempfile
import time

REGISTRY = os.path.expanduser("~/.claude/sessions")
PROJECTS = os.path.expanduser("~/.claude/projects")


def alive(pid):
    return os.path.exists(f"/proc/{pid}")


def open_sessions(registry=REGISTRY, projects=PROJECTS, is_alive=alive):
    rows = []
    for path in glob.glob(os.path.join(registry, "*.json")):
        try:
            with open(path, encoding="utf-8") as fh:
                d = json.load(fh)
        except (OSError, ValueError):
            continue
        pid, sid = d.get("pid"), d.get("sessionId", "")
        if not pid or not sid or not is_alive(pid):
            continue
        found = glob.glob(os.path.join(projects, "*", f"{sid}.jsonl"))
        rows.append({"pid": pid, "session": sid, "name": d.get("name", ""), "status": d.get("status", ""),
                     "entrypoint": d.get("entrypoint", ""), "transcript": found[0] if found else "",
                     "mtime": os.path.getmtime(found[0]) if found else 0})
    return sorted(rows, key=lambda r: r["mtime"], reverse=True)


def selftest():
    with tempfile.TemporaryDirectory() as tmp:
        reg, proj = os.path.join(tmp, "sessions"), os.path.join(tmp, "projects")
        os.makedirs(reg)
        os.makedirs(os.path.join(proj, "-home-x"))
        for pid, sid in ((101, "aaa"), (102, "bbb")):
            with open(os.path.join(reg, f"{pid}.json"), "w") as fh:
                json.dump({"pid": pid, "sessionId": sid, "name": f"s{pid}", "status": "idle", "entrypoint": "cli"}, fh)
        with open(os.path.join(reg, "101.abc.key"), "w") as fh:
            fh.write("not-json")                                   # a key file is never parsed
        open(os.path.join(proj, "-home-x", "aaa.jsonl"), "w").close()
        rows = open_sessions(reg, proj, is_alive=lambda pid: pid == 101)
        assert [r["name"] for r in rows] == ["s101"], rows      # the dead pid 102 is skipped
        assert rows[0]["transcript"].endswith("aaa.jsonl"), rows
    return "ok"


def main():
    if "--selftest" in sys.argv:
        print(selftest())
        return
    for r in open_sessions():
        when = time.strftime("%m-%d %H:%M", time.localtime(r["mtime"])) if r["mtime"] else "-"
        print(f"{r['pid']}\t{r['session'][:8]}\t{r['name']}\t{r['status']}\t{r['entrypoint']}\t{when}\t{r['transcript']}")


if __name__ == "__main__":
    main()
