---
description: Show the current bob methodical-mode and citation-verifier state
---

The user wants to see the bob state values: methodical-mode (the UserPromptSubmit preamble injection), citation-verifier (the Stop hook), and fable-mode (the completion gate).

Run exactly this Bash command:

```
methodical="on"; [ -f ~/.claude/.bob-state ] && methodical=$(cat ~/.claude/.bob-state | tr -d '[:space:]'); citations="default"; [ -f ~/.claude/.bob-citations-mode ] && citations=$(cat ~/.claude/.bob-citations-mode | tr -d '[:space:]'); fable="default"; [ -f ~/.claude/.bob-fable-mode ] && fable=$(cat ~/.claude/.bob-fable-mode | tr -d '[:space:]'); echo "bob methodical-mode: ${methodical}"; echo "bob citation-verifier: ${citations}"; echo "bob fable-mode: ${fable}"
```

After it succeeds, reply to the user with three short lines:

- methodical-mode: explain the value
  - `on` — methodical preamble fires every turn (default)
  - `off` — silenced for the session; `/bob:on` re-enables
  - `casual` — next turn skips, then auto-reverts to on
- citation-verifier: explain the value
  - `default` — Stop hook blocks responses with unverified file:line citations (default)
  - `off` — hook disabled; `/bob:citations-on` re-enables
- fable-mode: explain the value
  - `default` — Stop hook blocks responses that end by promising work without doing it (default)
  - `off` — gate disabled; `/bob:fable-on` re-enables

Keep it short — one line per state. Do not add anything else.
