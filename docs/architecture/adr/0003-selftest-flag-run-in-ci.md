# ADR 0003: A self-check flag per script, run in CI

## Status

Accepted (commit `62c1ebd`).

## Context

The hooks and tools read live files of the owner's machine: session registry, transcripts, usage limits, the SilverBullet space. A test against those files cannot run in CI and could change real data.

## Decision

Each hook and tool script has a `--selftest` flag (`agent-journal.py`: `--self-check`) that builds its input in a temporary folder or with a stand-in binary and asserts the result. GitHub Actions runs the self-checks of the three drift-check scripts, `readme-guard.py`, `lead-takeover.py` and `limit-guard.py` on every push to `main` and on every pull request.

## Consequences

- A test lives in the same file as the code; there is no test framework.
- The self-checks of the other scripts run only by hand.
- `sb-summarize.py --selftest` uses a stand-in `claude` binary, so the real cost log stays clean.

## Evidence

- `.github/workflows/ci.yml`.
- Commits `62c1ebd` "ci: run the selftests of the scripts and hooks on GitHub Actions", `5a9700e`, `b7ba1d6`, `85895ee` (self-checks of the sb-mem hooks).
