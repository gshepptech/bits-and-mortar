# Contributing to Bits & Mortar

Thanks for swinging by the job site. 👷 Whether you're fixing a typo, sharpening a
plugin, or pitching a whole new tradesperson for the crew, contributions are welcome.

## Ground rules

- **Be kind.** This project follows the [Code of Conduct](CODE_OF_CONDUCT.md).
- **Open an issue first** for anything non-trivial, so we can agree on the shape before you build.
- **Keep the spec intact.** Drew and Mason share one discipline — *plans are prompts*. Changes
  that touch the handoff format should preserve byte-for-byte fidelity.

## Repo layout

```
.claude-plugin/marketplace.json   # the marketplace manifest (lists all 8 plugins)
plugins/<name>/                   # one directory per tradesperson
  .claude-plugin/plugin.json      # that plugin's manifest
  README.md                       # per-plugin docs
.github/scripts/validate_manifests.py   # local manifest validator
```

## Local checks (run these before you push)

```bash
# 1. Validate the marketplace + every plugin manifest
python3 .github/scripts/validate_manifests.py

# 2. Syntax-check JavaScript
git ls-files '*.js' | xargs -I{} node --check {}

# 3. Run Mason's MCP-server tests
cd plugins/mason/mcp-server && pip install pytest jsonschema "mcp>=1.0.0" && pytest
```

All three are green on `main`. A PR should keep them that way.

## Adding or changing a plugin

1. Each plugin lives in `plugins/<name>/` with a `.claude-plugin/plugin.json` whose
   `name` matches the entry in `marketplace.json` (the manifest check above verifies this).
2. Update the plugin's own `README.md` and bump its `version`.
3. If you add a new plugin, add an entry to `marketplace.json` and a row to the
   **Crew** table in the root `README.md`.

## Pull requests

- Branch off `main`, keep the diff focused, and fill in the PR template.
- Reference the issue it closes.
- Run the local checks above before pushing.

## Naming note

The crew are people — **Drew, Mason, Bob, Gus, Dusty, Tess, Riggs, Marlowe**. One
internal note: the `mill_mcp` Python package under `plugins/mason/mcp-server/` has
**frozen** identifiers — they bind MCP tool resolution, so leave them as-is.

Happy building. 🧱
