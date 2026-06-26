---
description: "Explain the Mason workflow and available commands"
---

# Mason Help

Please explain the following to the user:

## What is Mason?

**Drew draws it. Mason builds it.**

Mason is an autonomous build-verify-fix loop for Claude Code. Give it Drew's spec; it decomposes the spec into castings with pre-authored teammate prompts, builds in parallel waves, runs multi-stream verification, grinds defects to zero, then assays the result with fresh eyes — all without approval gates.

## How it works

```
F0     RESEARCH   →  F0.5  DECOMPOSE  →  F0.9  VALIDATE  →  F1  CAST
                                                              ↓
                                                            F2  INSPECT  ←──┐
                                                              ↓             │
                                                       defects → F3 GRIND ──┘
                                                              ↓
                                                       clean → F4 ASSAY
                                                              ↓
                                                  F5 TEMPER (optional, --temper)
                                                              ↓
                                                  F5.5 NYQUIST (optional, --nyquist)
                                                              ↓
                                                            F6  DONE
```

### Phases

| Phase | What happens |
|---|---|
| **F0 RESEARCH** | Per-domain researcher agents investigate how to build. Optional `codebase-mapper` extracts conventions + mandatory rules. |
| **F0.5 DECOMPOSE** | Authors the casting manifest AND the complete teammate prompt for each casting, from the spec as source of truth. |
| **F0.9 VALIDATE** | 9-dimension mechanical gate: requirement coverage, completeness, dependency correctness, key links, scope sanity, research integration, prompt fidelity (with `<global_invariants>` and `<mandatory_rules>` propagation), migration coverage, spec structure. |
| **F1 CAST** | Parallel wave-based building. Lead is a router — never re-drafts teammate prompts. |
| **F2 INSPECT** | Up to 7 parallel verification streams (see below). |
| **F3 GRIND** | Every defect becomes a casting-scoped task. Teammates fix, Mason re-verifies. No deferrals. |
| **F4 ASSAY** | 4 fresh-eyes agents read spec FIRST, form expectations, THEN read code. Catches stubs and hollow handlers. |
| **F5 TEMPER** | Optional (`--temper`). Micro-domain stress testing per filesystem domain. |
| **F5.5 NYQUIST** | Optional (`--nyquist`). Generates regression tests for VERIFIED requirements that lack coverage. |
| **F6 DONE** | Shutdown, report, commit. |

### Verification streams (F2 INSPECT)

| Stream | Method | Checks |
|---|---|---|
| **TRACE** | Serena LSP | Upstream wiring: EXISTS → SUBSTANTIVE → WIRED → PLACED |
| **FLOW_TRACE** | Serena LSP | Brownfield only. Downstream wiring: PRODUCED → CONSUMES_UPSTREAM → SUBSTANTIVE → CHAIN_INTACT |
| **PROVE** | Spec-before-code | Every requirement has cited code evidence; stub detection; architectural placement check |
| **RESEARCH_AUDIT** | Research compliance | Code honors every recommendation captured during F0 research |
| **COVERAGE_DIFF** | 1:1 source/dest diff | MIGRATION specs only — every source symbol has a destination |
| **SIGHT** | Playwright | UI renders, buttons work, no console errors |
| **TEST / PROBE** | Test suite + smoke | All tests pass; APIs respond; smoke flows complete end-to-end |

## Drift prevention

Three frozen, byte-identical blocks ride in every casting prompt:

- `<mandatory_rules>` — full CLAUDE.md / AGENTS.md / .cursorrules imperatives
- `<global_invariants>` — cross-cutting spec rules (auth, validation, security, architectural placement)
- `<spec_requirements>` — the casting's specific spec slice (V2) OR `<upstream_anchor>`/`<this_hop>`/`<downstream_contract>` (V3 brownfield)

F0.9 mechanically verifies byte-identical propagation across every casting. The lead at F1/F3 calls `Mill-Spawn-Teammate`, gets the pre-authored prompt back, and passes it to the Agent tool **verbatim** — no re-drafting, no paraphrasing.

## Commands

### `/mason:start <SCOPE> [OPTIONS]`

Start a new build run.

```
/mason:start "user auth"  --spec docs/specs/auth.md
/mason:start "dashboard"  --spec docs/specs/dashboard.md --url http://localhost:3000
/mason:start "api"        --spec docs/specs/api.md --temper --nyquist
```

**Options:**
- `--spec <path>` — Drew's spec to build from (strongly recommended)
- `--url <url>` — base URL for SIGHT (Playwright UI audit)
- `--temper` — enable F5 micro-domain stress testing
- `--nyquist` — enable F5.5 regression test generation
- `--max-cycles <n>` — cap on F2/F3 verify-fix loops
- `--no-ui` — skip SIGHT
- `--output-dir <dir>` — custom run directory (default: `mill-archive/{run}/`)

### `/mason:resume`

Resume an interrupted run. Lists runs by phase + cycle; pick one to continue.

### `/mason:status`

Show current run status — phase, cycle, defects, stream coverage.

### `/mason:stop`

Gracefully stop the active run. Resumable later.

### `/mason:setup`

Install all prerequisites: Mason MCP server, Playwright MCP, Serena MCP, ralph-loop and hookify plugins.

### `/mason:help`

Show this help.

## Prerequisites

Run `/mason:setup` once per machine to install:

- **Mason MCP server** — phase gates, defect tracking, orchestration state
- **Playwright MCP** — browser automation for SIGHT
- **Serena MCP** — LSP wiring for TRACE / FLOW_TRACE
- **ralph-loop plugin** — teammate execution engine
- **hookify plugin** — hook configuration utilities

## Key properties

- **One command, zero approval gates** — fully autonomous from `/mason:start` to F6 DONE
- **Lead never edits code** — delegates everything to teammates (SIGHT/Playwright is the one exception)
- **Plans are prompts** — decompose authors once at F0.5, teammates receive the prompt verbatim
- **Every non-passing verdict is a defect** — no deferrals, no "close enough"
- **Full re-verify after every fix** — no spot-checking
- **Methodical teammate** — tuned for correctness over wall-clock speed (read floor, approach deliberation, blast radius, competing hypotheses)
- **Stall watchdog** — 3+ minute silence triggers a visible warning that forces re-engagement
- **MCP-guided** — `Mill-Next` returns a literal "YOUR NEXT CALL" imperative every step
- **Full audit trail** — every casting prompt, every acceptance, every handoff written to `mill-archive/{run}/`

## Complete workflow

```
1. Drew plans:    /drew:plan "my feature"
2. Mason builds: /mason:start "my feature" --spec docs/specs/my-feature.md
```

Drew draws it. Mason builds it. You ship.
