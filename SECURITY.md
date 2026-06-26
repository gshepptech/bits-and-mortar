# Security Policy

## Reporting a vulnerability

If you discover a security issue in Bits & Mortar — a plugin that executes
unintended commands, a hook that leaks data, an injection in a workflow script,
or anything else with a security impact — please report it privately.

**Preferred:** open a [GitHub Security Advisory](https://github.com/gshepptech/bits-and-mortar/security/advisories/new)
(Security → Advisories → *Report a vulnerability*).

**Alternative:** email **gshepptech@gmail.com** with the details.

Please do **not** open a public issue for a vulnerability before it has been
addressed.

When reporting, include where possible:

- The plugin and file involved
- A description of the impact
- Steps to reproduce (a minimal repro is ideal)
- Any suggested remediation

## What to expect

- Acknowledgement of your report as soon as it is triaged.
- An assessment and, where warranted, a fix released on `main`.
- Credit in the release notes if you'd like it (and only if you'd like it).

## Scope notes

These plugins run inside Claude Code and can drive shell commands, file edits,
browsers (Tess/Playwright), and remote systems (Gus). Treat that capability the
way you would any developer tool: review what a plugin does before granting it
permissions, and report anything that acts outside its stated remit.
