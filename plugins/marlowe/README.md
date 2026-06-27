<div align="center">

<img src="marlowe.svg" alt="Marlowe — the surveyor" width="100%"/>

# Marlowe

**Macro-architecture review — is this shaped right, or accreted?**

[![version](https://img.shields.io/badge/marlowe-v0.1.0-1E88E5?style=flat-square)](.claude-plugin/plugin.json)
[![license](https://img.shields.io/badge/license-Apache--2.0-4C9A2A?style=flat-square)](../../LICENSE)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-8E44AD?style=flat-square)](https://docs.claude.com/en/docs/claude-code)

</div>

> The senior-engineer design-cohesion critique — not bug-hunting, not lint. Marlowe reads a codebase the way a gumshoe reads a crime scene, deduces the real design problem from the detail that's out of place, and hands you an ordered reshaping plan. Report only — it never edits code.

---

## ✨ What It Does

A naive "review the architecture" pass produces plausible-sounding opinions you can't act on. Marlowe runs a deterministic Workflow engine that builds a grounded structural map of the target, runs **8 blind design lenses** over it, adversarially cross-examines every candidate finding, and synthesizes a per-subsystem **deliberate / mixed / accreted** verdict with `file:line` evidence and a concrete, highest-leverage-first reshaping plan.

It answers the questions a naive pass can't:

> Is this shaped right, or thrown together? Why are there N functions doing almost-the-same thing? Why so many packages? Where could this logic have been shared? Does the architecture flow, or fight you? Is it deliberate or accreted?

Its working principle: **the code is the only witness that doesn't lie.** Marlowe never takes a comment at its word — it reads the actual code and traces the call sites. An empty result is honest: a well-shaped target should produce few or no findings.

---

## 🚀 Install

```bash
claude plugin marketplace add gshepptech/bits-and-mortar
claude plugin install marlowe@bits-and-mortar
```

Marlowe requires the Workflow tool. The `/marlowe:review` command is itself the opt-in:

```
/marlowe:review pkg/auth
```

`<target>` is free-form: a path (`pkg/auth`), a change (`the diff`, `this branch vs main`), a subsystem name, or a description (`the retry logic in the worker`). Omit it and you'll be asked.

---

## 🧩 How It Works

`map → lenses (parallel, blind) → cross-examine (per-finding, adversarial) → critic (re-lens gaps) → synthesize`. Four mechanisms keep it honest:

| Worry | Mechanism |
|---|---|
| It hallucinates / cites things that aren't there | **Grounded map first** — a structural model every finding must anchor to with `file:line` |
| It misses whole areas | **8 blind lenses** — separate agents, each hunting one class of design smell, none seeing the others |
| It reports smells that are actually intentional | **Adversarial cross-examination** — every candidate goes to a skeptic that tries to *refute* it; non-survivors are dropped |
| I have to keep prodding it | **Completeness critic** — a final agent asks "what went unexamined?" and re-lenses the gaps |

### The eight lenses

| # | Lens | Hunts for |
|---|---|---|
| 1 | **Package / module proliferation** | arbitrary boundaries; collapsible modules; a module that's secretly three things |
| 2 | **Missed sharing & reuse** | logic reimplemented instead of shared; a missing seam |
| 3 | **Helper sprawl & abstraction fit** | one-off wrappers that hide nothing; over- or under-abstraction |
| 4 | **Flow & layering** | control/data flow that zigzags; dependencies pointed the wrong way |
| 5 | **Cohesion** | grab-bag modules that do more than one thing |
| 6 | **Naming & structural consistency** | similar things that don't look similar; half-finished migrations |
| 7 | **Accretion markers** | v1/v2 side-by-side, dead flags, vestigial layers — grew without pruning |
| 8 | **Boundary & dependency direction** | public surfaces leaking internals; dependencies that tangle instead of pointing toward stable cores |

### Output

A debrief in chat plus a saved report under `.marlowe/casefiles/`. Per subsystem: a `deliberate | mixed | accreted` verdict and the design story. Per finding: `file:line` evidence and a concrete proposed solution. Then an ordered, highest-leverage-first reshaping plan.

### Commands

| Command | What it does |
|---|---|
| `/marlowe:review [<target>]` | Scope the target, run the 8-lens engine, render the verdict and reshaping plan. Report only — never edits code |
| `/marlowe:help` | Plugin help |

---

## 📄 License

Apache-2.0 — see [LICENSE](../../LICENSE). © 2026 gshepptech
