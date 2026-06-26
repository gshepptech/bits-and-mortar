---
description: One-shot bypass of bob strict gates (grounding + critic) for the next single turn
---

The user wants to bypass the bob strict gates (the zero-tool-call grounding audit and the pre-Stop critic-agent gate) for the next single turn only. After that turn the bypass auto-consumes and strict mode resumes. The uncertainty scanner and citation verifier are NOT bypassed — only the strict layers.

Run exactly this Bash command:

```
mkdir -p ~/.claude && : > ~/.claude/.bob-trust-me && echo "bob strict-mode: TRUST-ME — next turn skips grounding + critic gates, then auto-reverts. (uncertainty scanner + citation verifier still on)"
```

After it succeeds, reply to the user with one short line confirming the next turn bypasses the strict gates and that they resume automatically afterward. Do not add anything else.
