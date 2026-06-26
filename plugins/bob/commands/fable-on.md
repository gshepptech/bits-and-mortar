---
description: Enable the bob Fable-mode completion gate (see-it-through enforcement)
---

The user wants to enable the bob Fable-mode completion gate: the Stop-hook check that blocks a response which ends by PROMISING first-person work without doing it (no trailing tool call, no clarifying question).

Run exactly this Bash command:

```
mkdir -p ~/.claude && echo default > ~/.claude/.bob-fable-mode && echo "bob fable-mode: ON. Responses that end by promising work instead of doing it will be blocked and bounced back."
```

After it succeeds, reply to the user with one short line confirming Fable-mode is on and noting that `/bob:fable-off` disables it. Do not add anything else.
