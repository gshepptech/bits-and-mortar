"""Mill MCP Server — tool registration and entry point."""

from __future__ import annotations

import argparse
import json
import sys

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from mill_mcp.tools.citation import verify_citations
from mill_mcp.tools.mill import (
    mill_add_defect,
    mill_add_verdict,
    mill_init,
    mill_query_defects,
    mill_verify_coverage,
)
from mill_mcp.tools.mill_orchestrator import (
    mill_clear_directives,
    mill_defects_to_tasks,
    mill_gate,
    mill_get_context,
    mill_inject_directive,
    mill_mark_defect_fixed,
    mill_mark_phase_complete,
    mill_mark_stream,
    mill_next_action,
    mill_register_team,
    mill_sync_defects,
    mill_unregister_team,
)
from mill_mcp.tools.display import format_result
from mill_mcp.tools.blueprint_spec import (
    blueprint_spec_check,
    blueprint_spec_start,
    blueprint_spec_status,
)
from mill_mcp.tools.mill_handoff import (
    mill_accept_casting,
    mill_handoff,
    mill_spec_hash,
)
from mill_mcp.tools.mill_spawn import mill_cast_wave, mill_spawn_teammate
from mill_mcp.tools.mill_validate import mill_validate_castings
from mill_mcp.tools.intent_coverage import mill_intent_coverage
from mill_mcp.tools.validation import validate_report

# Global project root, set via CLI arg
_project_root: str = "."

server = Server("Mill")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="Validate-Report",
            description="Validate a report's JSON block against a built-in schema (trace, prove, temper).",
            inputSchema={
                "type": "object",
                "required": ["report_path"],
                "properties": {
                    "report_path": {"type": "string", "description": "Path to the markdown report file."},
                    "schema_name": {"type": "string", "enum": ["trace", "prove", "temper", "custom"], "default": "trace"},
                    "schema_path": {"type": "string", "description": "Path to custom JSON schema (overrides schema_name)."},
                    "auto_fix": {"type": "boolean", "default": False, "description": "Auto-fix common issues."},
                },
            },
        ),
        Tool(
            name="Verify-Citations",
            description="Cross-reference spec requirements with PROVE verdicts for traceability.",
            inputSchema={
                "type": "object",
                "required": ["spec_path", "report_path"],
                "properties": {
                    "spec_path": {"type": "string", "description": "Path to the LISA spec."},
                    "report_path": {"type": "string", "description": "Path to the critic report."},
                    "strict": {"type": "boolean", "default": False, "description": "Fail if any requirement uncovered."},
                },
            },
        ),
        # ── Mill ──────────────────────────────────────────────
        Tool(
            name="Mill-Init",
            description=(
                "Start a new mill run under mill-archive/ or resume an existing one. "
                "Auto-generates a unique name. Each session tracks its active run in memory."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "spec_path": {"type": "string", "description": "Path to spec file to copy."},
                    "temper": {"type": "boolean", "default": False},
                    "no_ui": {"type": "boolean", "default": False},
                    "resume": {"type": "string", "description": "Name of existing run to resume (e.g. 'bold-falcon')."},
                    "ticket": {"type": "string", "default": ""},
                    "description": {"type": "string", "default": ""},
                },
            },
        ),
        Tool(
            name="Mill-Next",
            description=(
                "Guidance engine — returns exactly what to do next with rich status display. "
                "Call this instead of reading SKILL.md. Authoritative."
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="Mill-Context",
            description="Reload all mill state in one call. Use after compaction or session start.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="Mill-Gate",
            description="Check preconditions before entering a phase. Returns pass/fail with checklist.",
            inputSchema={
                "type": "object",
                "required": ["phase"],
                "properties": {
                    "phase": {"type": "string", "enum": ["validate", "cast", "inspect", "grind", "assay", "temper", "nyquist", "done"]},
                },
            },
        ),
        Tool(
            name="Mill-Phase",
            description="Mark a phase transition. Validates preconditions and updates state.",
            inputSchema={
                "type": "object",
                "required": ["phase"],
                "properties": {
                    "phase": {"type": "string", "enum": ["research_done", "decompose_done", "validate_done", "start_cast", "cast", "inspect_clean", "grind_start", "assay_fail", "temper", "nyquist_done", "done"]},
                },
            },
        ),
        Tool(
            name="Mill-Defect",
            description="Log a defect from any verification stream. Appends to ledger and blueprint-log.",
            inputSchema={
                "type": "object",
                "required": ["cycle", "source", "defect_type", "description"],
                "properties": {
                    "cycle": {"type": "integer"},
                    "source": {"type": "string", "enum": ["trace", "prove", "research_audit", "coverage_diff", "sight", "test", "assay", "temper"]},
                    "defect_type": {"type": "string", "enum": ["MISSING", "WRONG", "THIN", "HOLLOW", "UNWIRED", "BROKEN", "FAIL", "RESEARCH_DEVIATION", "COVERAGE_INCOMPLETE", "THIN_MIGRATION"]},
                    "description": {"type": "string"},
                    "spec_ref": {"type": "string"},
                    "symbol": {"type": "string"},
                    "file_path": {"type": "string"},
                },
            },
        ),
        Tool(
            name="Mill-Defects",
            description="Query the defect ledger with optional filters (status, cycle, source, spec_ref).",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["open", "fixed"]},
                    "cycle": {"type": "integer"},
                    "source": {"type": "string"},
                    "spec_ref": {"type": "string"},
                },
            },
        ),
        Tool(
            name="Mill-Fix",
            description="Mark a defect as fixed in this cycle.",
            inputSchema={
                "type": "object",
                "required": ["defect_id", "cycle"],
                "properties": {
                    "defect_id": {"type": "string"},
                    "cycle": {"type": "integer"},
                },
            },
        ),
        Tool(
            name="Mill-Sync",
            description="Sync new findings against existing defects. Detects regressions automatically.",
            inputSchema={
                "type": "object",
                "required": ["cycle", "findings"],
                "properties": {
                    "cycle": {"type": "integer"},
                    "findings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["description"],
                            "properties": {
                                "description": {"type": "string"},
                                "source": {"type": "string"},
                                "symbol": {"type": "string"},
                                "file": {"type": "string"},
                                "spec_ref": {"type": "string"},
                                "type": {"type": "string"},
                            },
                        },
                    },
                },
            },
        ),
        Tool(
            name="Mill-Tasks",
            description="Convert all open defects to grouped GRIND tasks.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="Mill-Verdict",
            description="Record a spec requirement verdict with evidence and citation.",
            inputSchema={
                "type": "object",
                "required": ["requirement_id", "verdict", "evidence"],
                "properties": {
                    "requirement_id": {"type": "string"},
                    "verdict": {"type": "string", "enum": ["VERIFIED", "HOLLOW", "THIN", "PARTIAL", "MISSING", "WRONG", "COVERAGE_INCOMPLETE"]},
                    "evidence": {"type": "string"},
                    "spec_text_cited": {"type": "string"},
                    "code_location": {"type": "string"},
                    "cycle": {"type": "integer", "default": 0},
                },
            },
        ),
        Tool(
            name="Mill-Coverage",
            description="Traceability matrix: spec requirements -> verdicts -> defects -> code evidence.",
            inputSchema={
                "type": "object",
                "properties": {
                    "spec_path": {"type": "string"},
                },
            },
        ),
        Tool(
            name="Mill-Stream",
            description="Mark a verification stream complete with coverage data. Requires items_checked > 0.",
            inputSchema={
                "type": "object",
                "required": ["stream", "cycle", "items_checked"],
                "properties": {
                    "stream": {"type": "string", "enum": ["trace", "prove", "research_audit", "coverage_diff", "sight", "test", "probe"]},
                    "cycle": {"type": "integer"},
                    "items_checked": {"type": "integer"},
                    "items_total": {"type": "integer"},
                    "findings_count": {"type": "integer", "default": 0},
                },
            },
        ),
        Tool(
            name="Mill-Validate-Castings",
            description="Validate castings against spec across 9 dimensions before CAST. Includes Prompt Fidelity (with <global_invariants> propagation), Migration Coverage, and Spec Structure (tagged requirement IDs + optional global_invariants section). Returns pass/fail with revision hints.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="Mill-Intent-Coverage",
            description=(
                "Validate intent-coverage.json (Phase 8 / INTENT-01) against the "
                "transcript-in-spec-appendix and emitted casting prompts. Runs at "
                "F0.7 between F0.5 DECOMPOSE and F0.9 VALIDATE. Returns "
                "{passed, dropped_answers, paraphrased_answers, propagated_count, "
                "matrix_path}. On any DROPPED, returns {action: 'redecompose'} "
                "with the missing A-NNN list as re-decompose guidance — never "
                "amends casting prompts in place."
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="Mill-Spawn-Teammate",
            description=(
                "Read the pre-authored teammate prompt for a casting and return it verbatim. "
                "The lead MUST pass the returned `prompt` field directly to the Agent tool without "
                "modification. Authored at F0.5 DECOMPOSE from the spec, validated at F0.9, frozen. "
                "Plans are prompts: the lead is a router, not an interpreter. "
                "Prefer Mill-Cast-Wave for wave-level bulk fetch — single casting lookups "
                "are for GRIND or one-off re-dispatches."
            ),
            inputSchema={
                "type": "object",
                "required": ["casting_id"],
                "properties": {
                    "casting_id": {"type": ["integer", "string"], "description": "Casting id from manifest.json."},
                    "phase": {"type": "string", "enum": ["cast", "grind"], "default": "cast"},
                },
            },
        ),
        Tool(
            name="Mill-Cast-Wave",
            description=(
                "Bulk-fetch prompts for every casting in a wave as a single MCP call. "
                "Replaces N sequential Mill-Spawn-Teammate roundtrips for a CAST wave. "
                "Returns {castings: [{casting_id, prompt, prompt_hash}, ...], team_name_suggestion, "
                "instructions}. Lead then does TeamCreate + Mill-Team-Up + a SINGLE parallel Agent "
                "tool-use message with one Agent per casting. Preserves audit trail — every casting "
                "is still logged to spawns.log with bulk=true."
            ),
            inputSchema={
                "type": "object",
                "required": ["wave"],
                "properties": {
                    "wave": {"type": "integer", "description": "1-indexed wave number from manifest.waves."},
                    "phase": {"type": "string", "enum": ["cast", "grind"], "default": "cast"},
                },
            },
        ),
        Tool(
            name="Mill-Spec-Hash",
            description=(
                "Return the current sha256 of spec.md. Call this before every Mill-Accept-Casting "
                "to force a re-read of the spec. Never accept a casting using a hash from memory — "
                "context rot makes prior-cycle hashes unreliable."
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="Mill-Handoff",
            description=(
                "Record a handoff event in the audit log. Every phase transition and artifact "
                "production should be recorded with source, destination, hashes, and whether "
                "the lead re-read the source. Writes to mill-archive/{run}/handoffs.md and "
                "handoffs.jsonl."
            ),
            inputSchema={
                "type": "object",
                "required": ["event"],
                "properties": {
                    "event": {"type": "string", "description": "e.g. spec_to_casting, casting_to_teammate, teammate_to_accepted, inspect_to_grind, grind_to_inspect, assay_to_done, spec_reread"},
                    "source": {"type": "string", "description": "Path to source artifact (relative to project root)."},
                    "destination": {"type": "string", "description": "Path to destination artifact."},
                    "source_reread": {"type": "boolean", "default": False, "description": "Did the lead just re-read the source before this handoff? Critical for spec→casting and acceptance handoffs."},
                    "summary": {"type": "string"},
                    "information_loss": {"type": "string", "description": "If non-empty, describes what was dropped from source in destination."},
                },
            },
        ),
        Tool(
            name="Mill-Accept-Casting",
            description=(
                "Gate acceptance of a completed casting. Requires fresh spec_hash and prompt_hash "
                "(verifies re-reads happened), extracts the casting's acceptance criteria from the "
                "<spec_requirements> block, checks the completion report for scope-flag phrases, "
                "and mechanically verifies every requirement ID in the casting's spec slice "
                "has a file:line citation in the completion report. Returns the AC list, requirement "
                "IDs, and any missing citations. Blocks acceptance if the teammate reported scope "
                "cuts OR any requirement has no citation."
            ),
            inputSchema={
                "type": "object",
                "required": ["casting_id", "spec_hash", "prompt_hash", "completion_report"],
                "properties": {
                    "casting_id": {"type": ["integer", "string"]},
                    "spec_hash": {"type": "string", "description": "Fresh hash from Mill-Spec-Hash."},
                    "prompt_hash": {"type": "string", "description": "Hash from Mill-Spawn-Teammate."},
                    "completion_report": {"type": "string", "description": "The teammate's completion report text."},
                },
            },
        ),
        Tool(
            name="Mill-Team-Up",
            description="Register a team for lifecycle tracking. Call after TeamCreate.",
            inputSchema={
                "type": "object",
                "required": ["team_name"],
                "properties": {"team_name": {"type": "string"}},
            },
        ),
        Tool(
            name="Mill-Team-Down",
            description="Unregister a team. Kills lingering tmux panes and waits for cleanup.",
            inputSchema={
                "type": "object",
                "required": ["team_name"],
                "properties": {"team_name": {"type": "string"}},
            },
        ),
        Tool(
            name="Mill-Directive",
            description="Inject a non-blocking directive. Lead reads it at every phase transition.",
            inputSchema={
                "type": "object",
                "required": ["directive"],
                "properties": {
                    "directive": {"type": "string"},
                    "priority": {"type": "string", "enum": ["normal", "urgent"], "default": "normal"},
                },
            },
        ),
        Tool(
            name="Mill-Clear",
            description="Clear all directives after they've been addressed.",
            inputSchema={"type": "object", "properties": {}},
        ),
        # ── Blueprint-Spec ─────────────────────────────────────────────
        Tool(
            name="Blueprint-Spec-Start",
            description=(
                "Initialize a blueprint-spec project directory and state machine. "
                "Creates blueprint-planning/{project}/ with research/, splits/, and state.json. "
                "Resumes if project already exists."
            ),
            inputSchema={
                "type": "object",
                "required": ["project_name"],
                "properties": {
                    "project_name": {"type": "string", "description": "Human-readable project name (e.g. 'BOM system for K3s')."},
                },
            },
        ),
        Tool(
            name="Blueprint-Spec-Check",
            description=(
                "Validate a blueprint-spec pipeline step completed. "
                "Actions: 'codebase' (knowledge graph exists?), 'decompose' (domain splits exist?), "
                "'spec' (deep-plan specs exist? converts to US-/FR- format)."
            ),
            inputSchema={
                "type": "object",
                "required": ["project_name", "action"],
                "properties": {
                    "project_name": {"type": "string", "description": "Project name or slug."},
                    "action": {
                        "type": "string",
                        "enum": ["codebase", "decompose", "spec"],
                        "description": "Which step to validate.",
                    },
                },
            },
        ),
        Tool(
            name="Blueprint-Spec-Status",
            description="Show blueprint-spec pipeline state with phase checklist.",
            inputSchema={
                "type": "object",
                "required": ["project_name"],
                "properties": {
                    "project_name": {"type": "string", "description": "Project name or slug."},
                },
            },
        ),
    ]


# ── Tool name -> function dispatch ───────────────────────────────────────────

_DISPATCH = {
    "Validate-Report": lambda args: validate_report(
        report_path=args["report_path"], schema_name=args.get("schema_name", "trace"),
        schema_path=args.get("schema_path"), auto_fix=args.get("auto_fix", False), project_root=_project_root),
    "Verify-Citations": lambda args: verify_citations(
        spec_path=args["spec_path"], report_path=args["report_path"],
        strict=args.get("strict", False), project_root=_project_root),
    "Mill-Init": lambda args: mill_init(
        spec_path=args.get("spec_path"), temper=args.get("temper", False), no_ui=args.get("no_ui", False),
        resume=args.get("resume"), ticket=args.get("ticket", ""), description=args.get("description", ""),
        project_root=_project_root),
    "Mill-Next": lambda args: mill_next_action(project_root=_project_root),
    "Mill-Context": lambda args: mill_get_context(project_root=_project_root),
    "Mill-Gate": lambda args: mill_gate(phase=args["phase"], project_root=_project_root),
    "Mill-Phase": lambda args: mill_mark_phase_complete(phase=args["phase"], project_root=_project_root),
    "Mill-Defect": lambda args: mill_add_defect(
        cycle=args["cycle"], source=args["source"], defect_type=args["defect_type"],
        description=args["description"], spec_ref=args.get("spec_ref", ""),
        symbol=args.get("symbol", ""), file_path=args.get("file_path", ""), project_root=_project_root),
    "Mill-Defects": lambda args: mill_query_defects(
        status=args.get("status"), cycle=args.get("cycle"), source=args.get("source"),
        spec_ref=args.get("spec_ref"), project_root=_project_root),
    "Mill-Fix": lambda args: mill_mark_defect_fixed(
        defect_id=args["defect_id"], cycle=args["cycle"], project_root=_project_root),
    "Mill-Sync": lambda args: mill_sync_defects(
        cycle=args["cycle"], findings=args["findings"], project_root=_project_root),
    "Mill-Tasks": lambda args: mill_defects_to_tasks(project_root=_project_root),
    "Mill-Verdict": lambda args: mill_add_verdict(
        requirement_id=args["requirement_id"], verdict=args["verdict"], evidence=args["evidence"],
        spec_text_cited=args.get("spec_text_cited", ""), code_location=args.get("code_location", ""),
        cycle=args.get("cycle", 0), project_root=_project_root),
    "Mill-Coverage": lambda args: mill_verify_coverage(
        spec_path=args.get("spec_path"), project_root=_project_root),
    "Mill-Stream": lambda args: mill_mark_stream(
        stream=args["stream"], cycle=args["cycle"], items_checked=args.get("items_checked", 0),
        items_total=args.get("items_total", 0), findings_count=args.get("findings_count", 0),
        project_root=_project_root),
    "Mill-Validate-Castings": lambda args: mill_validate_castings(project_root=_project_root),
    "Mill-Intent-Coverage": lambda args: mill_intent_coverage(project_root=_project_root),
    "Mill-Spawn-Teammate": lambda args: mill_spawn_teammate(
        casting_id=args["casting_id"], phase=args.get("phase", "cast"), project_root=_project_root),
    "Mill-Cast-Wave": lambda args: mill_cast_wave(
        wave=args["wave"], phase=args.get("phase", "cast"), project_root=_project_root),
    "Mill-Spec-Hash": lambda args: mill_spec_hash(project_root=_project_root),
    "Mill-Handoff": lambda args: mill_handoff(
        event=args["event"], source=args.get("source", ""), destination=args.get("destination", ""),
        source_reread=args.get("source_reread", False), summary=args.get("summary", ""),
        information_loss=args.get("information_loss", ""), project_root=_project_root),
    "Mill-Accept-Casting": lambda args: mill_accept_casting(
        casting_id=args["casting_id"], spec_hash=args["spec_hash"],
        prompt_hash=args["prompt_hash"], completion_report=args["completion_report"],
        project_root=_project_root),
    "Mill-Team-Up": lambda args: mill_register_team(team_name=args["team_name"], project_root=_project_root),
    "Mill-Team-Down": lambda args: mill_unregister_team(team_name=args["team_name"], project_root=_project_root),
    "Mill-Directive": lambda args: mill_inject_directive(
        directive=args["directive"], priority=args.get("priority", "normal"), project_root=_project_root),
    "Mill-Clear": lambda args: mill_clear_directives(project_root=_project_root),
    "Blueprint-Spec-Start": lambda args: blueprint_spec_start(
        project_name=args["project_name"], project_root=_project_root),
    "Blueprint-Spec-Check": lambda args: blueprint_spec_check(
        project_name=args["project_name"], action=args["action"], project_root=_project_root),
    "Blueprint-Spec-Status": lambda args: blueprint_spec_status(
        project_name=args["project_name"], project_root=_project_root),
}


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    handler = _DISPATCH.get(name)
    if handler:
        result = handler(arguments)
    else:
        result = {"error": f"Unknown tool: {name}"}

    return [TextContent(type="text", text=format_result(name, result))]


def main():
    global _project_root

    parser = argparse.ArgumentParser(description="Mill MCP Server")
    parser.add_argument("--project-root", default=".", help="Project root directory.")
    args = parser.parse_args()
    _project_root = args.project_root

    import asyncio
    asyncio.run(_run())


async def _run():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    main()
