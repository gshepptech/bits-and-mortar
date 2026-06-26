---
description: "Resume an interrupted Gus run from .gus/runs/<run-id>/"
argument-hint: "<run-id>"
allowed-tools: ["Bash(cat:*)", "Bash(ls:*)", "Bash(test:*)", "Bash(date:*)", "Bash(head:*)", "Bash(tail:*)", "Read", "Write", "Edit", "Glob", "Grep", "Agent", "AskUserQuestion"]
---

# Gus Resume

Resume an interrupted Gus run from where it left off.

```
RUN_ID="$ARGUMENTS"
```

If `$ARGUMENTS` is empty, list available runs from `.gus/runs/` (filter to ones with `state.json.status != "completed"`) and ask the user to pick one.

## Steps

1. Verify the run exists:

```bash
test -d ".gus/runs/$RUN_ID" || { echo "No such run: $RUN_ID"; exit 1; }
```

2. Read `.gus/runs/$RUN_ID/state.json`. Inspect `status` and `phase`.

3. Tell the user what state the run is in:

```
Run <RUN_ID>:
  status: <status>
  phase: <phase>
  intent: <intent>
  last activity: <last journal entry timestamp>
```

4. Branch on `phase`:

   - `dispatcher` — restart from PHASE 1 of `/gus:do`. Treat as new run with same intent.
   - `recon` — re-run recon (PHASE 2). Brief may exist partial; recon will overwrite or extend.
   - `decide_checkpoint` / `plan_approval` — re-render `plan.md` if it exists and re-prompt the user (PHASE 4 from `/gus:do`).
   - `builder_execute` — re-spawn builder in last known mode with existing brief/plan/reflections/journal as inputs.
   - `dual_verification` — re-spawn auditor + fresh-eyes (PHASE 7 from `/gus:do`).
   - `debrief` — read all verdicts and render debrief (PHASE 8 from `/gus:do`).
   - `completed` — tell user the run is already done, point them at `.gus/runs/<RUN_ID>/`.
   - `cancelled_at_plan` — tell user the run was cancelled, offer to restart with `/gus:do`.

5. Update `state.json` with `resumed_at: "<ISO timestamp>"` before proceeding.

6. Read the relevant phase logic from `commands/do.md` and follow it from that phase forward. **You do not have to re-execute earlier phases** — trust the on-disk state.

## Rules

- **Don't lose work.** If existing files (`brief.md`, `plan.md`, `journal.md`) are present, treat them as authoritative. Append, don't overwrite, unless re-running the producing phase.
- **Confirm with user before re-running expensive phases.** Recon takes minutes; the builder can take much longer. If you're about to re-run something the user might prefer to skip, ask via `AskUserQuestion`.
- **State.json is the source of truth.** Trust it over your own inference.
