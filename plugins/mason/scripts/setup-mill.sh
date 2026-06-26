#!/bin/bash

# Mason Setup Script
# Parses arguments and initializes the Mason run state

set -euo pipefail

# Parse arguments
SCOPE=""
SPEC_PATH=""
URL=""
TEMPER=false
MAX_CYCLES=0
NO_UI=false
OUTPUT_DIR=""
TICKET=""
DESCRIPTION=""
SKIP_START_BACKEND=false

# Handle subcommands first
case "${1:-}" in
  resume|status|stop)
    echo "MILL_SUBCOMMAND=$1"
    exit 0
    ;;
esac

while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      cat << 'HELP_EOF'
Mason — Build-Verify-Fix Loop

Drew draws it. Mason builds it.

USAGE:
  /mason:start <SCOPE> [OPTIONS]
  /mason:resume
  /mason:status
  /mason:stop

ARGUMENTS:
  SCOPE             Description of what to build (required)

OPTIONS:
  --spec <path>            Spec file for spec-aware decomposition
  --url <url>              Browser audit URL for SIGHT verification
  --output-dir <dir>       Output directory (default: auto-generated)
  --temper                 Enable micro-domain stress testing (F5)
  --max-cycles <n>         Cap verify-fix cycles (default: unlimited)
  --no-ui                  Skip browser audit (SIGHT)
  --ticket <id>            Ticket ID for commit messages
  --desc <text>            Run description
  --skip-start-backend     Don't auto-start dev servers

PHASES:
  F0: DECOMPOSE  — Break spec into castings with observable truths
  F1: CAST       — Build castings with parallel teams
  F2: INSPECT    — 4-stream verification (TRACE + PROVE + SIGHT + TEST)
  F3: GRIND      — Fix defects, loop back to INSPECT
  F4: ASSAY      — Final spec-before-code verification (4 parallel agents)
  F5: TEMPER     — Micro-domain stress testing (optional)
  F6: DONE       — Report and archive

EXAMPLES:
  /mason:start "user authentication" --spec docs/specs/auth.md
  /mason:start "dashboard redesign" --spec docs/specs/dashboard.md --url http://localhost:3000
  /mason:start "api improvements" --spec docs/specs/api.md --temper
  /mason:start "quick fix" --no-ui --max-cycles 2

WORKFLOW:
  1. Drew plans:    /drew:plan "my feature"
  2. Mason builds: /mason:start "my feature" --spec docs/specs/my-feature.md

  Drew draws it. Mason builds it.
HELP_EOF
      exit 0
      ;;
    --spec)
      SPEC_PATH="$2"
      shift 2
      ;;
    --url)
      URL="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --temper)
      TEMPER=true
      shift
      ;;
    --max-cycles)
      MAX_CYCLES="$2"
      shift 2
      ;;
    --no-ui|--headless)
      NO_UI=true
      shift
      ;;
    --ticket)
      TICKET="$2"
      shift 2
      ;;
    --desc)
      DESCRIPTION="$2"
      shift 2
      ;;
    --skip-start-backend)
      SKIP_START_BACKEND=true
      shift
      ;;
    *)
      if [[ -z "$SCOPE" ]]; then
        SCOPE="$1"
      else
        SCOPE="$SCOPE $1"
      fi
      shift
      ;;
  esac
done

# Validate
if [[ -z "$SCOPE" ]]; then
  echo "Error: Scope description is required" >&2
  echo "" >&2
  echo "   Example: /mason:start \"user authentication\" --spec docs/specs/auth.md" >&2
  exit 1
fi

# Output parsed state for the plan command to use
echo "Mason — Build-Verify-Fix Loop"
echo ""
echo "Scope: $SCOPE"
if [[ -n "$SPEC_PATH" ]]; then echo "Spec: $SPEC_PATH"; fi
if [[ -n "$URL" ]]; then echo "URL: $URL"; fi
if [[ -n "$OUTPUT_DIR" ]]; then echo "Output: $OUTPUT_DIR"; fi
if [[ "$TEMPER" == "true" ]]; then echo "Temper: enabled"; fi
if [[ "$MAX_CYCLES" -gt 0 ]]; then echo "Max Cycles: $MAX_CYCLES"; fi
if [[ "$NO_UI" == "true" ]]; then echo "UI: disabled"; fi
if [[ -n "$TICKET" ]]; then echo "Ticket: $TICKET"; fi
if [[ -n "$DESCRIPTION" ]]; then echo "Description: $DESCRIPTION"; fi
echo ""
echo "MILL_SCOPE=$SCOPE"
echo "MILL_SPEC=$SPEC_PATH"
echo "MILL_URL=$URL"
echo "MILL_OUTPUT=$OUTPUT_DIR"
echo "MILL_TEMPER=$TEMPER"
echo "MILL_MAX_CYCLES=$MAX_CYCLES"
echo "MILL_NO_UI=$NO_UI"
echo "MILL_TICKET=$TICKET"
echo "MILL_DESC=$DESCRIPTION"
echo "MILL_SKIP_BACKEND=$SKIP_START_BACKEND"
echo ""
echo "Use MCP tool Mill-Init to create the run, then follow the phase guide."
echo "Call Mill-Next at every step to get specific instructions."
echo ""
echo "Drew draws it. Mason builds it."
