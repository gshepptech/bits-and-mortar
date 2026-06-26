---
description: Disable the bob Stop hook citation verifier
---

The user wants to disable the citation-verifier Stop hook. While off, the hook short-circuits and never blocks responses regardless of citation accuracy.

Run exactly this Bash command:

```
mkdir -p ~/.claude && echo off > ~/.claude/.bob-citations-mode && echo "bob citation-verifier: OFF. Responses with unverified file:line citations will not be blocked. Run /bob:citations-on to re-enable."
```

After it succeeds, reply to the user with one short line confirming the citation hook is off. Do not add anything else.
