---
name: claude-team
description: How Claude (Fable 5.1, effort high; xhigh/max per task) works with its own subagents on AgroCamping and owner projects — the two team agents (reader-opus5 on Opus 5 1M xhigh, worker-opus48 on Opus 4.8 xhigh), the owner's caps (at most 5 subagents, 2 is the optimum, 0 when a few tool calls do it), how to brief, how to verify what comes back, and where OMX (writes the code) begins; the dsh/Ox review lane was retired 2026-08-28 (independent review = codex exec review + Claude subagents). Use whenever you are about to call the Agent tool, plan a parallel read or verification, or the owner says "use subagents", "team", "zespół", "subagenty".
---

# claude-team

Owner rule 2026-08-24: **Claude runs at most 5 subagents, optimally 2** (the unlimited Ox alpha fleet
existed 22–27.08 and was retired 2026-08-28 per decision Z-2026.08.22 20:45; owner 27.08: "użyj floty
10 agentów" / "20 agentów" is an explicit per-task override — then use Workflow, not the Agent tool). This supersedes the 19.08 "no subagents unless asked" — the verification duty and
the cost quote from that rule stay.

## Roles

| Role | Who | Model / effort | Does | Never |
|---|---|---|---|---|
| Lead | Claude Code | Fable 5.1, high (xhigh: receiving hard branches, planning big orders; max: only when xhigh failed) | decides, splits, briefs, verifies, integrates, reports | delegates the final judgement |
| Reader | `reader-opus5` | `opus[1m]`, xhigh | one big read: repo audit, handoff vs code+git, transcript, chronicle | writes anything |
| Worker | `worker-opus48` | `claude-opus-4-8`, xhigh | one bounded task: reproduce a finding, run gates in a worktree, draft a section, targeted search | pushes, merges, nests agents, edits app code unnamed by the lead |
| Reader (Fable) | `reader-fable-high` | `claude-fable-5-1`, high | same as Reader when the owner asks for a Fable fleet (05.09.2026): branch review, handoff vs code, audit | writes anything |
| Worker (Fable) | `worker-fable-high` | `claude-fable-5-1`, high | same as Worker on Fable 5.1 high; use when the owner says „flota fable high” | pushes, merges, nests agents, edits app code |
| Reviewer | `codex exec review --base dev` + a Claude subagent with a review persona | sol / `opus` | findings with file:line, an `## Unverified` section, no patches | commits |
| Coder | OMX (Codex) | `gpt-5.6-sol` | product code from `docs/orders/*.md` in a worktree | receives itself |

Definitions live in `~/.claude/agents/team/` (copy to `ms-ai-workflow/config/shared` when syncing).
`model:` accepts aliases, `opus[1m]` style 1M variants and full IDs; `effort:` overrides the session
level per agent (verified in Claude Code 2.1.241 docs + binary).

## Caps and when to spawn

- 0 agents when the answer is a handful of tool calls — read it yourself.
- 1 reader when the material is bigger than you want in your own context (a whole repo, a day's
  git history, a 500-line handoff to verify).
- 2 workers is the optimum: disjoint scopes, one message, run in parallel. 3–5 only for a
  genuinely disjoint sweep (two repos × two lenses, a verify panel) — say why in one line.
- More than 2 → quote the cost first (Fable-max reviewers cost 10–15 USD each on 19.08; Opus is
  cheaper, unmeasured — write the number down after the run). Floor: a spawn with zero tool
  calls already costs ~25k tokens of boot context (measured 24.08) — never spawn for a one-liner.
- Workflows (`ultracode`) only when the owner says "use a workflow".

## Brief (every agent gets all six)

1. Scope: the one question or task, in one sentence. 2. Paths: repo, worktree, files — a detached
worktree for reads of a repo with secrets or a live DB. 3. Exact commands, in order. 4. Output
shape: ranked list / table / counts; "Unverified" section mandatory. 5. Forbidden: push, merge,
deploy, `git add -A`, live checkouts, secrets in output. 6. Scratchpad path.
Agents return raw data — the owner-facing text is yours.

## Verify before you use it

- Spot-check at least one `file:line` per finding you carry into a report or an order; open it.
- Re-run any count you quote (tests, commits, lines) — an agent's "208/208" is a claim.
- A finding becomes an OMX order only after you reproduced it or Ox confirmed it independently.
- Sign the report: which agent found what, with its model (owner rule: model disclosure).

## Boundaries with OMX

OMX writes (`omx-delivery` skill); Claude's agents read, verify, gate and draft; independent review is
`codex exec review --base dev` plus, when the owner asks for a fleet, a Workflow of read-only Opus agents
(28.08: 10 × Opus 5 max ≈ 2.0 M tokens / 40 min; 20 × Opus 4.8 high ≈ 2.9 M tokens / 32 min). A Claude agent never patches
product code to "save a round trip" — that is an order for OMX.

## Fleets and agency-agents personas (owner 2026-08-29)

Owner 29.08 07:2x: "użyj agency agents do zbudowania tego. rozkaz." and 27.08 "Używaj agency Agents.
Pracuj we flocie." — when the owner orders a fleet ("dobierz sobie dużą flotę", "flota", "użyj N agentów"),
build it with the Workflow tool and give **every role a persona from `~/agency-agents/`**:

| Role | Persona file (source of truth: `~/agency-agents/<division>/`) | How to attach |
|---|---|---|
| planner | `engineering/engineering-multi-agent-systems-architect.md` | prompt prefix, model inherited (Fable 5.1, effort max) |
| coder: UI/server | `engineering/engineering-frontend-developer.md` | `agentType: 'worker-opus48'` + prefix |
| coder: prompts/audit | `engineering/engineering-prompt-engineer.md` | idem |
| coder: data/parsers | `engineering/engineering-data-engineer.md` | idem |
| coder: diagrams/inventory | `engineering/engineering-data-visualization-engineer.md` | idem |
| coder: service/runit | `DevOps Automator` (registered in `~/.claude/agents/`) | `agentType: 'DevOps Automator', model: 'claude-opus-4-8'` |
| integrator | `engineering/engineering-git-workflow-master.md` | worker-opus48 + prefix |
| QA data / privacy / UX / service / inventory | `testing/testing-evidence-collector.md`, `engineering/engineering-privacy-engineer.md`, `testing/testing-accessibility-auditor.md`, `testing/testing-test-automation-engineer.md`, `engineering/engineering-developer-tooling-engineer.md` | `model: 'opus', effort: 'medium'` + prefix |
| judge / acceptance | `Reality Checker` (registered) | `agentType: 'Reality Checker', model: 'opus'` |
| fixer | `engineering/engineering-minimal-change-engineer.md` | worker-opus48 + prefix |
| reviewer | `Code Reviewer` (registered) + ponytail lens in the prompt | `agentType: 'Code Reviewer', model: 'opus'` |

Prefix (verbatim): `PERSONA (owner order): FIRST read <file> and adopt that persona for this whole task — its
identity, standards, checklists and output habits — then execute the order below. State the persona name in
the first line of your report.` Registered persona types are the `name:` field of the file (`Reality Checker`),
not the slug; a freshly copied file is not in the registry until Claude Code restarts — use the prefix path.
`~/.claude/agents/` holds 16 files (3.5 kB of descriptions, limit ~15k tokens) — copy more only for a real role.

Fleet shape that worked (Panel AI, 29.08): plan (1) → coders in their own worktrees on disjoint files (5) →
integrator (1) → QA refuters in parallel with the verdict judge (5+1) → one fixer for all FAILs + re-run of
failed lenses → reviewer. Each coder gets the module contract in the prompt, its own port for tests, and the
rule "kill only the PID you started". Verify models after launch (owner rule 29.08):
`grep -h '"model"' <transcriptDir>/agent-*.meta.json`.

Journal: hook `~/.claude/hooks/dziennik.py` (PostToolUse on Agent|Workflow|Skill|Artifact|Bash) writes one line
per delegation/action to `~/.local/share/silverbullet/space/dziennik/YYYY-MM-DD.md` (owner 29.08: "rób sobie
ciągle notatki co robisz, co sobie zleciłeś — niech to będzie twój hook"). Do not duplicate it by hand.

## Ralph loop, light frameworks, environment (owner 2026-08-29 07:3x)

Owner: "pisz efficient kod /ponytail lite i używaj ralph-skilli. ustawiaj środowisko. updatuj skilla."

- **Ralph loop in a Workflow** (OMX `$ralph` persistence, ported): coder ↔ QA refuter in a loop until PASS, max 3 rounds,
  `log()` per round with the open findings count; never a single fix round when the owner asked for ralph.
    let round = 0, fails = await qa(); while (fails.length && round++ < 3) { await fixer(fails); fails = await qa(fails) }
- **Light frameworks only** for owner panels on localhost: htmx (cdnjs, one `<script>`) for partial refresh and Y/N buttons,
  stdlib `http.server` on the backend, no React/bundlers. Fonts: JetBrains Mono. Style tokens: black/white/red, hard edges.
- **Environment first**: every coder and QA agent gets a one-command environment (`dev-env.sh <key>`: own worktree, own
  `XDG_STATE_HOME`, own port, fixtures, the test commands printed) — agents must not improvise paths or ports.
- **Ponytail lite** for panel code (owner 07:3x); keep the one runnable self-check per module.
- **Owner feedback as data**: when a page shows AI opinions/proposals, store the owner's Y/N in the panel DB — that table is the
  evolution dataset (what to change in memory, skills, CLAUDE.md), not chat history.
- **Restart services by PID file only** — `pkill -f`/`pgrep -f` in the same Bash call as the start line kills the tool shell
  (exit 144; 29.08, twice).
