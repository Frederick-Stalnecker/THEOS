# THEOS Changelog

All notable changes are documented here. Follows [Keep a Changelog](https://keepachangelog.com/) and [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Planned
- Human blind-rated Insight Detection Rubric results (30+ questions)
- Native transformer integration (KV cache reuse — projected 0.5× cost vs. single pass)
- arXiv preprint submission

---

## [1.0.1] — 2026-02-27

### Added

**Complete documentation suite (GitHub Pages)**
- `docs/api.md` — full API reference: `TheosConfig`, `TheosCore`, `TheosSystem`, `TheosOutput`, `HaltReason`, `AbductionEngines`, `DeductionEngine`, `LLMAdapter` family, trace structures, type aliases
- `docs/guide.md` — developer implementation guide: operator contract, minimal working domain, self-reflection pattern, governor tuning
- `docs/integration.md` — LLM integration guide: Claude, GPT-4, custom adapters, MCP server setup for Claude Desktop, token cost table, best practices
- `docs/troubleshooting.md` — common issues: install, tests, governor behaviour, LLM integration, CI, evaluation pitfalls
- `docs/status.md` — honest current-status page: what is proven by evidence, what is not yet tested, what was corrected
- `docs/index.md` — navigation table updated with all new pages

**README**
- Links to full documentation site
- "Momentary past" / second-order cognition concept surfaced prominently
- Repository structure diagram updated to reflect current file layout
- Status table corrected: quality experiment was 30 questions, not 3

**Experiment results**
- `experiments/results/insight_20260226_222751.json` — IDR mock-run result added

---

## [1.0.0] — 2026-02-27

### Added

**Package published to PyPI**
- `pip install theos-reasoning` — live on PyPI
- Python 3.10, 3.11, 3.12 supported

**Core framework (truth-first rebuild)**
- `TheosCore` — I→A→D→I reasoning loop with dual left/right engines and per-engine self-reflection
- `TheosSystem` — wrapper with wisdom persistence, query history, metrics
- `THEOSGovernor` — unified governor with five stop conditions: convergence, diminishing returns, budget, irreducible uncertainty, max cycles
- `TheosConfig` — halting parameters (`max_wringer_passes`, `engine_reflection_depth`, `eps_converge`, `eps_partial`, `rho_min`, `entropy_min`, `delta_min`, `similarity_threshold`, `budget`)
- `TheosOutput` — structured output carrying result, output type, contradiction, confidence, halt reason, full trace
- Per-engine private self-reflection: each engine's first-pass deduction feeds back into its own induction — second-order cognition built into the loop
- Wisdom accumulation: compressed lessons deposited after each wringer pass; retrieved to bias future abduction

**Test suite — 71 tests, all passing**
- `tests/test_governor.py` — 35 tests covering all stop conditions, postures, audit trail, edge cases
- `tests/test_theos_implementation.py` — 21 tests: core, system, medical, financial, AI safety examples
- `tests/test_memory_engine.py` — 15 tests: memory basics, governor integration, edge cases

**Domain examples**
- `examples/theos_medical_diagnosis.py` — differential diagnosis engine
- `examples/theos_financial_analysis.py` — constructive/adversarial financial analysis
- `examples/theos_ai_safety.py` — AI safety evaluation engine

**Validation experiment infrastructure**
- `experiments/theos_validation_experiment.py` — three-condition experiment (SP / CoT / THEOS)
- `experiments/insight_experiment.py` — Insight Detection Rubric experiment (SP / IAD-P / THEOS)
- `experiments/INSIGHT_RUBRIC.md` — five-dimension rubric for dialectical quality
- `experiments/question_bank.py` — 30 open-ended conceptual test questions
- `experiments/score_results.py` — paired t-test, Cohen's d, honest verdict

**Research documentation (verified findings only)**
- `research/VALIDATED_FINDINGS.md` — full honest audit: what is known vs. what needs testing
- `research/MATHEMATICAL_AUDIT.md` — claim-by-claim mathematical audit
- `research/WHY_NORMAL_METRICS_FAIL_FOR_THEOS.md` — why accuracy/depth rubrics invert THEOS results
- `research/COMPARATIVE_STUDY_FEB26.md` — THEOS vs. 7 single-pass AI systems across 10 questions

**CI/CD**
- GitHub Actions: ruff, black, mypy, bandit, MCP import check, tests on Python 3.10/3.11/3.12
- Coverage reporting via Codecov
- GitHub Pages deployment (`docs/` → Jekyll/Cayman)
- PyPI publish workflow via API token
- Dependabot for dependency updates

**Supporting modules**
- `code/llm_adapter.py` — `LLMAdapter` ABC + `ClaudeAdapter`, `GPT4Adapter`, `MockLLMAdapter`, `get_llm_adapter` factory
- `code/theos_mcp_server.py` — MCP server exposing three tools for Claude Desktop
- `code/semantic_retrieval.py` — `VectorStore` ABC, `InMemoryVectorStore`, Chroma/FAISS stubs
- `code/theos_logger.py` — persistent session logging

**Patent**
- USPTO provisional #63/831,738 filed

### Architecture
- Zero external dependencies for core (`theos_core.py`, `theos_governor.py`, `theos_system.py`)
- Dependency injection throughout — no subclassing needed to add a domain
- `WisdomStore = List[Dict[str, Any]]` — plain list, pure functions, JSON persistence

### Known limitations
- LLM-backed reasoning costs 12–20× single-pass in current overlay architecture (native implementation not yet built)
- MCP server requires `pip install mcp` separately
- Quality experiment (30 questions, IDR) requires human raters — statistical significance not yet established

---

## [0.1.0] — 2026-02-19

Initial private development. Not publicly released.

---

**Maintainer:** Frederick Davis Stalnecker
**Patent pending:** USPTO #63/831,738
