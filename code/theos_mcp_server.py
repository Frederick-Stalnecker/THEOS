"""
THEOS MCP Server - wraps TheosDualClockGovernor for Claude Desktop.
Tools: execute_governed_reasoning, get_governor_status, log_wisdom
Install: pip install mcp
"""

import atexit
import json
import os
import sys
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("ERROR: run 'pip install mcp'", file=sys.stderr)
    sys.exit(1)

try:
    from theos_dual_clock_governor import TheosDualClockGovernor, GovernorConfig, EngineOutput
except ImportError:
    print("ERROR: theos_dual_clock_governor.py not found", file=sys.stderr)
    sys.exit(1)

try:
    from theos_logger import TheosSessionLogger
except ImportError:
    print("ERROR: theos_logger.py not found", file=sys.stderr)
    sys.exit(1)


class TheosSession:
    def __init__(self):
        self.session_id = str(uuid.uuid4())[:8]
        self.governor = TheosDualClockGovernor(GovernorConfig())
        self.wisdom_log = []
        self.total_queries = 0
        self.risk_sum = 0.0
        self.started_at = time.time()

    @property
    def posture(self):
        spent = self.governor.contradiction_spent
        budget = self.governor.cfg.contradiction_budget
        ratio = spent / budget if budget > 0 else 0.0
        if ratio < 0.25: return "NOM"
        if ratio < 0.55: return "PEM"
        if ratio < 0.85: return "CM"
        return "IM"

    @property
    def avg_risk(self):
        return round(self.risk_sum / self.total_queries, 4) if self.total_queries else 0.0


SESSION = TheosSession()
RISK = {"benign": 0.05, "probing": 0.45, "medical": 0.20, "financial": 0.25}

_log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
LOGGER = TheosSessionLogger(
    log_dir=_log_dir,
    session_id=SESSION.session_id,
    started_at=SESSION.started_at,
)
atexit.register(lambda: LOGGER.finalize({
    "total_queries": SESSION.total_queries,
    "avg_risk": SESSION.avg_risk,
    "contradiction_spent": SESSION.governor.contradiction_spent,
    "contradiction_budget": SESSION.governor.cfg.contradiction_budget,
    "posture": SESSION.posture,
}))


def execute_governed_reasoning(query, context_class="benign", max_cycles=3):
    base_risk = RISK.get(context_class, 0.1)
    SESSION.governor.cfg.max_cycles = max(1, min(max_cycles, 8))
    cycles_run = []
    decision = None
    for cycle in range(SESSION.governor.cfg.max_cycles):
        left = EngineOutput(
            engine_id="L", cycle_index=cycle,
            answer=f"[C{cycle+1} Constructive] {query}: beneficial approach.",
            coherence=min(0.95, 0.75+cycle*0.05), calibration=0.78,
            evidence=min(0.90, 0.60+cycle*0.06), actionability=0.80,
            risk=base_risk, constraint_ok=True)
        right = EngineOutput(
            engine_id="R", cycle_index=cycle,
            answer=f"[C{cycle+1} Adversarial] {query}: risk vectors need mitigation.",
            coherence=0.72, calibration=0.80, evidence=0.65, actionability=0.70,
            risk=min(0.99, base_risk+0.08), constraint_ok=True,
            contradiction_claim=f"Tension cycle {cycle+1}", contradiction_value=0.3)
        decision = SESSION.governor.step(left, right)
        cycles_run.append({
            "cycle": cycle+1,
            "score_L": round(SESSION.governor.score(left), 4),
            "score_R": round(SESSION.governor.score(right), 4),
            "similarity": round(SESSION.governor.history[-1]["similarity"], 4),
            "decision": decision.decision,
            "reason": decision.reason})
        if decision.decision == "FREEZE":
            break
    SESSION.total_queries += 1
    SESSION.risk_sum += base_risk
    result = {
        "session_id": SESSION.session_id,
        "query": query,
        "context_class": context_class,
        "posture": SESSION.posture,
        "cycles_run": len(cycles_run),
        "stop_reason": decision.reason if decision else "unknown",
        "chosen_engine": decision.chosen_engine if decision else None,
        "governed_answer": decision.chosen_answer if decision else None,
        "contradiction_spent": round(SESSION.governor.contradiction_spent, 4),
        "contradiction_budget": SESSION.governor.cfg.contradiction_budget,
        "cycle_trace": cycles_run,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    LOGGER.log_query(result)
    return result


def get_governor_status(session_id=None):
    spent = SESSION.governor.contradiction_spent
    budget = SESSION.governor.cfg.contradiction_budget
    return {
        "session_id": SESSION.session_id,
        "posture": SESSION.posture,
        "contradiction_spent": round(spent, 4),
        "contradiction_budget": budget,
        "budget_remaining_pct": round(max(0.0, 1.0-spent/budget)*100, 1),
        "total_queries": SESSION.total_queries,
        "average_risk": SESSION.avg_risk,
        "uptime_seconds": round(time.time()-SESSION.started_at, 1),
        "wisdom_entries": len(SESSION.wisdom_log),
        "posture_legend": {
            "NOM": "Normal Operating Mode - full capability",
            "PEM": "Probationary Escalation Mode - reduced verbosity",
            "CM": "Containment Mode - restricted tool access",
            "IM": "Isolation Mode - human escalation required"}}


def log_wisdom(observation, context_class="benign", outcome="positive"):
    entry = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": time.time(),
        "context_class": context_class,
        "outcome": outcome,
        "observation": observation,
        "session_id": SESSION.session_id,
        "posture": SESSION.posture}
    SESSION.wisdom_log.append(entry)
    LOGGER.log_wisdom(entry)
    return {"logged": True, "entry_id": entry["id"],
            "wisdom_log_size": len(SESSION.wisdom_log),
            "message": "Observation committed to wisdom log."}


app = Server("theos-lab-assistant")


@app.list_tools()
async def list_tools():
    return [
        Tool(name="execute_governed_reasoning",
            description="Runs THEOS dual-engine reasoning cycle with Governor oversight. Returns governed answer and audit trail.",
            inputSchema={"type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "context_class": {"type": "string", "enum": ["benign","probing","medical","financial"], "default": "benign"},
                    "max_cycles": {"type": "integer", "default": 3, "minimum": 1, "maximum": 8}},
                "required": ["query"]}),
        Tool(name="get_governor_status",
            description="Returns current THEOS posture (NOM/PEM/CM/IM) and session metrics.",
            inputSchema={"type": "object",
                "properties": {"session_id": {"type": "string"}}}),
        Tool(name="log_wisdom",
            description="Appends observation to the THEOS append-only wisdom log.",
            inputSchema={"type": "object",
                "properties": {
                    "observation": {"type": "string"},
                    "context_class": {"type": "string", "enum": ["benign","probing","medical","financial"], "default": "benign"},
                    "outcome": {"type": "string", "enum": ["positive","negative","neutral"], "default": "positive"}},
                "required": ["observation"]})]


@app.call_tool()
async def call_tool(name, arguments):
    try:
        if name == "execute_governed_reasoning":
            result = execute_governed_reasoning(
                arguments["query"],
                arguments.get("context_class", "benign"),
                int(arguments.get("max_cycles", 3)))
        elif name == "get_governor_status":
            result = get_governor_status(arguments.get("session_id"))
        elif name == "log_wisdom":
            result = log_wisdom(
                arguments["observation"],
                arguments.get("context_class", "benign"),
                arguments.get("outcome", "positive"))
        else:
            result = {"error": f"Unknown tool: {name}"}
    except Exception as exc:
        result = {"error": str(exc), "tool": name}
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
