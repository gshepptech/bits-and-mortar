#!/usr/bin/env bash
# setup-prereqs.sh — Install everything needed for Mason.
#
# Usage: bash scripts/setup-prereqs.sh [--project /path/to/project]
#
# Installs:
#   - Mason MCP server (via uvx from this plugin)
#   - Playwright MCP (browser automation for SIGHT)
#   - Serena MCP (LSP wiring for TRACE)
#   - ralph-loop plugin (teammate execution engine)
#   - Configures .mcp.json in the target project

set -euo pipefail

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

info()  { printf "${CYAN}[mason]${RESET} %s\n" "$*"; }
ok()    { printf "${GREEN}[mason]${RESET} %s\n" "$*"; }
warn()  { printf "${YELLOW}[mason]${RESET} %s\n" "$*"; }
fail()  { printf "${RED}[mason]${RESET} %s\n" "$*" >&2; }

# ── Parse arguments ──────────────────────────────────────────────────────────
PROJECT_DIR=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --project) PROJECT_DIR="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Find plugin root (where this script lives)
PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MCP_SERVER_DIR="$PLUGIN_ROOT/mcp-server"

# Find project root
if [[ -n "$PROJECT_DIR" ]]; then
  PROJECT_ROOT="$PROJECT_DIR"
elif [[ -f "$PWD/.mcp.json" ]] || [[ -f "$PWD/package.json" ]] || [[ -f "$PWD/go.mod" ]]; then
  PROJECT_ROOT="$PWD"
else
  PROJECT_ROOT="$PWD"
fi

info "Plugin root:  $PLUGIN_ROOT"
info "MCP server:   $MCP_SERVER_DIR"
info "Project root: $PROJECT_ROOT"

# ── Check prerequisites ─────────────────────────────────────────────────────
if ! command -v claude &>/dev/null; then
    fail "claude CLI not found. Install Claude Code first."
    exit 1
fi

if ! command -v python3 &>/dev/null; then
    fail "python3 not found. Required for the Mason MCP server."
    exit 1
fi

if ! command -v npx &>/dev/null; then
    warn "npx not found. Playwright MCP (SIGHT) won't work."
fi

if ! command -v uvx &>/dev/null; then
    warn "uvx not found. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    warn "Serena MCP (TRACE) and Mason MCP require uvx."
fi

# ── Install Plugins ──────────────────────────────────────────────────────────
info "Installing required plugins..."

# ralph-loop (teammate execution)
info "  Installing ralph-loop..."
if claude plugin marketplace add anthropics/claude-plugins-official 2>/dev/null; then
    claude plugin install ralph-loop 2>/dev/null && ok "  ralph-loop installed" || warn "  ralph-loop may already be installed"
else
    warn "  claude-plugins-official marketplace may already be added"
    claude plugin install ralph-loop 2>/dev/null && ok "  ralph-loop installed" || warn "  ralph-loop may already be installed"
fi

# hookify (optional but useful)
info "  Installing hookify..."
claude plugin install hookify 2>/dev/null && ok "  hookify installed" || warn "  hookify may already be installed"

# ── Configure .mcp.json ─────────────────────────────────────────────────────
info "Configuring MCP servers..."

MCP_FILE="$PROJECT_ROOT/.mcp.json"

if [ -f "$MCP_FILE" ]; then
    info "Updating existing .mcp.json..."
else
    info "Creating .mcp.json..."
    echo '{"mcpServers": {}}' > "$MCP_FILE"
fi

# Use python3 for safe JSON manipulation
python3 << PYEOF
import json, os

mcp_file = "$MCP_FILE"
mcp_server_dir = "$MCP_SERVER_DIR"

with open(mcp_file) as f:
    cfg = json.load(f)

servers = cfg.setdefault("mcpServers", {})

# Mason MCP (the core state engine)
servers["mill"] = {
    "command": "uvx",
    "args": ["--from", mcp_server_dir, "mill-mcp", "--project-root", "."]
}

# Playwright MCP (browser automation for SIGHT)
if "playwright" not in servers:
    servers["playwright"] = {
        "command": "npx",
        "args": ["@playwright/mcp@latest", "--caps", "vision,devtools", "--output-dir", ".playwright-mcp"]
    }

# Serena MCP (LSP wiring for TRACE)
if "serena" not in servers:
    servers["serena"] = {
        "command": "uvx",
        "args": ["serena-mcp"]
    }

with open(mcp_file, "w") as f:
    json.dump(cfg, f, indent=2)
    f.write("\n")

print(f"Configured: mill, playwright, serena in {mcp_file}")
PYEOF

ok "MCP servers configured in $MCP_FILE"

# ── Serena project config ────────────────────────────────────────────────────
SERENA_DIR="$PROJECT_ROOT/.serena"
if [ ! -d "$SERENA_DIR" ]; then
    info "Creating Serena project config..."
    mkdir -p "$SERENA_DIR"
    cat > "$SERENA_DIR/project.yml" << 'SERENA_EOF'
# Serena LSP configuration for Mason TRACE verification
languages:
  - name: go
  - name: typescript
  - name: python
  - name: javascript

ignored_paths:
  - node_modules
  - vendor
  - .git
  - dist
  - build
  - __pycache__
  - .venv
SERENA_EOF
    ok "Serena config created at $SERENA_DIR/project.yml"
else
    ok "Serena config already exists"
fi

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
printf "${BOLD}${GREEN}Mason setup complete.${RESET}\n"
echo ""
echo "Installed:"
echo "  Plugins:     ralph-loop, hookify"
echo "  MCP Servers: mill (local), playwright (npx), serena (uvx)"
echo "  Config:      $MCP_FILE, $SERENA_DIR/project.yml"
echo ""
echo "Commands available:"
echo "  /mason:start \"scope\" --spec path/to/spec.md    Start building"
echo "  /mason:resume                                  Resume interrupted run"
echo "  /mason:status                                  Show run status"
echo "  /mason:stop                                    Graceful stop"
echo ""
printf "${BOLD}Restart Claude Code to activate MCP servers.${RESET}\n"
echo ""
echo "Drew draws it. Mason builds it."
