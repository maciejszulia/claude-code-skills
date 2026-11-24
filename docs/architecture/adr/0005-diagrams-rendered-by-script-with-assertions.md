# ADR 0005: Diagrams rendered by a script with assertions

## Status

Accepted (commit `94b9363`).

## Context

The README has one diagram per skill. Hand-drawn diagrams drift in style, and the owner's diagram rules forbid floating nodes and diagonal lines.

## Decision

`tools/render_diagrams.py` defines every diagram as data and writes SVG files to `docs/diagrams/`. On every run it asserts that each node has at least one edge, each edge segment is horizontal or vertical, and each text line fits inside its node. It also renders the two diagrams of the tractatus-skills repository.

## Consequences

- A diagram that breaks a rule fails to render.
- The SVG files are generated output committed next to the source; a change of the script needs a re-run and a commit of the SVG files.

## Evidence

- `tools/render_diagrams.py`, docstring "House rules, enforced by assertions on every run".
- `README.md`, section "Diagrams".
- `git ls-files docs/diagrams`: 12 SVG files.
