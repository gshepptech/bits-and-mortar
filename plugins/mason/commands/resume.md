---
description: "Resume an interrupted Mason run"
allowed-tools: ["Bash(ls:*)", "Bash(cat:*)", "Bash(jq:*)", "AskUserQuestion", "Read", "Write", "Glob", "Grep", "Agent", "TaskCreate", "TaskUpdate", "TaskList", "TaskGet", "TeamCreate", "TeamDelete", "SendMessage", "Edit", "Bash(${CLAUDE_PLUGIN_ROOT}/scripts/mill.sh:*)", "Bash(git:*)", "Bash(go:*)", "Bash(npm:*)", "Bash(npx:*)", "Bash(pnpm:*)", "Bash(make:*)", "Bash(curl:*)"]
hide-from-slash-command-tool: "true"
---

# Mason Resume Command

Resume an interrupted Mason run.

## STEP 1: FIND EXISTING RUNS

Scan for Mason run directories:

```bash
ls -d mill-archive/*/ 2>/dev/null || echo "NO_RUNS"
```

## STEP 2: HANDLE RESULTS

### If NO runs exist:

Tell the user:

> No Mason runs found.
>
> To start a new run:
> ```
> /mason:start "scope" --spec path/to/spec.md
> ```

Then STOP.

### If runs exist:

For each run directory, read `state.json` to extract:
- Run name
- Current phase
- Cycle number
- Spec path
- Created timestamp

Present the list using AskUserQuestion:
- "bold-falcon (phase: INSPECT, cycle: 2, started: 2026-03-20)"
- "swift-anvil (phase: CAST, cycle: 0, started: 2026-03-22)"

## STEP 3: RESUME SELECTED RUN

1. Call `Mill-Init` with `resume: "<run-name>"` to reload state
2. Call `Mill-Context` to get full state
3. Call `Mill-Next` to get the next action
4. Continue the Mason loop from the current phase

Follow the same rules as `/mason:start` — you are the Lead, never edit code, delegate everything.
