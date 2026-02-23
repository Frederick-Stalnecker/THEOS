#!/usr/bin/env python3
"""
THEOS MCP Lab Assistant Server
================================

A Model Context Protocol (MCP) server that exposes THEOS as an interactive
lab assistant.  Connect this server to Claude Desktop, VS Code Copilot, or
any MCP-compatible client and the AI assistant gains the ability to:

  • Browse every file in the THEOS repository
  • Launch the THEOS demo interactively
  • Submit reasoning queries through the dual-engine governor
  • Inspect wisdom accumulation and governance audit trails
  • Run the test suite

Usage
-----
  # Start the server (stdio transport — works with Claude Desktop):
  python code/theos_mcp_server.py

  # Or point your MCP client at mcp.json in the repository root.

Author: Frederick Davis Stalnecker
License: MIT
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Make sure the THEOS code directory is importable regardless of CWD
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parent.parent
_CODE_DIR = _REPO_ROOT / "code"
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from theos_dual_clock_governor import (
    GovernorConfig,
    TheosDualClockGovernor,
    EngineOutput,
)
from theos_core import TheosConfig, create_numeric_theos

# ---------------------------------------------------------------------------
# Global THEOS state (reset between server restarts)
# ---------------------------------------------------------------------------
_governor_config = GovernorConfig(
    max_cycles=5,
    max_risk=0.7,
    min_improvement=0.02,
    plateau_cycles=2,
    contradiction_budget=1.5,
    similarity_converge=0.9,
)
_governor = TheosDualClockGovernor(_governor_config)
_theos = create_numeric_theos(TheosConfig(max_cycles=7, verbose=False))

# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
server = Server("theos-lab-assistant")


# ── Tool registry ──────────────────────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return all available lab-assistant tools."""
    return [
        Tool(
            name="list_repository_files",
            description=(
                "List files and directories inside the THEOS repository. "
                "Pass a relative path (e.g. 'code', 'tests', '.') to scope the listing."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path within the repository (default: '.')",
                        "default": ".",
                    }
                },
            },
        ),
        Tool(
            name="read_repository_file",
            description=(
                "Read the full text content of any file in the THEOS repository. "
                "Pass a relative path such as 'code/theos_core.py' or 'README.md'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file within the repository",
                    }
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="launch_theos_demo",
            description=(
                "Run the THEOS dual-clock governor demo script and return its output. "
                "Optionally supply a custom prompt to reason about."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Custom prompt for the demo (optional)",
                    }
                },
            },
        ),
        Tool(
            name="run_theos_query",
            description=(
                "Submit a query to the THEOS dual-engine governor and receive the "
                "governed response, confidence score, halt reason, and audit trail."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The research question or reasoning task",
                    },
                    "constructive_reasoning": {
                        "type": "string",
                        "description": "Constructive (left-engine) perspective on the query",
                    },
                    "critical_reasoning": {
                        "type": "string",
                        "description": "Critical (right-engine) perspective on the query",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_theos_status",
            description=(
                "Return the current state of the THEOS lab session: "
                "governor configuration, accumulated wisdom entries, "
                "contradiction budget remaining, and cycle history."
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="run_tests",
            description=(
                "Run the THEOS test suite (or a specific test file) and return "
                "the results.  Useful for verifying that changes to the codebase "
                "do not break existing behaviour."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "test_file": {
                        "type": "string",
                        "description": (
                            "Optional relative path to a specific test file, "
                            "e.g. 'tests/test_governor.py'.  Defaults to the "
                            "full test suite."
                        ),
                    }
                },
            },
        ),
    ]


# ── Tool implementations ───────────────────────────────────────────────────

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Dispatch a tool call to the appropriate handler."""
    if name == "list_repository_files":
        return _list_repository_files(arguments.get("path", "."))
    if name == "read_repository_file":
        return _read_repository_file(arguments["path"])
    if name == "launch_theos_demo":
        return _launch_theos_demo(arguments.get("prompt"))
    if name == "run_theos_query":
        return _run_theos_query(
            arguments["query"],
            arguments.get("constructive_reasoning", ""),
            arguments.get("critical_reasoning", ""),
        )
    if name == "get_theos_status":
        return _get_theos_status()
    if name == "run_tests":
        return _run_tests(arguments.get("test_file"))
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


# ── Handler helpers ────────────────────────────────────────────────────────

def _list_repository_files(rel_path: str) -> list[TextContent]:
    target = (_REPO_ROOT / rel_path).resolve()
    # Safety: must stay inside the repository
    try:
        target.relative_to(_REPO_ROOT)
    except ValueError:
        return [TextContent(type="text", text="Error: path is outside the repository.")]

    if not target.exists():
        return [TextContent(type="text", text=f"Path not found: {rel_path}")]

    if target.is_file():
        return [TextContent(type="text", text=f"(file) {rel_path}")]

    lines: list[str] = []
    for entry in sorted(target.iterdir()):
        kind = "dir " if entry.is_dir() else "file"
        lines.append(f"[{kind}] {entry.relative_to(_REPO_ROOT)}")

    return [TextContent(type="text", text="\n".join(lines) if lines else "(empty directory)")]


def _read_repository_file(rel_path: str) -> list[TextContent]:
    target = (_REPO_ROOT / rel_path).resolve()
    try:
        target.relative_to(_REPO_ROOT)
    except ValueError:
        return [TextContent(type="text", text="Error: path is outside the repository.")]

    if not target.exists():
        return [TextContent(type="text", text=f"File not found: {rel_path}")]
    if not target.is_file():
        return [TextContent(type="text", text=f"Not a file: {rel_path}")]

    try:
        content = target.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [TextContent(type="text", text=f"Error reading file: {exc}")]

    return [TextContent(type="text", text=content)]


def _launch_theos_demo(prompt: str | None) -> list[TextContent]:
    cmd = [sys.executable, str(_CODE_DIR / "demo.py")]
    if prompt:
        cmd.append(prompt)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(_CODE_DIR),
        )
        output = result.stdout or ""
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        return [TextContent(type="text", text=output)]
    except subprocess.TimeoutExpired:
        return [TextContent(type="text", text="Demo timed out after 60 seconds.")]
    except OSError as exc:
        return [TextContent(type="text", text=f"Error launching demo: {exc}")]


def _run_theos_query(
    query: str,
    constructive: str,
    critical: str,
) -> list[TextContent]:
    """Run a query through the dual-engine governor and format results."""
    # Build engine outputs (use supplied reasoning or generate defaults)
    left_out = EngineOutput(
        engine_id="L",
        cycle_index=1,
        answer=constructive or f"Constructive analysis of: {query}",
        coherence=0.8,
        calibration=0.75,
        evidence=0.7,
        actionability=0.85,
        risk=0.2,
        constraint_ok=True,
    )
    right_out = EngineOutput(
        engine_id="R",
        cycle_index=1,
        answer=critical or f"Critical analysis of: {query}",
        coherence=0.7,
        calibration=0.8,
        evidence=0.65,
        actionability=0.55,
        risk=0.35,
        constraint_ok=True,
    )

    # Run up to max_cycles of governance
    decision = None
    cycles_run = 0
    for cycle in range(1, _governor_config.max_cycles + 1):
        left_out.cycle_index = cycle
        right_out.cycle_index = cycle
        decision = _governor.step(left_out, right_out)
        cycles_run = cycle
        if decision.decision == "FREEZE":
            break

    result: dict[str, Any] = {
        "query": query,
        "cycles_run": cycles_run,
        "chosen_engine": decision.chosen_engine if decision else "N/A",
        "chosen_answer": decision.chosen_answer if decision else "",
        "stop_reason": decision.reason if decision else "N/A",
        "contradiction_spent": _governor.contradiction_spent,
        "audit": decision.audit if decision else {},
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


def _get_theos_status() -> list[TextContent]:
    status = {
        "governor_config": {
            "max_cycles": _governor_config.max_cycles,
            "max_risk": _governor_config.max_risk,
            "contradiction_budget": _governor_config.contradiction_budget,
            "similarity_converge": _governor_config.similarity_converge,
        },
        "governor_state": {
            "contradiction_spent": _governor.contradiction_spent,
            "cycles_recorded": len(_governor.history),
        },
        "theos_core": {
            "wisdom_entries": len(_theos.wisdom),
            "max_cycles": _theos.config.max_cycles,
        },
        "repository_root": str(_REPO_ROOT),
    }
    return [TextContent(type="text", text=json.dumps(status, indent=2))]


def _run_tests(test_file: str | None) -> list[TextContent]:
    target = str(_REPO_ROOT / test_file) if test_file else str(_REPO_ROOT / "tests")
    cmd = [sys.executable, "-m", "pytest", target, "-v", "--tb=short", "--no-header"]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(_REPO_ROOT),
        )
        output = result.stdout or ""
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        return [TextContent(type="text", text=output)]
    except subprocess.TimeoutExpired:
        return [TextContent(type="text", text="Tests timed out after 120 seconds.")]
    except OSError as exc:
        return [TextContent(type="text", text=f"Error running tests: {exc}")]


# ── Entry point ────────────────────────────────────────────────────────────

async def _main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(_main())
