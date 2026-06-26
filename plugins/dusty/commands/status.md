---
description: "Show recent Dusty runs and their status"
argument-hint: "[<run-id>]"
allowed-tools: ["Bash(ls:*)", "Bash(cat:*)", "Bash(test:*)", "Bash(date:*)", "Bash(head:*)", "Bash(tail:*)", "Bash(git:*)", "Read", "Glob"]
---

# Dusty Status

```
ARG="$ARGUMENTS"
```

## If ARG is a run ID

Render the full status of that run:

1. Read `.dusty/runs/$ARG/state.json`.
2. Render:

```markdown
**Dusty run <RUN_ID>**

- status: <status>
- phase: <phase>
- mode: <dry-run | apply>
- tracks: <list>
- pre-sweep sha: <sha>
- started: <created_at>
- finished: <completed_at or —>

**Per-track summary:**
| track | candidates | HIGH | MEDIUM | LOW | UNCERTAIN | applied |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | ... |

**Final check results (if applied):**
- Type check: ✓ | ✗
- Tests: ✓ | ✗
- Lint: ✓ | ✗

**Artifacts:** `.dusty/runs/<RUN_ID>/`
```

If the run is in apply phase, also show:
- Commits made in this run (`git log <pre_sweep_sha>..HEAD --oneline`)
- Net diff stats (`git diff --shortstat <pre_sweep_sha>..HEAD`)

## If ARG is empty

List all recent runs:

```markdown
| run id | status | mode | tracks | started |
|---|---|---|---|---|
| dusty-20260512-… | ✓ completed | apply | all | 14:32 |
| dusty-20260511-… | ⏸ inspection_complete | dry-run | all | 09:15 |
| ... | ... | ... | ... | ... |
```

If any have status `inspection_complete`, remind the user they can apply with `/dusty:apply <run-id>`.

## Rules

Read-only. Never modify state.json or anything in `.dusty/runs/`.
