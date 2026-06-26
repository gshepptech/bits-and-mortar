<!-- Thanks for the contribution! Keep the diff focused and the local checks green. -->

## What does this change?

<!-- A short summary. What and why, not just how. -->

## Which crew member(s)?

<!-- e.g. mason, bob, marketplace-wide -->

## Related issue

Closes #

## Checklist

- [ ] `python3 .github/scripts/validate_manifests.py` passes
- [ ] `git ls-files '*.js' | xargs -I{} node --check {}` passes (if JS changed)
- [ ] `cd plugins/mason/mcp-server && pytest` passes (if Mason changed)
- [ ] Bumped the plugin `version` and updated its `README.md` (if behavior changed)
- [ ] Updated the root `README.md` Crew table / `CHANGELOG.md` (if user-facing)
