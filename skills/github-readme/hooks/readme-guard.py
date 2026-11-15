#!/usr/bin/env python3
"""readme-guard (PostToolUse on Bash): after a large git commit, tell the lead to update the README (skill github-readme).

Owner rule of 2026-11-15: „za każdym razem jak jest duża zmiana na git napisz hooka który zaktualizuje readme”.
Large: the new HEAD commit changes at least 200 lines, adds a top-level directory, or touches a manifest
(pyproject.toml, package.json, requirements*.txt, Dockerfile, compose.yaml, Makefile, .github/workflows/*),
and the commit leaves README.md untouched. Once per commit; lead session only. Never blocks.
"""
import json
import os
import re
import subprocess
import sys

STATE = os.environ.get("README_GUARD_STATE", os.path.expanduser("~/.claude/state/readme-guard.json"))
THRESHOLD = 200
MANIFEST = re.compile(r"(^|/)(pyproject\.toml|package\.json|requirements[^/]*\.txt|Dockerfile|compose\.ya?ml|Makefile)$|^\.github/workflows/")
MSG = ("README-GUARD: commit {sha} w repo {repo} to duża zmiana ({why}), a README.md jej nie opisuje. "
       "Zaktualizuj README według skillu github-readme i zrób osobny commit „docs: ...”. "
       "Jeżeli README już opisuje tę zmianę, napisz ownerowi 1 zdanie, dlaczego.")


def repo_dir(command, cwd):
    m = re.search(r"git\s+-C\s+(\"[^\"]+\"|'[^']+'|\S+)", command)
    if not m:
        m = re.search(r"(?:^|&&|;)\s*cd\s+(\"[^\"]+\"|'[^']+'|\S+)\s*&&", command)
    return os.path.expanduser(m.group(1).strip("\"'")) if m else cwd


def reasons(numstat, added, prev_top):
    """numstat: lines 'added<TAB>deleted<TAB>path'; added: paths added by the commit; prev_top: top-level names before it."""
    files, lines = [], 0
    for row in numstat.splitlines():
        parts = row.split("\t", 2)
        if len(parts) == 3:
            files.append(parts[2])
            lines += sum(int(x) for x in parts[:2] if x.isdigit())
    if any(os.path.basename(f).lower() == "readme.md" for f in files):
        return []
    why = []
    if lines >= THRESHOLD:
        why.append(f"{lines} zmienionych linii")
    new_top = sorted({p.split("/")[0] for p in added if "/" in p} - set(prev_top))
    if new_top:
        why.append("nowy katalog " + ", ".join(new_top))
    if any(MANIFEST.search(f) for f in files):
        why.append("zmiana manifestu")
    return why


def git(path, *args):
    return subprocess.run(["git", "-C", path, *args], capture_output=True, text=True, timeout=10).stdout


def selftest():
    assert reasons("150\t60\tsrc/a.py", [], ["src"]) == ["210 zmienionych linii"]
    assert reasons("5\t1\tsrc/a.py\n3\t0\tREADME.md", [], ["src"]) == []                  # README changed with it
    assert reasons("10\t0\tmcp/server.py", ["mcp/server.py"], ["src"]) == ["nowy katalog mcp"]
    assert reasons("2\t1\tpyproject.toml", [], ["src"]) == ["zmiana manifestu"]
    assert reasons("3\t1\tsrc/a.py", [], ["src"]) == []                                   # small change
    assert repo_dir("git -C ~/x commit -m y", "/w") == os.path.expanduser("~/x")
    assert repo_dir("cd /r/p && git commit -m y", "/w") == "/r/p"
    return "ok"


def main():
    if "--selftest" in sys.argv:
        print(selftest())
        return
    try:
        hook = json.load(sys.stdin)
        if "/subagents/" in str(hook.get("transcript_path", "")):
            return
        command = str((hook.get("tool_input") or {}).get("command", ""))
        if not re.search(r"\bgit\b[^\n]*\b(commit|merge)\b", command):
            return
        repo = git(repo_dir(command, hook.get("cwd") or os.getcwd()), "rev-parse", "--show-toplevel").strip()
        sha = git(repo, "rev-parse", "HEAD").strip() if repo else ""
        if not sha or not os.path.exists(os.path.join(repo, "README.md")):
            return
        try:
            state = json.load(open(STATE, encoding="utf-8"))
        except (OSError, ValueError):
            state = {}
        if state.get(repo) == sha:
            return
        state[repo] = sha
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        json.dump(state, open(STATE, "w", encoding="utf-8"))
        prev_top = git(repo, "ls-tree", "--name-only", "HEAD~1").split() if git(repo, "rev-parse", "--verify", "-q", "HEAD~1") else []
        why = reasons(git(repo, "show", "--numstat", "--format=", "HEAD"),
                      git(repo, "show", "--name-only", "--diff-filter=A", "--format=", "HEAD").split(), prev_top)
        if why:
            msg = MSG.format(sha=sha[:7], repo=repo, why=", ".join(why))
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}}, ensure_ascii=False))
    except Exception:
        pass


if __name__ == "__main__":
    main()
