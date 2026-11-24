# ADR 0002: Python standard library only

## Status

Accepted.

## Context

Hooks are copied into `~/.claude/hooks/` and run by Claude Code with the system `python3`. A hook with a third-party import would need a virtual environment on every machine and could fail on every event.

## Decision

Every Python script and hook in the repository imports only the standard library. Model calls go through the `claude` CLI in a subprocess; HTTP calls use `urllib`.

## Consequences

- A hook works after one `cp`; CI needs no install step.
- Features that a library would give (YAML, HTTP sessions, rich CLI) are written by hand or left out.

## Evidence

- `.github/workflows/ci.yml`: step "Self-checks of the scripts and hooks (standard library only)", no install step.
- Docstrings of `tools/pair-watch/pair.py`, `tools/gitea-middle-remote/gitea_mirror.py`, `tools/second-brain-nightly/nightly.py` and `tools/render_diagrams.py`: "standard library only".
- `README.md`, section "drift-check": "The scripts use the standard library only".
