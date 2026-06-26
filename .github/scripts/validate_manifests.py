#!/usr/bin/env python3
"""Validate the marketplace manifest and every plugin manifest.

Run from the repo root. Exits non-zero on the first class of problems found,
after reporting all of them. Used by .github/workflows/ci.yml.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
errors: list[str] = []


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    return None


def main() -> int:
    # 1. Every tracked .json must parse.
    for path in sorted(ROOT.rglob("*.json")):
        if ".git" in path.parts:
            continue
        load_json(path)

    # 2. Marketplace manifest exists and is well-formed.
    market_path = ROOT / ".claude-plugin" / "marketplace.json"
    market = load_json(market_path)
    if market is None:
        _report()
        return 1

    if not market.get("name"):
        errors.append("marketplace.json: missing 'name'")

    plugins = market.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        errors.append("marketplace.json: 'plugins' must be a non-empty array")
        _report()
        return 1 if errors else 0

    # 3. Each marketplace entry resolves to a real plugin with a matching manifest.
    seen: set[str] = set()
    for entry in plugins:
        name = entry.get("name", "<unnamed>")
        if name in seen:
            errors.append(f"duplicate plugin name in marketplace: {name}")
        seen.add(name)

        source = entry.get("source")
        if not source:
            errors.append(f"{name}: missing 'source'")
            continue

        plugin_dir = (ROOT / source).resolve()
        manifest = plugin_dir / ".claude-plugin" / "plugin.json"
        data = load_json(manifest)
        if data is None:
            continue
        if data.get("name") != name:
            errors.append(
                f"name mismatch: marketplace says '{name}', "
                f"{manifest.relative_to(ROOT)} says '{data.get('name')}'"
            )

    _report()
    return 1 if errors else 0


def _report() -> None:
    if errors:
        print(f"\n✗ {len(errors)} problem(s) found:\n", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
    else:
        print("✓ all manifests valid")


if __name__ == "__main__":
    raise SystemExit(main())
