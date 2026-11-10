# claude-code-skills

Claude Code skills from my own working setup: a lead Claude session that plans and verifies,
subagents that read, and OMX (oh-my-codex) workers that write the code.

| Skill | What it does |
|---|---|
| [`claude-team`](skills/claude-team/SKILL.md) | How the lead session works with its subagents: roles, models, caps, the six-part brief, and how to verify what comes back. |
| [`omx-delivery`](skills/omx-delivery/SKILL.md) | Hands a task to an OMX/Codex worker: lane choice, a committed order file, launch in its own git worktree, tmux handover, receiving the branch on re-run gates. |
| [`drift-check`](skills/drift-check/SKILL.md) | Narrates what a diff actually does, step by step, and marks every place it drifted from the owner's latest stated intent. |
| [`reload`](skills/reload/SKILL.md) | Re-reads CLAUDE.md, AGENTS.md, the memory index and the current order mid-session, then restates the rules that apply now. |
| [`polszczyzna-kontrolowana`](skills/polszczyzna-kontrolowana/SKILL.md) | Controlled Polish (PK): 32 numbered rules that leave each Polish sentence one meaning — fixed senses for „lub” and „albo”, MUSI / POWINIEN / MOŻE keywords, subject–verb–object order, explicit interval bounds, ISO dates. Three modes: write, rewrite, audit. |

The skills are written for my environment (paths, tools, dates of owner rules). Adapt them
before use.

## Install

```sh
git clone https://github.com/maciejszulia/claude-code-skills.git
ln -s "$PWD/claude-code-skills/skills/drift-check" ~/.claude/skills/drift-check
```

Repeat the link for each skill you want. See also
[tractatus-skills](https://github.com/maciejszulia/tractatus-skills).
