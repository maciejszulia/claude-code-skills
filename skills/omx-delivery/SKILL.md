---
name: omx-delivery
description: Run a full OMX (oh-my-codex) delivery from Claude Code — choose the lane, write and commit an order file, launch a Codex leader in its own git worktree, hand it the task through tmux, keep every pane in one readable window, and receive the branch on gates you re-run yourself. Use this whenever work is being handed to OMX or Codex ("zleć to OMX-owi", "użyj omx", "niech worker to zrobi", "delegate this to a worker", "let Codex build it"), whenever you are about to type `omx`, `omx team`, `omx ralph` or `omx ultragoal`, whenever a running leader looks stuck or its panes are scattered across tmux windows, and whenever a worker's finished branch needs receiving or reviewing. Reach for it even when the user only says "dowieź mi X" and delegation is the obvious way to get there.
---

# OMX delivery

You are the lead: you decide what gets built, write the order, watch the run, and accept or
refuse the result. The worker writes the product code.

This skill covers only the OMX-specific mechanics. General engineering discipline — read
before you write, verify before you claim done, smallest diff — already applies and is not
repeated here.

## Pick the lane

Upstream is explicit that `omx team` is **not** an entry point; it is for a story that splits
into disjoint areas. The heavy lane on small work buys coordination overhead, idle workers, and
a `completed` counter that counts the leader's own tasks rather than delivered scope.

| Shape of the work | Lane |
|---|---|
| One area, one owner, clear gates | `omx --worktree=<name> --madmax --tmux -c model_reasoning_effort="max"`, then `$ralph` |
| Multi-step plan worth checkpointing across sessions | same launch, then `$ultragoal` |
| Genuinely disjoint areas worth parallel workers | `omx team`, and only inside an ultragoal story |

If the change is two lines you already understand, doing it yourself is cheaper than a
delegation — say so in one line, then do whichever the user asked for.

## The order file

`docs/orders/<YYYY-MM-DD>-<slug>.md`, English, committed before launch — `.omx/` is gitignored
and a worktree only contains committed files, so an uncommitted order simply is not there when
the worker looks.

```markdown
# Order — <imperative one-liner>
Repository, branch, and where work must NOT happen.
Second brain: /home/ms/.local/share/silverbullet/space — read index.md, operating-model.md,
briefings/2026-08-12-omx-stack.md before starting (path only; do not paste their contents).
## Problem            — file:line evidence
## Required outcome   — observable behaviour, numbered
## Contract           — state shape, endpoint, status table, which existing helper to reuse
## Verification       — the exact gate commands, in order
## Constraints        — no new deps, diff surface, language, staging rules
## Definition of done — what the branch looks like, and that the worker stops there
```

Two things earn their space every time:

- **Gates the repo's aggregate script misses.** CI often runs suites that `quality:all` (or its
  local equivalent) does not; a worker that runs only the aggregate reports green on code CI
  rejects.
- **Where work must not happen**, by path: a live checkout whose `dist/` is served, a state
  directory with real sessions, a production database.

When you forbid something, leave a correct path open. A ban that removes the only way to do the
job pushes the worker into a worse one.

## Pre-flight

- One leader at a time: a live `~/.omx/state/session.json` means another session owns the lock.
- Move a **repo-local** `<repo>/.omx/state/session.json` aside first. A pointer left by a
  previous team makes the new worker loop on a blocked Stop with `PROVENANCE_DENIED`, writing
  nothing, and fixing it afterwards does not clear it.
- The main checkout stays on its integration branch — launch pre-flight builds in the current
  directory, and a served `dist/` is not managed by git, so nothing warns you and nothing
  rolls it back.

## Launch

```bash
find /var/tmp/omx -mindepth 1 -mmin +2880 -delete 2>/dev/null   # sprzątanie po poprzednich biegach
cd <repo> && env TMPDIR=/var/tmp/omx PONYTAIL_DEFAULT_MODE=<lite|ultra> \
  omx --worktree=<branch-like-name> --madmax --tmux        # ultra + astra come from config.toml
```

Leader reasoning (owner 2026-08-18): `max` when the leader works alone, `ultra` when it drives
workers (`$team`); OMX has no `--max`/`--ultra` shorthand, the `-c` value goes straight to Codex.
Since 2026-09-05 `~/.codex/config.toml` pins `gpt-6-astra` with `model_reasoning_effort = "ultra"`,
so a plain launch already runs the leader on ultra — pass `-c` only to lower it; roles take max/xhigh
from `~/.codex/.omx-config.json`. Owner 2026-09-05: OMX on Astra is the main lane again.

Leader ponytail mode (owner 2026-08-21, benchmark E1+E2): `lite` for bughunts and new
features, `ultra` for narrow fixes; never `full`. `TMPDIR=/var/tmp/omx` keeps worker scratch
off `/` (OMX has filled `/tmp` to zero mid-run before); the `find` line above is the only
cleanup — there is no cron yet.

`--madmax` is `--dangerously-bypass-approvals-and-sandbox` ("YOLO mode" in the TUI);
`--worktree` is what makes that acceptable, creating `<repo>.omx-worktrees/launch-<branch>`
from the current HEAD. Run state lands in `~/.omx-runs/run-<stamp>-<pid>`.

Called without a TTY the launch ends with `open terminal failed: not a terminal` and
`detached launch safety failure during post-release-attach`. **Only the attach failed.** Check
`tmux list-sessions` before reacting — the session and both panes are usually alive, and
relaunching just fights the session lock.

Dependencies in the worktree are installed there (`npm ci`); never symlink a parent
`node_modules` — one committed symlink replaced the real directory at merge time.

## Hand over one sentence

The leader decomposes your text sentence by sentence into tasks, so a multi-sentence briefing
becomes a task list — including a list of prohibitions turned into work items. Send one
sentence pointing at the committed file:

> Read `docs/orders/<file>.md` in this repository and implement it end to end on the current
> branch, treating that single file as the complete and authoritative specification of scope,
> deliverables, constraints, forbidden paths and acceptance gates.

```bash
tmux load-buffer -b omxtask <file>; tmux paste-buffer -b omxtask -t <pane>
printf '\r' > <submit>; tmux load-buffer -b omxsubmit <submit>; tmux paste-buffer -b omxsubmit -t <pane>
```

Check the pane's cwd first — if the leader is not sitting in the intended worktree, "this
repository" points somewhere else and you must name the path. Confirm delivery with
`tmux capture-pane -p -t <pane> | grep -n .`; plain `tail` on a tall pane returns blank lines,
and the composer placeholder does not mean the paste vanished. A double paste is cleared with
`C-u` — never `Esc`, which interrupts the running turn.

## One tmux window, readable

Every agent pane belongs in the single window the user watches: `join-pane`, not `link-window`.
Moving a pane mid-task is safe — the process keeps its pty. The `omx-…` session disappears when
its last pane leaves; that is expected.

The watchdog pane runs `codex-tmux-watchdog --watch`; it also lives on its own in the
detached `codex-watchdog` session, which the user opens read-only with `Super+F9`.

Column layouts wreck line-oriented output, so give every pane full width:

```bash
tmux select-layout -t <window> even-vertical
tmux resize-pane -t <hud-pane> -y 3
tmux resize-pane -t <watchdog-pane> -y 22
```

Kill HUD panes from previous runs — a live HUD names repo, branch and mode
(`ralph:1/10 | turns:1`); a dead one says `No active modes.`

## Watch and receive

A living pane is not evidence of work, and neither is a rising `completed` count:

```bash
git -C <worktree> log --oneline <base>..HEAD
git -C <worktree> status --porcelain
```

A leader that has been "Working" for a long stretch with no commits is stuck — read its pane,
then re-deliver the scope rather than waiting.

Owner rule 2026-08-24: watch the run **every minute**, workers included. Arm the Monitor tool with
`omx-watch <worktree> [session]` (`~/.local/bin/omx-watch`, emits only changes): leader phase,
commits and dirty files, each worker pane's phase, `HUNG?` after `HANG_MIN` (3) minutes without new
pane output while a pane claims to work, `SUBAGENTS` when the leader waits for its native agents
longer than 10 minutes, `STOPPED-DIRTY` when the leader idles on uncommitted work. Pane text is the
only signal — treat `HUNG?` as a prompt to read the pane, not as proof.

When receiving, re-run the gates the order named **from the worktree or a clean clone**, never
from the live checkout, and quote the counts you saw. Then check the scope against the order:
only the named files, no `node_modules` symlink, no live state directory touched. A migration
file in the branch is not a migration in the live database — check migration status against the
real database before any restart, or the next restart becomes an outage days later.

Merging, building the served artifact, restarting services and pushing are yours, not the
worker's — keep them out of the order. When the environment blocks one, hand the user the exact
command instead of routing around it.

After accept or refuse, signal the owner: `ntfy-push "[OMX] <order-slug>: accepted|refused"
"<one line: gates + commit sha>"` — signals only, no sensitive content.

## Signals you will actually meet

| Signal | What it means | What to do |
|---|---|---|
| `detached launch safety failure during post-release-attach` | only the attach failed | check `tmux list-sessions`; the leader is probably running |
| `PROVENANCE_DENIED` / `foreign-cwd` | stale repo-local session pointer | shutdown, move the pointer aside, relaunch |
| `session.json is present but unusable` | dead state from a previous run | move `session.json` and `run-state.json` aside; `omx cleanup` ignores them |
| `leader_session_conflict` | another leader holds the lock | find and close the live session, do not duplicate |
| `restored_hud_cleanup_debt_unresolved:%N` | orphaned HUD pane blocks shutdown | `tmux kill-pane -t %N`, retry shutdown |
| Worker reports "completed", no commits | the leader's own task counter | verify with `git log`; re-deliver the scope |
| Codex draws in 80x24 inside a full-size pane | the OMX wrapper spawns codex without a controlling tty, so tmux's SIGWINCH never reaches it | `kill -WINCH $(pgrep -x codex)` — redraw only, nothing is interrupted |
