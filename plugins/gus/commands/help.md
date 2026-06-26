---
description: "Explain the Gus plugin and how to use it"
argument-hint: ""
allowed-tools: []
---

# Gus Help

Render this help text to the user verbatim.

---

# Gus — your general contractor for gnarly problems

Hand Gus a gnarly problem and he owns the outcome end to end. Gus is a single command that gathers context, optionally proposes a plan, then executes against real systems (SSH, infra, code edits, deploys, features), and verifies the outcome by observation — not by inference.

## How to use it

```
/gus:do <whatever you want>
```

The intent is free-form. You don't pick a task type. Gus classifies it.

Examples:

```
/gus:do figure out why staging login is broken since yesterday

/gus:do make sure Shiro can run properly on Azure on RHEL — I want to deploy

/gus:do get the airgap bundle pulling all packages until it works

/gus:do rotate the prod database credentials and update all the services

/gus:do add a /workloads page to the embedded dashboard
```

## Flags

- `--thorough` — doubles depth contract; spawns N=3 builder variants in parallel from the start; runs the auditor twice with different framings.
- `--yolo` — skips the plan-approval checkpoint. **Forbidden against production** (Gus enforces this regardless of flag).
- `--scope=quick|standard` — override scope (default: dispatcher decides).

## What happens

1. **Dispatcher** classifies the intent — initial mode, scope, side-effect surface, whether a plan checkpoint is needed.
2. **Recon** gathers context — codebase, memory, recent git history, targeted web research, the verification surface ("what would prove this is real?"), and an honest assumption ledger. Bounded budget (30 tool calls / 6 min, doubled in thorough mode).
3. **Builder** does the work, switching between modes as the task evolves:
   - `investigating` — forming hypotheses, reading systems
   - `planning` — proposing a path forward
   - `executing` — applying changes to real systems
   - `verifying` — proving the outcome with concrete commands
   - `stuck` — declaring it explicitly rather than thrashing
4. **One checkpoint** (only for side-effecting tasks) — the builder proposes a plan in chat, you approve / revise / cancel.
5. **Auditor** runs after execution — adversarial check, must produce an evidence ledger of commands it actually ran.
6. **Fresh-eyes** runs in parallel with the auditor — blind to everything except the original intent and current state. Catches drift the auditor and builder can't see.
7. **Debrief** in chat — what was done, what changed along the way, what was verified, open follow-ups.

## On stuck

When the builder declares stuck (4 reflections without progress on a step), Gus spawns **N=2-3 parallel builder variants** with deliberately different framings ("treat this as a config issue," "treat as an environment issue," "treat as a permissions issue"). An arbiter synthesizes their findings. This replaces the single-builder-reading-its-own-reflections loop that the research showed degenerates.

## Where state lives

Everything is in `.gus/runs/<run-id>/`:

- `state.json` — phase, status, configuration
- `brief.md` — recon's output
- `plan.md` — the builder's plan (if checkpoint phase ran)
- `journal.md` — append-only log of every significant action
- `reflections.md` — what failures taught the builder
- `verification.md` — the builder's own verification pass
- `auditor-verdict.md` — adversarial verdict with evidence ledger
- `fresh-eyes-verdict.md` — blind drift check with evidence ledger
- `followups.md` — out-of-scope things noticed during the run
- `escalation.md` — only present if the builder got stuck

You don't have to read any of these. Plan and debrief render in chat. The files exist for resume and audit.

## Unattended goal runs

```
/gus:goal <completion condition>
```

`/gus:do` does one task and hands back. `/gus:goal` takes a *completion condition* and runs Gus's builder → auditor → fresh-eyes loop **unattended**, cycle after cycle, until the condition is met — auditor AND fresh-eyes both return `pass` — or a safety cap stops it. No plan checkpoint, no budget questions. You set the finish line and walk away.

```
/gus:goal every test in test/auth passes and `npm run lint` exits 0

/gus:goal the /workloads page renders live pod data, verified in a browser
```

A `Stop` hook (`goal-gate.py`) enforces it — the run cannot end while the goal is unmet. It exits only on **goal met** (auditor + fresh-eyes both pass), **capped** (`--max-cycles`, default 15, or `--max-hours`, default 6), **stuck** (multi-angle retry exhausted), or **blocked** (production side-effects without `--allow-production`).

**Before the first run:** an unattended run can't survive an interactive block, so `/gus:goal` refuses to start unless bob's strict gates are off — run `/bob:strict-off` first if you use the bob plugin.

## Other commands

- `/gus:do <intent>` — one task, end to end, with a plan checkpoint
- `/gus:goal <condition>` — unattended: run until auditor + fresh-eyes both pass
- `/gus:resume <run-id>` — pick up an interrupted run
- `/gus:list` — show recent runs
- `/gus:cancel [<run-id>]` — cancel an active run
- `/gus:help` — this text

## Host registry (optional)

If you have `.gus/hosts.yml` in the project, Gus reads it and uses host tags. Example:

```yaml
hosts:
  staging:
    ssh: ubuntu@staging.example.com
    tags: [dev, azure, rhel]
  prod:
    ssh: deploy@prod.example.com
    tags: [production, azure, rhel]
```

The builder references host tags rather than re-learning hosts every run. Production-tagged hosts force plan approval.

## What Gus is NOT

- Not a feature-builder pipeline (that's mill/blueprint)
- Not a phase planner (that's gsd)

Gus is "I have a problem, go own it."
