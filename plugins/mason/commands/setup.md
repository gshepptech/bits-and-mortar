---
description: "Install Mason MCP server and all prerequisites"
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/setup-prereqs.sh:*)", "AskUserQuestion", "Read", "Write", "Glob"]
hide-from-slash-command-tool: "true"
---

# Mason Setup Command

Install everything needed for Mason to work.

Run the prerequisite installation script:

```!
"${CLAUDE_PLUGIN_ROOT}/scripts/setup-prereqs.sh" $ARGUMENTS
```

After the script completes, tell the user:
1. **Restart Claude Code** to pick up the MCP server and plugins
2. Run `/mason:start "scope" --spec path/to/spec.md` to start building
3. If they don't have a spec yet, use `/drew:plan "feature"` first

Drew draws it. Mason builds it.
