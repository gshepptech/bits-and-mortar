---
description: Show the Tess plugin commands, skills, and agent
---

The user wants help with the Tess plugin. Reply with exactly this message — verbatim, no additions:

```
Tess — Playwright E2E test authoring + maintenance, driven by Claude

WHAT IT DOES
  Wraps Playwright + Playwright MCP into a slash-command workflow. Claude drives
  a real browser, reads the accessibility tree, writes *.spec.ts files that
  pass, and keeps them passing. Author specs from prompts, generate smoke
  coverage across every route, lock down access control via routes × roles,
  triage failures from trace.zip.

COMMANDS
  /tess:init                  Install Playwright + register MCP + scaffold tests/
  /tess:write <flow>          Claude drives the browser, emits *.spec.ts, runs green
  /tess:crawl [baseURL]       Discover every route → one smoke spec per route
  /tess:matrix                Routes × roles coverage with reused storageState
  /tess:audit [--fix]         Run suite, read trace.zip, triage by root cause
  /tess:record <slug>         Wrap `playwright codegen` for manual recording
  /tess:help                  This message

SKILLS
  tess:author     Selector hygiene, auto-wait discipline, idempotent test design
  tess:diagnose   Trace.zip reading, flaky-test triage, failure taxonomy

SUBAGENT
  tess:spec-writer     Isolated MCP-driven spec authoring. Spawned by /tess:write
                         for multi-step flows. Invoked via Agent tool with
                         subagent_type=tess:spec-writer.

CONFIG
  playwright.config.ts   Scaffolded by /tess:init. baseURL via $BASE_URL env.
  .mcp.json              Playwright MCP entry (headed by default).
  tess.config.json     Roles + login flow for /tess:matrix. Created on first
                         matrix run.
  .auth/                 storageState per role. Gitignored — contains session
                         tokens. Never commit.

TYPICAL FLOW
  1. /tess:init                              (once per project)
  2. /tess:crawl http://localhost:3000       (smoke baseline)
  3. /tess:write "user logs in and adds a todo"   (per-feature specs)
  4. /tess:audit                             (run + triage on each PR)
  5. /tess:matrix                            (when access control matters)

PRINCIPLES
  - getByRole over CSS. Auto-wait over sleep. Idempotent over chained.
  - Observe first, lock assertions second. Especially in /tess:matrix.
  - Trace.zip is the source of truth for failures. Don't guess from messages.
  - Don't commit .auth/.
```

Do not embellish, summarize, or rephrase. The verbatim block IS the help.
