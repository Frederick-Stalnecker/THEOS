# THEOS Changelog

All notable changes are documented here. Follows [Keep a Changelog](https://keepachangelog.com/) and [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Planned
- PyPI package publishing (`pip install theos-reasoning`)
- Human blind-rated insight experiment results (IDR rubric)
- Native transformer integration research

---

## [1.0.0] — 2026-02-24

### Added

**Core framework (truth-first rebuild)**
- `TheosCore` — I→A→D→I reasoning loop with dual left/right engines
- `TheosSystem` — wrapper with wisdom persistence, query history, metrics
- `THEOSGovernor` — unified governor with five stop conditions: convergence, risk, budget, plateau, max cycles
- `TheosConfig` — halting parameters (`max_cycles`, `eps_converge`, `eps_partial`, `rho_min`, `entropy_min`, `delta_min`, `similarity_threshold`, `budget`)
- `TheosOutput` — structured output carrying result, contradiction, confidence, halt reason, full trace
- `GovernorDecision` — decision object with chosen engine, chosen answer, similarity, posture, audit dict
- TF-IDF cosine similarity replacing Jaccard (reduces false positives from stop-word overlap)
- Wisdom accumulation: consequence-tracking, domain-organized retrieval

**Test suite — 71 tests, all passing**
- `tests/test_governor.py` — 35 tests covering all stop conditions, postures, audit trail, edge cases
- `tests/test_theos_implementation.py` — 21 tests: core, system, medical, financial, AI safety examples
- `tests/test_memory_engine.py` — 15 tests: memory basics, governor integration, edge cases

**Examples**
- `examples/theos_medical_diagnosis.py` — MedicalDiagnosisEngine
- `examples/theos_financial_analysis.py` — FinancialAnalysisEngine
- `examples/theos_ai_safety.py` — AISafetyEvaluator

**Validation experiment infrastructure**
- `experiments/theos_validation_experiment.py` — three-condition experiment (SP / CoT / THEOS)
- `experiments/insight_experiment.py` — Insight Detection Rubric experiment (SP / IAD-P / THEOS)
- `experiments/llm_interface.py` — MockLLM + AnthropicLLM + OpenAILLM adapters
- `experiments/score_results.py` — paired t-test, Cohen's d, honest verdict
- `experiments/INSIGHT_RUBRIC.md` — five-dimension rubric for measuring dialectical quality

**Research documentation (verified findings only)**
- `research/VALIDATED_FINDINGS.md` — what is known vs. needs testing
- `research/MATHEMATICAL_AUDIT.md` — claim-by-claim audit
- `research/WHY_NORMAL_METRICS_FAIL_FOR_THEOS.md` — why accuracy/depth rubrics invert THEOS results
- `research/COMPARATIVE_STUDY_FEB26.md` — THEOS vs. 7 major AI systems across 10 questions

**CI/CD**
- GitHub Actions: ruff, black, mypy, bandit, MCP import check, tests on Python 3.10/3.11/3.12
- Coverage reporting via pytest-cov + Codecov upload
- GitHub Pages deployment (`docs/` → Jekyll/Cayman)
- Dependabot for GitHub Actions updates

**Supporting modules**
- `code/semantic_retrieval.py` — VectorStore ABC, InMemoryVectorStore, ChromaVectorStore stub, FAISSVectorStore stub
- `code/llm_adapter.py` — abstract LLMAdapter base for Claude, GPT-4, Llama, etc.
- `code/theos_mcp_server.py` — MCP server exposing three tools for Claude Desktop
- `code/theos_logger.py` — persistent session logging

### Architecture
- Zero external dependencies for core (`code/theos_core.py`, `code/theos_governor.py`, `code/theos_system.py`)
- Dependency injection throughout — no subclassing needed for new domains
- `WisdomStore = List[Dict[str, Any]]` — plain list, pure functions, JSON persistence
- `TheosDualClockGovernor` kept as backward-compat alias for `THEOSGovernor`

### Known limitations
- No built-in LLM integration — callers supply engine outputs (by design)
- MCP server requires `pip install mcp` separately
- LLM-backed reasoning (`theos_llm_reasoning.py`) requires API key at runtime

---

## [0.1.0] — 2026-02-19

Initial private development. Not publicly released.

---

**Maintainer:** Frederick Davis Stalnecker
**Patent pending:** USPTO #63/831,738
