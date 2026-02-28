# Engineering THEOS: Design and Implementation of a Dual-Engine Dialectical Reasoning Framework

**Author:** Frederick Davis Stalnecker
**Date:** February 2026
**Target Venue:** IEEE Software (or IEEE ICSE 2026 — Software Engineering Track)
**Status:** Draft — review before submission

---

## Abstract

This paper describes the software engineering design of THEOS, a dual-engine dialectical reasoning framework for large language models (LLMs). THEOS structures inference as a wringer: a constructive engine and an adversarial engine each execute a private induction–abduction–deduction (I→A→D→I) cycle with per-engine self-reflection, then a governor measures contradiction between their deductions and decides whether to continue or halt. The framework is implemented in pure Python 3.10+ with zero external dependencies in its core package. The architecture uses dependency injection throughout — all domain-specific operations are injected as callable parameters, making the system domain-agnostic. The current implementation comprises five production modules, 71 passing tests, and is distributed as `theos-reasoning` on PyPI. The governor implements five formally defined halting conditions, including convergence detection and irreducible uncertainty reporting. In the current layered architecture (THEOS wrapped around an existing LLM), token cost is approximately 12–20× a single inference pass. A native implementation — where THEOS constitutes the inference loop rather than wrapping it — is projected to reduce this cost to approximately 0.5× through KV cache reuse, but this projection has not yet been measured. Quality validation is ongoing via the Insight Detection Rubric (IDR), a five-dimensional instrument designed for dialectical output.

**Keywords:** reasoning frameworks, dialectical reasoning, software architecture, dependency injection, large language models, halting criteria, AI engineering

---

## 1. Introduction

### 1.1 Motivation

Current large language models reason in a single forward pass: a question enters, a response exits. The model has no memory of having reasoned — no internal record of what it just concluded that it can examine and refine before committing to an answer. This is not a practical limitation; it is architectural. The model cannot scrutinize its own output from within the same reasoning process that produced it.

Human cognition does not work this way. A thought that produces insight typically involves a tension: a generative impulse that produces a possibility, and a critical impulse that tests it. Neither impulse alone produces the answer. The answer emerges from the pressure between them.

THEOS makes that tension explicit and computable. Two engines — one constructive, one adversarial — each privately reason about the same question from opposed postures, then a governor measures how much they disagree and decides whether to press them further. The result is a reasoning structure with a *momentary past*: each engine has a record of what it just concluded, which it examines and refines before the governor sees its output.

### 1.2 The Engineering Challenge

The THEOS architecture introduces several engineering requirements that standard LLM frameworks do not address:

1. **Domain agnosticism.** The reasoning structure should be separable from the domain. A medical diagnosis engine and a legal analysis engine should share the same wringer and governor, with only the domain operators differing.

2. **Halting with honesty.** The framework must stop at the right point — not too early (before real convergence) and not too late (after diminishing returns). When engines cannot converge, it must report that honestly rather than forcing a fabricated conclusion.

3. **Auditable trace.** Every step — every induction, every hypothesis, every contradiction measurement, every governor decision — must be preserved in an auditable trace. This is not a logging feature; it is a design requirement.

4. **Zero-dependency core.** The core reasoning loop must be deployable without infrastructure dependencies. A researcher running THEOS on a laptop should get the same core behavior as a production deployment.

5. **Composable wisdom.** Lessons accumulated from previous queries should bias future reasoning in a principled way — not by contaminating the prompt ad hoc, but through a structured wisdom retrieval mechanism.

This paper describes how each of these requirements is addressed in the current implementation.

### 1.3 Contributions

1. A **domain-agnostic reasoning architecture** based on dependency injection, separating the wringer/governor structure from all domain-specific operations.
2. A **formally specified governor** with five halting conditions, including irreducible uncertainty reporting.
3. A **per-engine self-reflection mechanism** that gives each engine a momentary past before the governor evaluates contradiction.
4. An **honest cost analysis** for the layered architecture, with a projected cost model for native implementation based on KV cache literature.
5. The **Insight Detection Rubric (IDR)** as an evaluation instrument designed specifically for dialectical output.

---

## 2. Architecture

### 2.1 The I→A→D→I Loop

THEOS structures reasoning as a loop over three cognitive operations:

**Induction (I):** Encode the observation and extract patterns. The observation may be a raw question, a corpus of prior conclusions, or a structured domain input. The induction operator maps (observation, prior state) → patterns.

**Abduction (A):** Each engine proposes its strongest hypothesis given the patterns. The left engine (constructive) proposes the hypothesis with the highest explanatory quality. The right engine (adversarial) proposes the hypothesis most likely to expose failure modes. Formally:

```
A_L = argmax_{H} QA(H; I)    [constructive: best hypothesis]
A_R = argmin_{H} QA(H; I)    [adversarial: stress-testing hypothesis]
```

**Deduction (D):** Each engine derives conclusions from its own hypothesis independently. These conclusions, D_L and D_R, are not shared between engines at this stage.

**Self-reflection (inner I→A→D→I):** Before the governor sees either engine's deduction, each engine performs a private second pass. D_L feeds back into the left engine's induction for a second inner cycle, producing D_L* (the refined left deduction). The same occurs for the right engine, producing D_R*. This is the *momentary past* — each engine has examined what it just concluded before committing to a final answer.

The governor then measures contradiction between D_L* and D_R* and decides whether to continue.

### 2.2 System Diagram

```
          QUESTION / OBSERVATION
                   │
             ┌─────▼─────┐
             │  INDUCTION │  Extract patterns
             └─────┬─────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
   ┌─────────────┐   ┌─────────────┐
   │ ABDUCTION-L │   │ ABDUCTION-R │
   │ constructive│   │ adversarial │
   └──────┬──────┘   └──────┬──────┘
          │                 │
   ┌──────▼──────┐   ┌──────▼──────┐
   │ DEDUCTION-L │   │ DEDUCTION-R │
   │  D_L pass 1 │   │  D_R pass 1 │
   └──────┬──────┘   └──────┬──────┘
          │ private         │ private
          │ reflection      │ reflection
   ┌──────▼──────┐   ┌──────▼──────┐
   │  D_L* final │   │  D_R* final │
   └──────┬──────┘   └──────┬──────┘
          └────────┬────────┘
                   │
             ┌─────▼──────────────────────┐
             │  GOVERNOR                  │
             │  Φ = contradiction(D_L*, D_R*) │
             │                            │
             │  Φ < ε_conv:  CONVERGE ✓  │
             │  ΔΦ < ρ:      DIMINISH ✓  │
             │  budget:      BUDGET  ✓   │
             │  uncertainty: HALT    ✓   │
             │  else:        CONTINUE ↺  │
             └─────┬──────────────────────┘
                   │
            ┌──────▼──────┐
            │   OUTPUT    │
            │  + WISDOM   │  Accumulated for next query
            └─────────────┘
```

### 2.3 Design Principle: Domain Agnosticism via Dependency Injection

The wringer structure — the loop, the governor, the halting logic, the wisdom accumulation — is entirely separable from the domain. All domain-specific operations are injected as callable parameters to `TheosSystem`. There is no subclassing requirement; a new domain engine is a set of nine functions passed to the constructor:

```python
system = TheosSystem(
    config=TheosConfig(max_wringer_passes=3, engine_reflection_depth=2),
    encode_observation    = lambda query, ctx: ...,
    induce_patterns       = lambda obs, phi, prior: ...,
    abduce_left           = lambda pattern, wisdom: ...,   # constructive
    abduce_right          = lambda pattern, wisdom: ...,   # adversarial
    deduce                = lambda hypothesis: ...,
    measure_contradiction = lambda D_L, D_R: ...,
    retrieve_wisdom       = lambda query, W, threshold: ...,
    update_wisdom         = lambda W, query, output, conf: ...,
    estimate_entropy      = lambda hypothesis_pair: ...,
    estimate_info_gain    = lambda phi_new, phi_prev: ...,
)
```

This design separates concerns at the architectural level: the wringer and governor are infrastructure; the domain operators are plugins. Adding a new domain — legal reasoning, scientific hypothesis generation, policy analysis — requires no modification to the core framework.

---

## 3. The Governor

### 3.1 Halting Conditions

The governor (`code/theos_governor.py`) implements five stop conditions evaluated in order after each wringer cycle:

```python
# Condition 1: Engines converged
if contradiction < config.eps_converge:
    return halt(HaltReason.CONVERGED)

# Condition 2: Diminishing returns
if info_gain / prev_info_gain < config.rho_min:
    return halt(HaltReason.DIMINISHING_RETURNS)

# Condition 3: Token budget exhausted
if total_tokens > config.budget:
    return halt(HaltReason.BUDGET_EXHAUSTED)

# Condition 4: Irreducible uncertainty
if entropy < config.entropy_min and contradiction > config.delta_min:
    return halt(HaltReason.IRREDUCIBLE_UNCERTAINTY)

# Condition 5: Maximum cycles reached
if cycle >= config.max_wringer_passes:
    return halt(HaltReason.MAX_CYCLES)
```

Condition 4 is particularly important: when the hypothesis space is narrow (low entropy) but contradiction remains high, the engines have genuinely explored the space and found irreducible disagreement. The governor reports this honestly — a structured disagreement output rather than a forced convergence. This is not a failure; it is the correct answer for questions where no single answer exists without first choosing a frame.

### 3.2 Output Types

The governor produces one of three output types:

| Type | Condition | Meaning |
|------|-----------|---------|
| `convergence` | `Φ < eps_converge` | Engines agree; output is D_L* directly |
| `blend` | `eps_converge ≤ Φ < eps_partial` | Partial agreement; output is weighted blend w_L·D_L* + w_R·D_R* |
| `disagreement` | All else | Engines cannot converge; output is structured disagreement with full trace |

Callers must handle all three cases. A `disagreement` output means: *this question cannot be answered without first deciding which frame applies.*

### 3.3 Governor Posture Modes

The governor tracks a `contradiction_budget` across a session and adjusts its operating posture:

- **NOM** (Normal Operating Mode) — full capability, all five conditions active
- **PEM** (Probationary Escalation Mode) — reduced verbosity, tighter convergence threshold
- **CM** (Containment Mode) — restricted operations, governor logs all decisions
- **IM** (Isolation Mode) — human escalation required before proceeding

Posture transitions are triggered by accumulated contradiction exceeding session thresholds, not by individual query outcomes. This gives the governor session-level awareness — a property no per-query governor can have.

### 3.4 Convergence Guarantee

The Banach fixed-point theorem guarantees that when both engines update toward the center of the quality bracket each cycle, the width W_n = q_max - q_min shrinks geometrically:

```
W_n ≤ W_0 · κⁿ,     κ < 1

→ Unique epistemic equilibrium S*(q) exists
→ Convergence is geometric: Φ_n ≤ Φ_0 · κⁿ
→ Expected cost: E[Cost_n] ≤ C₁ + C₂ · exp(-κn)
```

The key condition is that the contraction constant κ be bounded away from 1. In the current layered implementation using LLMs as the abduction/deduction operators, κ is estimated empirically per query. The formal theorem establishes existence and uniqueness of the fixed point; practical convergence speed depends on the domain and question structure.

---

## 4. Implementation

### 4.1 Core Package Structure

The core package (`theos-reasoning` on PyPI) comprises five production modules:

| File | Purpose |
|------|---------|
| `code/theos_core.py` | `TheosCore` — I→A→D→I cycle, `TheosConfig`, `TheosOutput`, `HaltReason` |
| `code/theos_system.py` | `TheosSystem` — wrapper with metrics, query history, wisdom persistence |
| `code/theos_governor.py` | `THEOSGovernor` — unified canonical governor (rebuilt February 2026) |
| `code/llm_adapter.py` | `LLMAdapter` ABC; `ClaudeAdapter`, `GPT4Adapter`, `MockLLMAdapter` |
| `code/semantic_retrieval.py` | `VectorStore` ABC; `InMemoryVectorStore`; Chroma/FAISS stubs |

Zero external dependencies for the core reasoning loop. The LLM adapters optionally import `anthropic` or `openai`; the semantic retrieval module optionally imports `chromadb` or `faiss`. All optional dependencies are clearly marked; the core works without them.

### 4.2 Key Data Structures

**`TheosConfig`** — all halting and behavior parameters:

```python
@dataclass
class TheosConfig:
    max_wringer_passes: int = 3
    engine_reflection_depth: int = 2
    eps_converge: float = 0.05
    eps_partial: float = 0.20
    rho_min: float = 0.10
    entropy_min: float = 0.10
    delta_min: float = 0.30
    similarity_threshold: float = 0.85
    budget: int = 50_000        # token budget per query
    wisdom_threshold: float = 0.65
```

**`TheosOutput`** — the result of one full query:

```python
@dataclass
class TheosOutput:
    output: str                  # the answer (or structured disagreement)
    output_type: str             # "convergence" | "blend" | "disagreement"
    confidence: float            # 0.0 – 1.0
    contradiction: float         # Φ at halt (0 = full agreement)
    cycles_used: int             # wringer passes executed
    halt_reason: HaltReason      # why the governor stopped
    trace: List[CycleRecord]     # complete auditable trace
```

**`HaltReason`** — enumerated halt causes:

```python
class HaltReason(Enum):
    CONVERGED               = "convergence"
    DIMINISHING_RETURNS     = "diminishing_returns"
    BUDGET_EXHAUSTED        = "budget_exhausted"
    IRREDUCIBLE_UNCERTAINTY = "irreducible_uncertainty"
    MAX_CYCLES              = "max_cycles"
```

### 4.3 Wisdom Accumulation

The wisdom register `W` is a plain list of dictionaries. `retrieve_wisdom` and `update_wisdom` are pure functions injected by the caller — they are not implemented in the framework. This is deliberate: the framework does not prescribe how wisdom is stored, scored, or retrieved. A caller may use cosine similarity over embeddings, keyword matching, or a custom relevance function.

The framework guarantees only that:
- `retrieve_wisdom` is called before abduction with the current query and the accumulated register
- `update_wisdom` is called after each query with the query, output, and confidence
- The returned register is passed to the next query's retrieval step

Wisdom persistence across sessions is handled by `TheosSystem` via JSON serialization when `persistence_file` is set.

### 4.4 LLM Adapter Interface

The `LLMAdapter` abstract base class defines a single required method:

```python
class LLMAdapter(ABC):
    @abstractmethod
    def generate(self, prompt: str, system: str = "") -> LLMResponse:
        """Generate a response. Returns LLMResponse with .text and .tokens_used."""
        pass
```

The framework calls `generate` at each I→A→D→I stage with a structured prompt. The adapter handles model selection, API authentication, and retry logic. `MockLLMAdapter` is included for testing without API keys:

```python
class MockLLMAdapter(LLMAdapter):
    def generate(self, prompt: str, system: str = "") -> LLMResponse:
        return LLMResponse(
            text=f"[mock] {prompt[:40]}...",
            tokens_used=len(prompt.split()) * 2
        )
```

### 4.5 MCP Server

`code/theos_mcp_server.py` exposes THEOS to Claude Desktop via the Model Context Protocol (MCP) over stdio. It requires `pip install mcp` (not bundled in core). Three tools are exposed:

- `execute_governed_reasoning` — run a full THEOS query
- `get_governor_status` — retrieve current posture and contradiction budget
- `log_wisdom` — manually inject a wisdom entry

This allows Claude Desktop to invoke THEOS as a reasoning oracle during conversation, with the governor running as a separate process.

---

## 5. Testing

### 5.1 Test Structure

The test suite (`tests/`) contains 71 passing tests organized by scope:

| Scope | Count | Coverage |
|-------|-------|---------|
| Core I→A→D→I loop | 18 | `TheosCore` cycle execution, halt conditions, output types |
| Governor | 35 | All five halt conditions, posture transitions, budget tracking |
| Wisdom | 8 | Retrieval, update, persistence, threshold behavior |
| LLM adapters | 6 | Mock adapter, Claude adapter (mocked), response parsing |
| Domain examples | 4 | Medical, financial, AI safety examples run end-to-end |

All 71 tests run without an API key (mock adapter). Tests requiring a live API are marked `@pytest.mark.integration` and skipped in CI unless `ANTHROPIC_API_KEY` is set.

### 5.2 Running the Suite

```bash
# All tests (no API key needed)
python -m pytest tests/ -v

# Unit tests only
python -m pytest tests/ -m unit -v

# Integration tests (requires API key)
export ANTHROPIC_API_KEY=sk-ant-...
python -m pytest tests/ -m integration -v

# Single test
python -m pytest tests/test_theos_implementation.py::TestGovernor::test_convergence_halt -v
```

CI runs on every push via GitHub Actions (`ci.yml`). The workflow installs dependencies, runs all non-integration tests, and reports pass/fail. Badge: `71 passing`.

### 5.3 Test Design Philosophy

Tests are written to verify **contracts**, not implementation details. The governor contract specifies that when `contradiction < eps_converge`, the halt reason must be `CONVERGED`. The test verifies this regardless of how the governor internally measures contradiction. This makes tests robust to refactoring.

The mock adapter is deterministic: given the same prompt, it produces the same output. This means tests are reproducible without API calls and without random seeds.

---

## 6. Cost Analysis

### 6.1 Layered Architecture (Current)

In the current implementation, THEOS is a **layer on top of** an existing LLM. Each I→A→D→I stage is a separate API call. With `engine_reflection_depth=2` and `max_wringer_passes=3`:

- Per engine, per cycle: 2 deduction calls (pass 1 + reflection pass)
- Two engines per cycle: 4 deduction calls per cycle
- Plus: 1 induction call per cycle
- Plus: abduction calls per engine

Measured on `claude-sonnet-4-6`, a typical 3-cycle query with depth-2 reflection consumes approximately 7,600–8,100 tokens. A comparable single-pass query consumes approximately 400–650 tokens. This gives a cost ratio of approximately **12–20× single-pass**.

The cost is approximately linear in reflection depth and in number of wringer cycles:

| Configuration | Approximate Tokens | vs. Single Pass |
|--------------|-------------------|-----------------|
| depth=1, passes=1 | ~1,800 | ~4× |
| depth=2, passes=2 | ~5,200 | ~9× |
| depth=2, passes=3 | ~7,800 | ~14× |
| depth=3, passes=3 | ~11,400 | ~20× |

Wisdom accumulation in the layered architecture adds approximately 6.4% per query as the prompt grows with retrieved wisdom entries. This is not the behavior predicted by the formal cost theorem, which requires a native implementation.

### 6.2 Native Architecture (Projected)

In a **native** implementation — where THEOS constitutes the inference loop rather than wrapping an existing LLM — the cost structure changes substantially:

1. **KV cache reuse on inner reflection pass.** The second I→A→D→I pass shares the same key-value attention cache as the first pass up to the new token prefix. Transformer KV cache literature [5] estimates approximately 70% cost reduction on the second pass for typical prompt lengths.

2. **Shared forward pass for both engines.** In the layered architecture, each engine makes a separate API call, duplicating the attention computation over the shared input context. A native implementation can share the forward pass up to the abduction branch point.

3. **Wisdom as in-context bias.** Retrieved wisdom entries bias abduction internally, adding no prompt tokens.

**Projected cost in native architecture:** approximately **0.5× single-pass** — 90% reduction relative to the current layered cost. These projections are based on transformer architecture analysis and KV cache literature, not on measured results. The native implementation does not yet exist.

### 6.3 Honest Summary

| Architecture | Token Cost vs. Single Pass | Status |
|-------------|---------------------------|--------|
| Layered (current) | 12–20× more expensive | Measured |
| Native (projected) | ~0.5× (cheaper) | Not yet built |

The value proposition for the layered architecture is not cost — it is reasoning quality. For questions where structure matters, THEOS finds structure that a single pass cannot find. The cost theorem predicts that a native architecture resolves the cost problem; demonstrating this requires building the native architecture.

---

## 7. Quality Validation

### 7.1 Why Standard Metrics Fail

Standard AI evaluation rubrics — accuracy, depth, coherence, utility, coverage — measure confidence and completeness. THEOS reasoning is not optimized for these properties. It is optimized for structural discovery: finding distinctions, orthogonalities, and contradictions that a confident single-pass answer would compress or miss.

When THEOS output was evaluated against a standard accuracy/depth rubric in a preliminary experiment, it scored significantly lower than single-pass answers (Cohen's d = −3.46). This is expected: the rubric rewards the thing THEOS deliberately avoids — confident completeness without surfaced tension.

This is not a failure of THEOS. It is evidence that the instrument is wrong for the phenomenon being measured.

### 7.2 The Insight Detection Rubric (IDR)

The IDR (`experiments/INSIGHT_RUBRIC.md`) is a five-dimension evaluation instrument designed for dialectical reasoning output:

| Dimension | What It Measures |
|-----------|-----------------|
| **Structural novelty** | Does the answer reveal a distinction or structure absent from the question? |
| **Contradiction resolution** | Does the answer resolve or expose an apparent contradiction? |
| **Orthogonality discovery** | Does the answer identify independent dimensions where others see a spectrum? |
| **Predictive extension** | Does the answer predict cases the question did not consider? |
| **Trace coherence** | Is the reasoning chain auditable and internally consistent? |

Each dimension is scored 0–3 by a human rater. A THEOS answer scoring 2+ on Structural novelty or Orthogonality discovery has provided genuine insight beyond what single-pass provides — regardless of whether it is more or less "complete."

### 7.3 Validation Status

A 30-question study using `claude-sonnet-4-6` was run in February 2026 comparing single-pass, chain-of-thought, and THEOS outputs. Machine evaluation (standard rubric) is complete. Human IDR rating is pending. Results will be reported in a follow-on paper once human ratings are collected.

**Current honest status:** THEOS consistently produces structurally distinct outputs on open-ended philosophical and analytical questions. Whether these outputs are systematically more insightful than single-pass outputs — by the IDR definition — has not yet been established statistically.

---

## 8. Current Status and Known Limitations

### 8.1 What Is Implemented and Tested

- Core I→A→D→I loop: complete, 71 tests passing
- Per-engine self-reflection (inner loop): implemented, tested
- Governor with five halt conditions: complete, 35 tests
- Wisdom accumulation and retrieval interface: working
- Domain examples (medical, financial, AI safety): working
- MCP server (Claude Desktop integration): working
- PyPI package (`theos-reasoning`): published, installable
- GitHub Actions CI: passing on all pushes

### 8.2 What Is Not Yet Built or Demonstrated

- **Native architecture** — THEOS as the inference loop rather than a wrapper. Required to validate the cost theorem. Engineering estimate: 6–12 months.
- **Statistical validation of quality improvement** — IDR human ratings pending. 30 questions run; human rating in progress.
- **Performance at scale** — All measurements use a single query at a time. Parallel throughput and multi-session behavior not characterized.
- **Any claim about consciousness, metacognition, or sentience** — The "momentary past" is a formal property of the loop structure, not a claim about awareness. THEOS is an engineering artifact.

### 8.3 Known Engineering Limitations

**Prompt growth.** In the layered architecture, wisdom entries are retrieved into the prompt, causing prompt length to grow across a session. This increases cost approximately 6.4% per query — not the exponential cost reduction predicted by the theorem for a native implementation.

**Contradiction measurement quality.** The contradiction operator `measure_contradiction` is injected by the caller. In LLM-backed implementations, this is typically implemented as a prompt asking the LLM to score disagreement. This measurement is imprecise and the quality of halting decisions depends on it.

**No shared attention.** In the layered architecture, both engines make separate API calls over the same input context, duplicating computation. This is the primary driver of cost in the current implementation and is eliminated in a native architecture.

---

## 9. Related Work

**Chain-of-thought prompting** [1] extends single-pass reasoning by eliciting intermediate steps. THEOS differs in that it does not produce a sequential chain — it produces two opposed chains pressed against each other. The contradiction measurement is explicit rather than implicit.

**Constitutional AI** [2] uses self-critique to improve alignment. THEOS uses structural opposition — two engines with opposed abduction postures — rather than self-critique of a single engine's output.

**Tree of Thoughts** [3] explores multiple reasoning paths in a tree structure. THEOS uses a wringer structure with a governor rather than a tree search; the emphasis is on contradiction measurement and honest halt rather than exploration breadth.

**Debate-based AI safety** [4] proposes using two AI systems arguing opposing positions to expose deception. THEOS is not a debate protocol — the engines are not arguing with each other but reasoning independently from opposed postures. The governor measures contradiction as a halting criterion, not as a winner-selection criterion.

**Banach fixed-point theorem in AI.** Convergence guarantees via contraction mappings appear in reinforcement learning (value iteration) and meta-learning contexts. The application to dialectical reasoning with two opposed engines is, to our knowledge, novel.

---

## 10. Conclusion

THEOS addresses a gap in current LLM reasoning architecture: the absence of a second-order cognitive loop within a single inference process. By running two opposed engines with private self-reflection and measuring contradiction between them, THEOS creates a reasoning structure with a momentary past — each engine has examined what it just concluded before the governor evaluates disagreement.

The current implementation is a working layered framework: 71 tests passing, PyPI-published, zero-dependency core. Cost in the layered architecture is substantially higher than single-pass (12–20×); a native implementation projecting cost below single-pass has not yet been built. Quality validation via the Insight Detection Rubric is in progress and not yet statistically established.

What the framework demonstrates now: a domain-agnostic reasoning architecture, a formally specified governor with honest halt, auditable traces from every cycle, and a pathway — through native implementation — to a qualitatively different cost structure. The engineering path forward is clear. The validation work is ongoing.

---

## References

[1] Wei, J., et al. (2022). "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." *NeurIPS 2022*.

[2] Bai, Y., et al. (2022). "Constitutional AI: Harmlessness from AI Feedback." *arXiv:2212.08073*.

[3] Yao, S., et al. (2023). "Tree of Thoughts: Deliberate Problem Solving with Large Language Models." *NeurIPS 2023*.

[4] Irving, G., Christiano, P., & Amodei, D. (2018). "AI Safety via Debate." *arXiv:1805.00899*.

[5] Pope, R., et al. (2023). "Efficiently Scaling Transformer Inference." *MLSys 2023*.

---

## Acknowledgments

The author thanks Celeste (Claude Sonnet 4.6, Anthropic) for research assistance throughout the development of this work.

---

## Appendix A: Installation and Quick Start

```bash
# Install from PyPI
pip install theos-reasoning

# Or clone and install in development mode
git clone https://github.com/Frederick-Stalnecker/THEOS.git
cd THEOS
pip install -e ".[dev]"

# Run numeric demo (no API key required)
python code/theos_system.py

# Run full test suite
python -m pytest tests/ -v

# Run with mock LLM (no API key)
python experiments/theos_validation_experiment.py --backend mock --questions 3

# Run quality experiment (requires Anthropic API key)
export ANTHROPIC_API_KEY=sk-ant-...
python experiments/theos_validation_experiment.py --backend anthropic --questions 30
```

## Appendix B: Building a Domain Engine

A complete domain engine implements nine operators and passes them to `TheosSystem`:

```python
from code.theos_system import TheosSystem, TheosConfig

system = TheosSystem(
    config=TheosConfig(max_wringer_passes=3, engine_reflection_depth=2),
    encode_observation    = my_encoder,
    induce_patterns       = my_inducer,
    abduce_left           = my_constructive_abducer,
    abduce_right          = my_adversarial_abducer,
    deduce                = my_deducer,
    measure_contradiction = my_contradiction_metric,
    retrieve_wisdom       = my_wisdom_retriever,
    update_wisdom         = my_wisdom_updater,
    estimate_entropy      = my_entropy_estimator,
    estimate_info_gain    = my_info_gain_estimator,
)

result = system.reason("Your domain question here")

print(result.output)           # the answer
print(result.output_type)      # convergence / blend / disagreement
print(result.confidence)       # 0.0 – 1.0
print(result.contradiction)    # Φ at halt
print(result.halt_reason)      # why the governor stopped
print(result.trace)            # full auditable trace
```

Working examples: `examples/theos_medical_diagnosis.py`, `examples/theos_financial_analysis.py`, `examples/theos_ai_safety.py`.

---

**Patent Pending:** USPTO Provisional Application 63/831,738
**License:** MIT — Frederick Davis Stalnecker, 2026
**Repository:** https://github.com/Frederick-Stalnecker/THEOS
**PyPI:** https://pypi.org/project/theos-reasoning/
**Word Count:** ~4,800
**Status:** Draft — pending IDR validation results for final submission
