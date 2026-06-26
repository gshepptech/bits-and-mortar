---
description: Disable the bob Fable-mode completion gate (see-it-through enforcement)
---

The user wants to disable the bob Fable-mode completion gate (the Stop-hook check that blocks promise-without-action endings).

Run exactly this Bash command:

```
mkdir -p ~/.claude && echo off > ~/.claude/.bob-fable-mode && echo "bob fable-mode: OFF for this session. Run /bob:fable-on to re-enable."
```

After it succeeds, reply to the user with one short line confirming Fable-mode is off and noting that `/bob:fable-on` re-enables it. Do not add anything else.
