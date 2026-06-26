---
description: Disable bob methodical-mode injection for the rest of this session
---

The user wants to silence the bob UserPromptSubmit hook for the remainder of this session.

Run exactly this Bash command:

```
mkdir -p ~/.claude && echo off > ~/.claude/.bob-state && echo "bob methodical-mode: OFF for this session. Run /bob:on to re-enable."
```

After it succeeds, reply to the user with one short line confirming methodical-mode is off and noting that `/bob:on` re-enables it. Do not add anything else.
