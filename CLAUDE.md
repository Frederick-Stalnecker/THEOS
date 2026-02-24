# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

THEOS (Temporal Hierarchical Emergent Optimization System) is a runtime AI governance framework built in pure Python (3.10+) with zero external dependencies for the core implementation. It implements dual-engine dialectical reasoning with a contradiction-bounded governor.

## Commands

### Run the core demo
```bash
python code/theos_system.py
```

### Run examples
```bash
python examples/theos_medical_diagnosis.py
python examples/theos_financial_analysis.py
python examples/theos_ai_safety.py
```

### Run tests
```bash
python -m pytest tests/test_theos_implementation.py -v
```

**Note:** `tests/test_theos_implementation.py` has hardcoded paths (`/home/ubuntu/THEOS_repo/`). To run tests locally, you must either update those `sys.path.insert` lines to point to `code/` and `examples/`, or run from the correct path context.

### Run a specific test
```bash
python -m pytest tests/test_theos_implementation.py::TestTheosCore::test_single_query -v
```

### Run by marker
```bash
python -m pytest tests/ -m unit -v
python -m pytest tests/ -m integration -v
```

### Install dev dependencies
```bash
pip install -r requirements-dev.txt
```

### Run the MCP server (requires `pip install mcp`)
```bash
python code/theos_mcp_server.py
```

## Architecture

The codebase has two implementation layers that partially overlap:

### Layer 1: Formal I→A→D→I Core (`code/theos_core.py` + `code/theos_system.py`)
The primary research implementation. `TheosCore` runs the reasoning loop:
1. **Induction** — encode observation, extract patterns
2. **Abduction** — dual engines generate left (constructive) and right (critical) hypotheses
3. **Deduction** — each engine derives conclusions
4. **Contradiction measurement** — governor decides to continue or halt

`TheosSystem` wraps `TheosCore` with wisdom persistence, query history, and metrics. All reasoning functions (encode, induce, abduce, deduce, measure_contradiction, retrieve_wisdom, update_wisdom, estimate_entropy, estimate_info_gain) are injected as callables—the system is domain-agnostic.

`TheosConfig` governs halting via: `max_cycles`, `eps_converge`, `eps_partial`, `rho_min`, `entropy_min`, `delta_min`, `similarity_threshold`, `budget`.

`TheosOutput` carries: `output`, `output_type` (convergence/blend/disagreement), `confidence`, `contradiction`, `cycles_used`, `halt_reason`, `trace`.

### Layer 2: Dual-Clock Governor (`code/theos_dual_clock_governor.py`)
A higher-level governor that manages two named engines (L/R) with structured `EngineOutput` objects scored on coherence, calibration, evidence, actionability, and risk. Tracks a `contradiction_budget` across a session. Produces `GovernorDecision` objects (CONTINUE / ADJUDICATE / FREEZE) with full audit dicts. This is what the MCP server (`code/theos_mcp_server.py`) wraps.

### Phase 2 Governor (`code/theos_governor_phase2.py`)
Extended implementation adding energy accounting, ethical alignment monitoring, adaptive cycle depth, Unified Query Interface (UQI), and `hashlib`-based audit trails.

### Supporting modules
- `code/llm_adapter.py` — Abstract `LLMAdapter` base class for Claude, GPT-4, Llama, etc.
- `code/semantic_retrieval.py` — Semantic search for wisdom retrieval
- `code/theos_llm_reasoning.py` — LLM-backed reasoning engine
- `code/uqi_implementation.py` — Unified Query Interface

### Examples (`examples/`)
Domain-specific engines built on top of `TheosSystem`: `theos_medical_diagnosis.py`, `theos_financial_analysis.py`, `theos_ai_safety.py`. These are imported by the test suite.

### Governor reference docs (`THEOS_Architecture/governor/`)
Specification documents for the governor mechanism (v1.1–v1.4) with worked examples and safety envelope presets.

## Key Design Patterns

**Dependency injection for domain logic:** `TheosCore` and `TheosSystem` accept all domain-specific functions as constructor arguments. To add a new domain, implement the required callable signatures and pass them in—no subclassing needed.

**Wisdom as a plain list:** `WisdomStore = List[Dict[str, Any]]`. `retrieve_wisdom` and `update_wisdom` are pure functions that take and return the list. Persistence is handled by `TheosSystem` via JSON file if `persistence_file` is set.

**Output type hierarchy:** When engines converge (`contradiction < eps_converge`), output is the left deduction directly. When partially converged (`< eps_partial`), output is a weighted blend. When fully disagreeing, output is a `{"type": "disagreement", ...}` dict—callers must handle all three cases.

**MCP integration:** `code/theos_mcp_server.py` exposes three tools (`execute_governed_reasoning`, `get_governor_status`, `log_wisdom`) for Claude Desktop via stdio. Requires `pip install mcp` separately.
