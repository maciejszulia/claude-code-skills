#!/usr/bin/env python3
"""Add the local Gitea as the third push URL of each clone that pushes to GitHub and GitLab, and push to Gitea.

Owner 2026-11-15, 22:31: „pomiedzy glab i gh niech będzie gitea”. Pair decision P10: Gitea is the third push URL,
after GitHub and GitLab, because an error of the second URL stops `git push` before the third one.

Modes, in this order: --dry-run (plan only), --apply (create repos, add the push URL, push), --compare (hashes).
--apply creates a missing Gitea repo with the GitHub visibility, appends the Gitea URL to the push URLs, never touches
the fetch URL, and pushes every branch and every tag straight to the Gitea URL without force (GitHub and GitLab get
no push). The token is read from a file and only ever sent in an HTTP header; it never reaches the output.

Usage: gitea_mirror.py --dry-run|--apply|--compare [--handoff PAGE] [--token-file FILE] | --selftest
Python standard library only: the token travels in a header from process memory, not in a command line.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

HOME = os.path.expanduser("~")
HANDOFF = os.path.join(HOME, ".local/share/silverbullet/space/handoffs/2026-11-15-2035-lead.md")
TOKEN_FILE = os.path.join(HOME, ".config/gitea/token")
API = "http://127.0.0.1:3400/api/v1"
OWNER = "maciejszulia"
SSH = "ssh://git@127.0.0.1:2223/{owner}/{name}.git"


def handoff_clones(text):
    """Clone paths from the "## Repo" table of a lead handoff."""
    part = text.split("\n## Repo", 1)[1].split("\n## ", 1)[0] if "\n## Repo" in text else ""
    return [os.path.expanduser(m) for m in re.findall(r"^\| `(~[^`]*)` \|", part, re.M)]


def git(path, *args):
    r = subprocess.run(["git", "-C", path, *args], capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def mirror_remote(path):
    """(remote, GitHub repo name, push URLs) when a remote pushes to exactly GitHub and GitLab, else None."""
    rc, names = git(path, "remote")
    for remote in names.split() if rc == 0 else []:
        _, urls = git(path, "config", "--get-all", f"remote.{remote}.pushurl")
        urls = urls.split()
        hub = [u for u in urls if "github.com" in u]
        lab = [u for u in urls if "gitlab.com" in u]
        if len(urls) == 2 and hub and lab:
            name = re.sub(r"\.git$", "", hub[0].rstrip("/").rsplit("/", 1)[-1].rsplit(":", 1)[-1])
            return remote, name, urls
        if len(urls) == 3 and hub and lab and "127.0.0.1:2223" in urls[2]:
            name = re.sub(r"\.git$", "", hub[0].rstrip("/").rsplit("/", 1)[-1].rsplit(":", 1)[-1])
            return remote, name, urls                 # already done: --apply only pushes again
    return None


def api(method, path, token, body=None):
    """(HTTP status, parsed JSON or None). Errors give the status only; the token stays in the header."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method,
                                 headers={"Authorization": "token " + token, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, None


def github_private(name):
    r = subprocess.run(["gh", "api", f"repos/{OWNER}/{name}", "--jq", ".private"], capture_output=True, text=True)
    return {"true": True, "false": False}.get(r.stdout.strip())


def default_branch(path, remote):
    rc, ref = git(path, "symbolic-ref", "--short", f"refs/remotes/{remote}/HEAD")
    if rc == 0 and "/" in ref:
        return ref.split("/", 1)[1]
    rc, cur = git(path, "rev-parse", "--abbrev-ref", "HEAD")
    return cur if rc == 0 else "main"


def plan(clones):
    rows = []
    for path in clones:
        if not os.path.isdir(os.path.join(path, ".git")):
            continue
        hit = mirror_remote(path)
        if hit:
            remote, name, urls = hit
            rows.append({"path": path, "remote": remote, "name": name, "urls": urls,
                         "gitea": SSH.format(owner=OWNER, name=name)})
    return rows


def main():
    if "--selftest" in sys.argv:
        print(selftest())
        return 0
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--compare", action="store_true")
    p.add_argument("--handoff", default=HANDOFF)
    p.add_argument("--token-file", default=TOKEN_FILE)
    a = p.parse_args()
    with open(a.handoff, encoding="utf-8") as fh:
        rows = plan(handoff_clones(fh.read()))
    if a.compare:
        bad = 0
        for r in rows:
            branch = default_branch(r["path"], r["remote"])
            _, local = git(r["path"], "rev-parse", f"refs/heads/{branch}")
            out = subprocess.run(["git", "ls-remote", r["gitea"], f"refs/heads/{branch}"], capture_output=True, text=True)
            remote = out.stdout.split()[0] if out.stdout.split() else "missing"
            same = local == remote
            bad += not same
            print(f"{r['name']}\t{branch}\tlocal {local[:7]}\tgitea {remote[:7]}\t{'same' if same else 'DIFFERENT'}")
        print(f"{len(rows)} clones, {len(rows) - bad} same, {bad} different")
        return 1 if bad else 0
    token = ""
    if a.apply:
        with open(a.token_file, encoding="utf-8") as fh:
            token = fh.read().strip()
    for r in rows:
        private = github_private(r["name"])
        line = f"{r['name']}\t{r['path']}\tremote {r['remote']}\tprivate {private}\tpush URLs {len(r['urls'])} -> 3"
        if a.dry_run:
            print(line + f"\tadd {r['gitea']}")
            continue
        if private is None:
            print(line + "\tSKIP: GitHub visibility unknown")
            continue
        status, _ = api("GET", f"/repos/{OWNER}/{r['name']}", token)
        if status == 404:
            status, _ = api("POST", "/user/repos", token, {"name": r["name"], "private": private})
            if status != 201:
                print(line + f"\tSKIP: Gitea create HTTP {status}")
                continue
        if len(r["urls"]) == 2:
            git(r["path"], "remote", "set-url", "--add", "--push", r["remote"], r["gitea"])
        b = subprocess.run(["git", "-C", r["path"], "push", "--quiet", r["gitea"], "--all"], capture_output=True, text=True)
        t = subprocess.run(["git", "-C", r["path"], "push", "--quiet", r["gitea"], "--tags"], capture_output=True, text=True)
        # the Gitea URL is a push URL of the remote, so git moved <remote>/* to the Gitea state; fetch puts them back
        git(r["path"], "fetch", "--quiet", r["remote"])
        print(line + f"\tbranches exit {b.returncode}\ttags exit {t.returncode}"
              + (f"\t{(b.stderr or t.stderr).strip().splitlines()[-1][:120]}" if b.returncode or t.returncode else ""))
    return 0


def selftest():
    page = ("## Stan\n\n| `~/x` | a |\n\n## Repo\n\n| Repo | Gałąź |\n|---|---|\n| `~/one` | main |\n"
            "| `~/.local/share/two` | dev |\n\n## Kolejka\n\n| `~/three` | x |\n")
    assert handoff_clones(page) == [os.path.join(HOME, "one"), os.path.join(HOME, ".local/share/two")]
    with tempfile.TemporaryDirectory() as tmp:
        repo = os.path.join(tmp, "r")
        subprocess.run(["git", "init", "-q", repo], check=True)
        git(repo, "remote", "add", "origin", "https://gitlab.com/maciejszulia/demo.git")
        assert mirror_remote(repo) is None                                   # no push URLs: not a mirror clone
        git(repo, "remote", "set-url", "--add", "--push", "origin", "git@github.com:maciejszulia/demo.git")
        git(repo, "remote", "set-url", "--add", "--push", "origin", "https://gitlab.com/maciejszulia/demo.git")
        remote, name, urls = mirror_remote(repo)
        assert (remote, name, len(urls)) == ("origin", "demo", 2), (remote, name, urls)
        git(repo, "remote", "set-url", "--add", "--push", "origin", SSH.format(owner=OWNER, name="demo"))
        _, pushes = git(repo, "config", "--get-all", "remote.origin.pushurl")
        assert pushes.split()[2].startswith("ssh://git@127.0.0.1:2223/") and "github" in pushes.split()[0]
        _, fetch = git(repo, "remote", "get-url", "origin")
        assert fetch == "https://gitlab.com/maciejszulia/demo.git"           # the fetch URL stays as it was
        assert mirror_remote(repo)[1] == "demo"                              # a done clone is still found
    return "ok"


if __name__ == "__main__":
    sys.exit(main())
