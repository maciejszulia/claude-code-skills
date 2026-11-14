#!/usr/bin/env python3
"""Render the README diagrams as SVG. Standard library only.

Usage: python3 tools/render_diagrams.py [output_dir]   (default: docs/diagrams)

House rules, enforced by assertions on every run:
- every node has at least one edge (no floating nodes);
- every edge segment is horizontal or vertical (no diagonals, no curves);
- one font family; every text line fits inside its node.
"""
import os
import sys
from xml.sax.saxutils import escape

W, MARGIN, COL_GAP, ROW_GAP = 960, 16, 24, 30
FONT = "'JetBrains Mono', ui-monospace, Menlo, Consolas, 'DejaVu Sans Mono', monospace"
SIZE, LINE_H, PAD = 12.5, 17, 8
CHAR_W = SIZE * 0.6  # advance width of a monospace glyph
TITLE_SIZE, TITLE_LINE_H = 15, 21
INK, RED, GREY = "#111111", "#c8102e", "#f2f2f2"


def node(nid, col, row, lines, kind="plain", rows=1, head=1):
    """head = number of leading lines that form the node's name (drawn bold)."""
    return {"id": nid, "col": col, "row": row, "lines": lines, "kind": kind, "rows": rows, "head": head}


# Each diagram: title lines (the finding), column count, nodes, edges (from, to).
DIAGRAMS = {
    "overview": {
        "title": ["One lead session plans and verifies. Subagents read, workers write the code,",
                  "hooks keep the memory. Each skill covers one stage of that loop."],
        "cols": 5,
        "nodes": [
            node("s0", 0, 0, ["Context", "memory and rules"], "stage"),
            node("s1", 1, 0, ["Understand", "what is wanted"], "stage"),
            node("s2", 2, 0, ["Delegate", "reading and coding"], "stage"),
            node("s3", 3, 0, ["Receive", "check the result"], "stage"),
            node("s4", 4, 0, ["Report", "text people act on"], "stage"),
            node("mem", 0, 1, ["sb-mem", "journal of every", "session, recalled", "at the next start"], "skill"),
            node("reload", 0, 2, ["reload", "rules back in front", "in a long session"], "skill"),
            node("sense", 1, 1, ["tractatus-sense", "truth-conditions", "of the request"], "skill"),
            node("team", 2, 1, ["claude-team", "subagents read,", "verify and draft"], "skill"),
            node("omx", 2, 2, ["omx-delivery", "a Codex worker", "writes the code"], "skill"),
            node("drift", 3, 1, ["drift-check", "the diff against", "the stated intent"], "skill"),
            node("verify", 3, 2, ["tractatus-verify", "the claim against", "reality"], "skill"),
            node("pk", 4, 1, ["polszczyzna-", "kontrolowana", "one meaning", "per sentence"], "skill", head=2),
        ],
        "edges": [("s0", "s1"), ("s1", "s2"), ("s2", "s3"), ("s3", "s4"),
                  ("s0", "mem"), ("mem", "reload"), ("s1", "sense"), ("s2", "team"), ("team", "omx"),
                  ("s3", "drift"), ("drift", "verify"), ("s4", "pk")],
    },
    "sb-mem": {
        "title": ["Hooks write every prompt, answer, file write and commit to plain Markdown pages.",
                  "The next session starts with those pages; the skill searches them."],
        "cols": 4,
        "nodes": [
            node("events", 0, 0, ["Claude Code events", "prompt, answer,", "Write, Edit,", "git commit, git push"]),
            node("writer", 1, 0, ["dziennik.py (hook)", "one line per event;", "secrets, e-mails and", "phone numbers cut"]),
            node("end", 0, 1, ["Session end", "at least 3 new lines", "in the journal"]),
            node("sum", 1, 1, ["sb-summarize.py (hook)", "one-line summary", "by a small model,", "detached process"]),
            node("pages", 2, 0, ["SilverBullet space", "plain Markdown:", "dziennik/<date>.md", "sessions.md", "handoffs/",
                                 "papercuts.md", "decisions/", "runbooks/"], "accent", rows=2),
            node("recall", 3, 0, ["sb-recall.py (hook)", "session start: cards", "of the last 3 days;", "before Read: lines",
                                  "about that file"]),
            node("skill", 3, 1, ["sb-mem (skill)", "search, timeline,", "save: rg and sed", "are the engine"], "skill"),
        ],
        "edges": [("events", "writer"), ("writer", "pages"), ("end", "sum"), ("sum", "pages"),
                  ("pages", "recall"), ("pages", "skill")],
    },
    "claude-team": {
        "title": ["The lead decides and verifies. Subagents only read, check and draft,",
                  "and what they return is a claim until the lead has opened it."],
        "cols": 5,
        "nodes": [
            node("lead", 0, 0, ["Lead session", "splits the task,", "0 agents for a few", "tool calls"]),
            node("caps", 0, 1, ["Caps", "at most 5 subagents,", "2 is the optimum"]),
            node("brief", 1, 0, ["Brief, six parts", "scope, paths,", "exact commands,", "output shape,", "forbidden actions,",
                                 "scratchpad"], rows=2),
            node("reader", 2, 0, ["Reader", "one big read,", "writes nothing"]),
            node("worker", 2, 1, ["Worker", "one bounded task,", "never pushes"]),
            node("found", 3, 0, ["Findings", "ranked, each with", "file:line, plus an", "Unverified section"], rows=2),
            node("check", 4, 0, ["Lead verifies", "opens one file:line", "per finding, re-runs", "every count"], "accent"),
            node("report", 4, 1, ["Report", "which agent found", "what, with its model"]),
        ],
        "edges": [("caps", "lead"), ("lead", "brief"), ("brief", "reader"), ("brief", "worker"),
                  ("reader", "found"), ("worker", "found"), ("found", "check"), ("check", "report")],
    },
    "omx-delivery": {
        "title": ["The order is a committed file, the worker gets one sentence,",
                  "and the lead re-runs the gates before accepting the branch."],
        "cols": 4,
        "nodes": [
            node("order", 0, 0, ["Order file", "docs/orders/<slug>.md", "problem, outcome, gates,", "forbidden paths;",
                                 "committed before launch"]),
            node("launch", 1, 0, ["Launch", "omx --worktree=<name>", "Codex leader in its own", "git worktree, in tmux"]),
            node("hand", 2, 0, ["Hand over", "one sentence that", "points at the order file"]),
            node("watch", 3, 0, ["Watch", "git log and git status", "of the worktree,", "every minute"]),
            node("gates", 0, 1, ["Receive", "re-run the named gates", "from the worktree,", "quote the counts"], "accent"),
            node("scope", 1, 1, ["Scope check", "only the named files,", "no live state touched"]),
            node("accept", 2, 1, ["Accept or refuse", "merge, build and deploy", "stay with the lead"]),
        ],
        "edges": [("order", "launch"), ("launch", "hand"), ("hand", "watch"), ("watch", "gates"),
                  ("gates", "scope"), ("scope", "accept")],
    },
    "drift-check": {
        "title": ["The change is told as a story in run-time order.",
                  "Every step that departs from the owner's latest stated intent is bold."],
        "cols": 4,
        "nodes": [
            node("intent", 0, 0, ["Intent", "the owner's latest", "statement, quoted", "in one line"]),
            node("diff", 1, 0, ["Diff", "what actually exists:", "git diff base...HEAD,", "read end to end"]),
            node("story", 2, 0, ["Narrate", "numbered steps in", "run-time order, each", "with its file:line"]),
            node("bold", 3, 0, ["Mark the drift", "bold where the change", "adds, skips or does it", "differently"], "accent"),
            node("list", 3, 1, ["List \"Drift\"", "one line per item and", "one question each:", "keep, revert or change"]),
        ],
        "edges": [("intent", "diff"), ("diff", "story"), ("story", "bold"), ("bold", "list")],
    },
    "reload": {
        "title": ["Long contexts dilute instructions that sit far from the end.",
                  "reload puts the rules for the current task back in front."],
        "cols": 4,
        "nodes": [
            node("trig", 0, 0, ["Trigger", "/reload, or the first", "turn after /compact"]),
            node("read", 1, 0, ["Re-read, in order", "global CLAUDE.md,", "project CLAUDE.md and", "AGENTS.md, MEMORY.md,",
                                "the current order"]),
            node("state", 2, 0, ["Restate", "at most five lines:", "only the rules that", "govern this task"], "accent"),
            node("go", 3, 0, ["Continue", "from where the work", "stopped; verified work", "is not redone"]),
        ],
        "edges": [("trig", "read"), ("read", "state"), ("state", "go")],
    },
    "polszczyzna-kontrolowana": {
        "title": ["32 numbered rules close the places where Polish grammar leaves the reader a choice.",
                  "A missing fact is marked, never guessed."],
        "cols": 4,
        "nodes": [
            node("src", 0, 0, ["Source", "a request or a text", "that people act on"]),
            node("mode", 1, 0, ["Mode", "write, rewrite", "or check"]),
            node("rules", 2, 0, ["Rules A to E", "words, sentence, logic,", "numbers and time,", "structure;",
                                 "module F: sources"]),
            node("control", 3, 0, ["Control, 7 steps", "word count by script,", "banned words, doer,", "numbers, dates, terms,",
                                   "two-meanings test"], "accent"),
            node("out", 3, 1, ["Output", "text in PK and the table", "\"Decisions and gaps\""]),
        ],
        "edges": [("src", "mode"), ("mode", "rules"), ("rules", "control"), ("control", "out")],
    },
    "tractatus-sense": {
        "title": ["A request is safe only when every result that satisfies its words is wanted:",
                  "P is a subset of C. The skill narrows P before the work starts."],
        "cols": 4,
        "nodes": [
            node("req", 0, 0, ["Request", "the words, as given"]),
            node("truth", 1, 0, ["Truth-conditions", "elementary propositions,", "each answered yes or no", "by looking"]),
            node("signs", 2, 0, ["Split the signs", "words that signify", "in two ways, settled", "from repo and memory"]),
            node("pc", 3, 0, ["Find P \\ C", "results the words allow", "and the owner would", "reject"], "accent"),
            node("ask", 3, 1, ["Narrow or ask", "negative conditions;", "one question per", "open sign"]),
        ],
        "edges": [("req", "truth"), ("truth", "signs"), ("signs", "pc"), ("pc", "ask")],
    },
    "tractatus-verify": {
        "title": ["\"Done\" is a conjunction. Each part is compared with reality,",
                  "and a part that was not compared is reported as unverified."],
        "cols": 4,
        "nodes": [
            node("claim", 0, 0, ["Claim", "done, fixed,", "deployed, sent"]),
            node("split", 1, 0, ["Elementary propositions", "one observable state each"]),
            node("cmp", 2, 0, ["Compare with reality", "a command, a fetch,", "a read of the live", "location"], "accent"),
            node("table", 3, 0, ["Truth table", "T, F or ? with the", "evidence for each row"]),
            node("say", 3, 1, ["Verdict", "\"done\" only when every", "row is T; ? stays", "unverified"]),
        ],
        "edges": [("claim", "split"), ("split", "cmp"), ("cmp", "table"), ("table", "say")],
    },
}


def layout(d):
    """Return ({id: (x, y, w, h)}, total_height). Row height = tallest single-row node in that row."""
    cols = d["cols"]
    col_w = (W - 2 * MARGIN - (cols - 1) * COL_GAP) / cols
    n_rows = max(n["row"] + n["rows"] for n in d["nodes"])
    row_h = [0.0] * n_rows
    for n in d["nodes"]:
        if n["rows"] == 1:
            row_h[n["row"]] = max(row_h[n["row"]], 2 * PAD + len(n["lines"]) * LINE_H)
    for n in d["nodes"]:  # a spanning node may need more room than its rows offer
        if n["rows"] > 1:
            need = 2 * PAD + len(n["lines"]) * LINE_H
            have = sum(row_h[n["row"]:n["row"] + n["rows"]]) + (n["rows"] - 1) * ROW_GAP
            if need > have:
                row_h[n["row"] + n["rows"] - 1] += need - have
    top = MARGIN + len(d["title"]) * TITLE_LINE_H + 14
    row_y, y = [], top
    for h in row_h:
        row_y.append(y)
        y += h + ROW_GAP
    boxes = {}
    for n in d["nodes"]:
        h = sum(row_h[n["row"]:n["row"] + n["rows"]]) + (n["rows"] - 1) * ROW_GAP
        boxes[n["id"]] = (MARGIN + n["col"] * (col_w + COL_GAP), row_y[n["row"]], col_w, h)
    return boxes, y - ROW_GAP + MARGIN


def route(a, b, na, nb):
    """Orthogonal polyline from box a to box b, as a list of points."""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    if na["col"] == nb["col"]:  # same column: straight down or up
        x = ax + aw / 2
        return [(x, ay + ah), (x, by)] if by > ay else [(x, ay), (x, by + bh)]
    if nb["col"] > na["col"]:  # left to right
        y = (ay + ah / 2) if na["rows"] <= nb["rows"] else (by + bh / 2)
        if ay <= y <= ay + ah and by <= y <= by + bh:
            return [(ax + aw, y), (bx, y)]
        mid = ax + aw + COL_GAP / 2
        return [(ax + aw, ay + ah / 2), (mid, ay + ah / 2), (mid, by + bh / 2), (bx, by + bh / 2)]
    # wrap to an earlier column in a lower row: down, left through the row gap, down
    mid = ay + ah + ROW_GAP / 2
    return [(ax + aw / 2, ay + ah), (ax + aw / 2, mid), (bx + bw / 2, mid), (bx + bw / 2, by)]


def render(name, d):
    boxes, height = layout(d)
    by_id = {n["id"]: n for n in d["nodes"]}
    linked = {i for e in d["edges"] for i in e}
    assert linked == set(by_id), f"{name}: floating or unknown nodes {linked ^ set(by_id)}"
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height:g}" width="{W}" '
           f'font-family="{FONT}" font-size="{SIZE}" role="img" aria-label="{escape(" ".join(d["title"]), {chr(34): "&quot;"})}">',
           f'<rect width="{W}" height="{height:g}" fill="#ffffff"/>',
           f'<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
           f'<path d="M0,0 L8,4 L0,8 z" fill="{INK}"/></marker></defs>']
    for i, line in enumerate(d["title"]):
        assert len(line) * TITLE_SIZE * 0.6 <= W - 2 * MARGIN, f"{name}: title line too long: {line}"
        out.append(f'<text x="{MARGIN}" y="{MARGIN + (i + 1) * TITLE_LINE_H - 5}" font-size="{TITLE_SIZE}" '
                   f'font-weight="bold" fill="{INK}">{escape(line)}</text>')
    for src, dst in d["edges"]:
        pts = route(boxes[src], boxes[dst], by_id[src], by_id[dst])
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            assert x1 == x2 or y1 == y2, f"{name}: diagonal segment {src}->{dst}"
        out.append(f'<polyline points="{" ".join(f"{x:g},{y:g}" for x, y in pts)}" fill="none" stroke="{INK}" '
                   f'stroke-width="1.5" marker-end="url(#arrow)"/>')
    for n in d["nodes"]:
        x, y, w, h = boxes[n["id"]]
        fill = GREY if n["kind"] == "stage" else "#ffffff"
        stroke, sw = (RED, 2) if n["kind"] == "accent" else (INK, 1.5)
        out.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        ty = y + (h - len(n["lines"]) * LINE_H) / 2 + LINE_H - 4
        for i, line in enumerate(n["lines"]):
            assert len(line) * CHAR_W <= w - 2 * PAD, f"{name}/{n['id']}: line does not fit: {line}"
            head = i < n["head"]
            colour = RED if head and n["kind"] in ("skill", "accent") else INK
            weight = ' font-weight="bold"' if head else ""
            out.append(f'<text x="{x + PAD:g}" y="{ty + i * LINE_H:g}" fill="{colour}"{weight}>{escape(line)}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "docs", "diagrams")
    os.makedirs(out_dir, exist_ok=True)
    for name, d in DIAGRAMS.items():
        with open(os.path.join(out_dir, name + ".svg"), "w", encoding="utf-8") as f:
            f.write(render(name, d))
    print(f"{len(DIAGRAMS)} diagrams written to {os.path.normpath(out_dir)}")


if __name__ == "__main__":
    main()
