---
layout: default
title: API Reference — THEOS
---

# API Reference

Complete reference for `theos-reasoning` — the THEOS Python package.

---

## Table of Contents

- [TheosConfig](#theosconfig)
- [TheosCore](#theoscore)
- [TheosSystem](#theossystem)
- [TheosOutput](#theosoutput)
- [HaltReason](#haltreason)
- [AbductionEngines](#abductionengines)
- [DeductionEngine](#deductionengine)
- [Trace Structures](#trace-structures)
- [LLM Adapters](#llm-adapters)

---

## TheosConfig

Controls the governor's halting behaviour and the engines' reasoning depth.

```python
from theos_core import TheosConfig

config = TheosConfig(
    max_wringer_passes=7,
    engine_reflection_depth=2,
    eps_converge=0.05,
    eps_partial=0.5,
    rho_min=0.4,
    entropy_min=0.15,
    delta_min=0.4,
    similarity_threshold=0.7,
    budget=None,
    verbose=False,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_wringer_passes` | `int` | `7` | Hard ceiling on outer wringer cycles. The governor may halt earlier. |
| `engine_reflection_depth` | `int` | `2` | Inner self-reflection passes per engine per wringer pass. `1` = no self-reflection; `2` = reflect on first thought before committing. |
| `eps_converge` | `float` | `0.05` | Contradiction threshold for full convergence. Below this, output is `D_L*` directly. |
| `eps_partial` | `float` | `0.5` | Contradiction threshold for blended output. Between `eps_converge` and `eps_partial`, output is a weighted blend of `D_L*` and `D_R*`. |
| `rho_min` | `float` | `0.4` | Minimum information-gain ratio. If `IG_n / IG_{n-1} < rho_min`, the wringer has hit diminishing returns. |
| `entropy_min` | `float` | `0.15` | Entropy floor for the irreducible-uncertainty halt condition. |
| `delta_min` | `float` | `0.4` | Contradiction floor for the irreducible-uncertainty halt condition. |
| `similarity_threshold` | `float` | `0.7` | Minimum cosine similarity for wisdom retrieval. Entries below this threshold are not surfaced. |
| `budget` | `float \| None` | `None` | Optional resource budget. `None` = unlimited. |
| `verbose` | `bool` | `False` | Print per-pass trace to stdout. |

**Alias:** `max_cycles` is a backward-compatible alias for `max_wringer_passes`.

---

## TheosCore

The primary reasoning engine. Runs the governed I→A→D→I wringer loop.

```python
from theos_core import TheosCore, TheosConfig, AbductionEngines, DeductionEngine

core = TheosCore(
    config=TheosConfig(),
    encode_observation=my_encoder,
    induce_patterns=my_inducer,
    engines=AbductionEngines(
        abduce_left=my_left_engine,
        abduce_right=my_right_engine,
    ),
    deduction=DeductionEngine(deduce=my_deducer),
    measure_contradiction=my_contradiction_fn,
    retrieve_wisdom=my_retrieval_fn,
    update_wisdom=my_wisdom_update_fn,
    estimate_entropy=my_entropy_fn,
    estimate_info_gain=my_info_gain_fn,
)

result = core.run_query("What is the difference between egotism and arrogance?")
```

### Constructor Parameters

All reasoning functions are injected — `TheosCore` is domain-agnostic.

| Parameter | Signature | Description |
|-----------|-----------|-------------|
| `config` | `TheosConfig` | Governor configuration. |
| `encode_observation` | `(query: str) -> Any` | Encode the raw query into an observation object `O`. |
| `induce_patterns` | `(obs, prev_phi, prev_own_deduction) -> PatternI` | Induction operator `σ_I`. Called once per inner pass per engine. `prev_own_deduction` is `None` on the first inner pass (no prior yet) and the engine's own prior `D` on reflection passes. |
| `engines` | `AbductionEngines` | Pair of abduction callables (left + right). |
| `deduction` | `DeductionEngine` | Shared deduction operator `σ_D`. |
| `measure_contradiction` | `(d_left, d_right) -> float` | The wringer. Returns `Φ ∈ [0, 1]`. |
| `retrieve_wisdom` | `(wisdom_store, query, threshold) -> WisdomStore` | Retrieve relevant wisdom entries for a query. |
| `update_wisdom` | `(wisdom_store, query, deduction, confidence) -> WisdomStore` | Deposit a new lesson into the wisdom store. |
| `estimate_entropy` | `(hyp_left, hyp_right) -> float` | Entropy of hypothesis space. Returns `float ∈ [0, 1]`. |
| `estimate_info_gain` | `(phi_prev, phi_curr) -> float` | Information gained this wringer pass. |

### Methods

#### `run_query(query, wisdom_store=None) -> TheosOutput`

Run a single query through the full wringer. Returns a `TheosOutput`.

```python
result = core.run_query("Is courage the absence of fear?")
print(result.output)
print(result.confidence)  # 0.0–1.0
print(result.halt_reason)  # HaltReason enum value
```

---

## TheosSystem

Higher-level wrapper that adds metrics tracking, query history, and optional JSON wisdom persistence.

```python
from theos_system import TheosSystem

system = TheosSystem(
    core=my_theos_core,
    persistence_file="wisdom.json",  # optional
)

result = system.reason("My question")
metrics = system.get_metrics()
```

### Constructor Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `core` | `TheosCore` | The underlying reasoning core. |
| `persistence_file` | `str \| None` | Path to a JSON file for wisdom persistence across sessions. `None` = in-memory only. |

### Methods

#### `reason(query) -> TheosOutput`

Run a query. Updates internal metrics and history.

#### `get_metrics() -> SystemMetrics`

Returns aggregate metrics across all queries run this session.

```python
m = system.get_metrics()
m.total_queries          # int
m.total_wringer_passes   # int
m.avg_passes_per_query   # float
m.convergence_rate       # fraction of queries that converged
m.wisdom_entries         # int
m.avg_confidence         # float
```

#### `get_history() -> list[dict]`

Returns the full audit log of every query and its output.

---

## TheosOutput

Returned by `TheosCore.run_query()` and `TheosSystem.reason()`.

```python
@dataclass
class TheosOutput:
    output: Any           # The answer — type depends on output_type
    output_type: str      # "convergence" | "blend" | "disagreement"
    confidence: float     # [0, 1]
    contradiction: float  # Φ at the halting wringer pass
    wringer_passes_used: int
    halt_reason: HaltReason
    trace: list[WringerPassTrace]
    wisdom_updated: bool
```

### Output Types

| `output_type` | When | `output` value | `confidence` |
|---------------|------|----------------|--------------|
| `"convergence"` | `Φ < eps_converge` | `D_L*` directly | `1 - Φ/eps_converge` (near 1.0) |
| `"blend"` | `eps_converge ≤ Φ < eps_partial` | Weighted blend dict or combined value | `1 - (Φ/eps_partial) * 0.5` |
| `"disagreement"` | `Φ ≥ eps_partial` on halt | `{"type": "disagreement", "left": D_L*, "right": D_R*, "contradiction": Φ}` | `0.5` |

**Callers must handle all three output types.** A `"disagreement"` result is not a failure — it means the question cannot be answered without first deciding which frame applies.

### Backward-Compatible Alias

`result.cycles_used` is an alias for `result.wringer_passes_used`.

---

## HaltReason

Enum returned in `TheosOutput.halt_reason`.

```python
from theos_core import HaltReason

class HaltReason(Enum):
    CONVERGENCE            = "convergence"             # Φ < eps_converge
    DIMINISHING_RETURNS    = "diminishing_returns"     # IG ratio < rho_min
    BUDGET_EXHAUSTION      = "budget_exhaustion"       # max passes or budget hit
    IRREDUCIBLE_UNCERTAINTY = "irreducible_uncertainty" # entropy low AND Φ high
    MAX_CYCLES             = "max_cycles"              # hit max_wringer_passes
    UNKNOWN                = "unknown"
```

---

## AbductionEngines

Dataclass wrapping the two opposing abduction callables.

```python
from theos_core import AbductionEngines

engines = AbductionEngines(
    abduce_left=my_constructive_engine,   # (PatternI, WisdomStore) -> HypothesisA
    abduce_right=my_adversarial_engine,   # (PatternI, WisdomStore) -> HypothesisA
)
```

- **`abduce_left`** — constructive (clockwise). Builds toward the best coherent answer.
- **`abduce_right`** — adversarial (counterclockwise). Systematically stresses and opposes.

Both functions share the same signature: `(pattern_I: PatternI, wisdom_slice: WisdomStore) -> HypothesisA`

---

## DeductionEngine

Dataclass wrapping the shared deduction callable.

```python
from theos_core import DeductionEngine

deduction = DeductionEngine(
    deduce=my_deduction_fn,   # (HypothesisA) -> DeductionD
)
```

The deduction operator is shared between both engines. The constructive/adversarial distinction lives entirely in abduction — both engines deduce conclusions from their own hypothesis using the same logic.

---

## Trace Structures

### WringerPassTrace

Full record of one outer wringer pass. Present in `TheosOutput.trace`.

```python
@dataclass
class WringerPassTrace:
    wringer_pass: int
    left_inner_passes: list[InnerPassTrace]   # Left engine's self-reflection trace
    right_inner_passes: list[InnerPassTrace]  # Right engine's self-reflection trace
    deduction_L: Any      # D_L*: left engine's final self-reflected output
    deduction_R: Any      # D_R*: right engine's final self-reflected output
    contradiction: float  # Φ = Contr(D_L*, D_R*)
    entropy: float
    info_gain_ratio: float
    halt_reason: HaltReason | None
    timestamp: str
```

### InnerPassTrace

Record of one inner self-reflection pass within a single engine.

```python
@dataclass
class InnerPassTrace:
    pass_num: int          # 0 = first thought, 1 = reflection, 2+ = deeper introspection
    pattern_I: Any         # Inductive pattern used this pass
    hypothesis: Any        # Abductive hypothesis generated
    deduction: Any         # Deductive conclusion reached
    used_own_prior: bool   # True if this pass reflected on the engine's own prior D
```

---

## LLM Adapters

THEOS ships adapters for connecting real LLMs to the reasoning engines.

### LLMAdapter (abstract base)

```python
from llm_adapter import LLMAdapter, LLMResponse

class LLMAdapter(ABC):
    def reason(self, prompt, system_prompt=None, temperature=0.7, max_tokens=2000) -> LLMResponse
    def get_statistics(self) -> dict
```

`LLMResponse` fields: `content: str`, `tokens_used: int`, `model: str`, `stop_reason: str | None`, `confidence: float | None`

### ClaudeAdapter

```python
from llm_adapter import ClaudeAdapter

adapter = ClaudeAdapter(
    api_key="sk-ant-...",           # or set ANTHROPIC_API_KEY env var
    model="claude-sonnet-4-6",      # any Claude model ID
)
response = adapter.reason("My prompt")
print(response.content)
```

Requires: `pip install anthropic`

### GPT4Adapter

```python
from llm_adapter import GPT4Adapter

adapter = GPT4Adapter(
    api_key="sk-...",               # or set OPENAI_API_KEY env var
    model="gpt-4-turbo",
)
```

Requires: `pip install openai`

### MockLLMAdapter

For testing — no API key required. Returns deterministic mock responses.

```python
from llm_adapter import MockLLMAdapter
adapter = MockLLMAdapter()
```

### Factory Function

```python
from llm_adapter import get_llm_adapter

adapter = get_llm_adapter(
    provider="claude",   # "claude" | "gpt4" | "mock"
    api_key=None,        # uses env var if not provided
    model=None,          # uses provider default if not provided
)
```

---

## Type Aliases

```python
PatternI      = Any           # Inductive pattern: output of σ_I
HypothesisA   = Any           # Abductive hypothesis: output of σ_A^L / σ_A^R
DeductionD    = Any           # Deductive conclusion: output of σ_D
ContradictionF = float        # Wringer measurement: output of Contr(D_L, D_R)
WisdomEntry   = dict[str, Any]
WisdomStore   = list[WisdomEntry]
```

THEOS is generic over these types. Your domain determines what `PatternI`, `HypothesisA`, and `DeductionD` look like — they can be strings, structured dicts, embeddings, or anything else.

---

*Patent pending — USPTO 63/831,738 · MIT License · Frederick Davis Stalnecker, 2026*
