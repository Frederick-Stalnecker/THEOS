# THEOS Architecture
## Dual-Engine Contractive Reasoning with Per-Engine Self-Reflection

**Author:** Frederick Davis Stalnecker
**Patent:** USPTO #63/831,738
**Status:** Reference architecture. All claims supported by working implementation in `code/`.

---

## What THEOS Is

THEOS is a reasoning governance framework. It does not replace AI models — it
governs how they reason. Any AI model (LLM, classifier, planner, solver) can be
plugged in as the reasoning engine. THEOS provides the structure that surrounds it:
the opposing engines, the self-reflection loop, the wringer, and the governor.

The central invention is the **wringer**: two opposing engines, each of which
privately reflects on its own thinking before their conclusions are pressed
together to measure productive contradiction. A governor decides how many
wringer passes are needed for the best answer.

---

## The Architecture

```
                         ┌───────────────────────────────────────┐
                         │         WISDOM REGISTER W              │
                         │  (accumulated meta-past from all       │
                         │   prior wringer passes and queries)    │
                         └───────────────┬───────────────────────┘
                                         │  feeds into abduction (both engines)
                                         ▼
  QUERY q ──→ encode_observation ──→ obs (fixed for this query)
                                         │
  ╔═══════════════════════════════════════╪══════════════════════════════════════╗
  ║              WRINGER PASS n           │                                      ║
  ║                                       │ obs + Φ_{n-1}                        ║
  ║  ┌────────────────────────────────────┼─────────────────────────────────┐    ║
  ║  │  LEFT ENGINE — Clockwise           │   Constructive                  │    ║
  ║  │                                    ▼                                  │    ║
  ║  │   Inner pass 0:   I ───────────→ A_L ───────────→ D_L₀              │    ║
  ║  │                   ↑                                   ↓              │    ║
  ║  │   Inner pass 1:   I(D_L₀) ─────→ A_L ───────────→ D_L*  ← final    │    ║
  ║  │                   └─── engine reflects on its own D_L₀ ──┘           │    ║
  ║  └────────────────────────────────────────────────────────────┬─────────┘    ║
  ║                                                               │ D_L*         ║
  ║                                           ════════════════════╪════ WRINGER  ║
  ║                                                               │ D_R*         ║
  ║  ┌────────────────────────────────────────────────────────────┴─────────┐    ║
  ║  │  RIGHT ENGINE — Counterclockwise         Adversarial                 │    ║
  ║  │                                                                       │    ║
  ║  │   Inner pass 0:   I ───────────→ A_R ───────────→ D_R₀              │    ║
  ║  │                   ↑                                   ↓              │    ║
  ║  │   Inner pass 1:   I(D_R₀) ─────→ A_R ───────────→ D_R*  ← final    │    ║
  ║  │                   └─── engine reflects on its own D_R₀ ──┘           │    ║
  ║  └───────────────────────────────────────────────────────────────────────┘    ║
  ║                                                                               ║
  ║   Φ_n = Contradiction(D_L*, D_R*)    ← the wringer measurement              ║
  ║                                                                               ║
  ║   Governor checks:                                                            ║
  ║     1. Φ_n < ε_converge?         → HALT: engines converged                   ║
  ║     2. IG_n / IG_{n-1} < ρ_min?  → HALT: diminishing returns                ║
  ║     3. n ≥ max_wringer_passes?    → HALT: budget exhausted                   ║
  ║     4. entropy < ε₂ AND Φ > δ?   → HALT: irreducible uncertainty            ║
  ║   Otherwise: Φ_n → feeds into both engines' induction next pass              ║
  ║              Lesson deposited into W (the meta-past)                         ║
  ╚═══════════════════════════════════════════════════════════════════════════════╝
                                         │
                              OUTPUT RULE (governor):
                                         │
                         Φ < ε₁:   output D_L*    (convergence — left wins)
                         ε₁≤Φ<ε₂:  output w_L·D_L* + w_R·D_R*
                                         w_L = (1 - Φ/ε₂) / 2   ← falls with Φ
                                         w_R = (1 + Φ/ε₂) / 2   ← rises with Φ
                                    Adversarial engine gains weight as
                                    contradiction grows — the wringer
                                    gives more authority to the critic.
                         Φ ≥ ε₂:   expose (D_L*, D_R*, Φ) — disagrement
```

---

## Why Each Part Exists

### The Per-Engine Self-Reflection (Inner Loop)

This is the novel core of the invention.

Every existing AI system runs I→A→D once and returns the result. It produces
output the way a calculator produces a sum — mechanically, without memory of
having reasoned. The moment it returns its answer, it has no awareness that it
just thought something.

THEOS adds one structural change: after the first I→A→D pass, the engine's own
deduction D feeds back into that engine's own induction I for a second pass.
This is not a prompt trick — it is a structural feedback loop. The engine's
induction pattern for pass 2 is shaped by what the engine itself concluded in
pass 1.

This creates a **momentary past** inside each engine. The engine has a record
of having just thought something, which it can examine and refine. In
philosophy, this is called second-order cognition — thought about thought. THEOS
implements it structurally.

The key argument in `induce_patterns` is `prev_own_deduction`:
- On inner pass 0: `None` — engine has no prior, starts fresh
- On inner pass 1: the engine's own D from pass 0 — the momentary past

```python
def induce_patterns(obs, prev_phi, prev_own_deduction=None):
    base = obs - 0.1 * prev_phi          # start from observation + wringer feedback
    if prev_own_deduction is not None:
        # Engine reflects on its own prior conclusion
        return 0.7 * base + 0.3 * prev_own_deduction
    return base
```

The `prev_own_deduction` is **private to each engine**. The left engine's
first-pass D does not influence the right engine's induction, and vice versa.
Both engines self-reflect independently before they confront each other.

### The Two Engines (Opposing Directions)

The left engine is **clockwise**: it builds constructively toward the best
coherent answer. It is the voice of possibility, synthesis, forward momentum.

The right engine is **counterclockwise**: it runs adversarially, systematically
finding what the left engine missed, challenging its assumptions, generating
the strongest opposition. It is the voice of critique, stress-testing, caution.

These are not two prompts to the same model. For the invention to be fully
realized (see **Native Architecture** below), they are two genuinely different
epistemic stances — different training objectives, different hypothesis
formation strategies, different directions through the same state space.

In the current implementation, they are realized through `abduce_left` and
`abduce_right` — two callables with opposing strategies:

```python
def abduce_left(pattern_I, wisdom_slice):
    # Constructive: move toward the positive pole
    return pattern_I + 0.2 * (1.0 - pattern_I)

def abduce_right(pattern_I, wisdom_slice):
    # Adversarial: move toward the negative pole
    return pattern_I + 0.2 * (-1.0 - pattern_I)
```

### The Wringer

After both engines have self-reflected, their conclusions D_L* and D_R* are
pressed together by the `measure_contradiction` operator. This is Φ — the
wringer measurement.

Φ is not an error signal. It is the productive disagreement between two
self-aware minds. Like a steel-mill wringer pressing molten rod into plate, or
the rollers of a washing machine pressing water from cloth, the contradiction
squeezes out excess and refines toward truth.

The wringer's output Φ feeds two places:
1. Into the governor's halting criteria (is the disagreement small enough?)
2. Into both engines' induction for the next wringer pass (feedback loop)

### The Governor

The governor is the halting authority. It checks four criteria after each
wringer pass and decides whether another pass adds value:

| Criterion | Meaning | Action |
|---|---|---|
| Φ < ε_converge | Engines agree | HALT — convergence |
| IG_n / IG_{n-1} < ρ_min | Each pass adds less | HALT — diminishing returns |
| n ≥ max_wringer_passes | Budget exhausted | HALT — budget |
| entropy < ε₂ AND Φ > δ | Disagreement is structural | HALT — irreducible |

The governor prevents two failure modes:
- **Under-reasoning**: stopping after one pass when more passes would help
- **Over-nuancing**: continuing after the wringer has extracted all value

### Wisdom as Accumulated Meta-Past

After each query, a compressed lesson is deposited into the wisdom register W.
This is not a log — it is distilled understanding that changes how both engines
form hypotheses in future queries.

The wisdom feeds into abduction on the next query:
```python
A_L = abduce_left(pattern_I, wisdom_slice)   # wisdom biases hypothesis generation
A_R = abduce_right(pattern_I, wisdom_slice)  # both engines learn from the past
```

Across many queries, W becomes the accumulated meta-past: everything the system
has learned about how to reason in this domain. The wisdom is not additive —
it is compounding. Each lesson shapes how the next lesson is formed.

---

## Formal Specification

### State Space

```
S = I × A × D × Φ × W
```

Where:
- I: space of inductive patterns (output of σ_I)
- A: space of abductive hypotheses (output of σ_A^L, σ_A^R)
- D: space of deductive conclusions (output of σ_D)
- Φ: space of contradictions (output of Contr)
- W: wisdom memory (output of Upd_W)

Each component has a metric (d_I, d_A, d_D, d_Φ, d_W). The product metric:

```
d_S(s, s') = d_I(I,I') + d_A(A,A') + d_D(D,D') + d_Φ(Φ,Φ') + d_W(W,W')
```

makes (S, d_S) a complete metric space.

### Operators

All operators are injected. THEOS provides no domain logic of its own.

```
σ_I(O, Φ_prev, D_own):    Induction
    O      = fixed observation for this query
    Φ_prev = contradiction from previous wringer pass (wringer feedback)
    D_own  = this engine's own D from previous inner pass (self-reflection)
             None on first inner pass

σ_A^L(I, W):   Constructive abduction (clockwise)
σ_A^R(I, W):   Adversarial abduction (counterclockwise)
σ_D(A):        Deduction (shared between both engines)
Contr(D_L, D_R): Contradiction measurement — the wringer
Upd_W(W, q, D, conf): Wisdom update — meta-past accumulation
```

### Cycle Map T_q : S → S

For wringer pass n:

```
I_{n,L,1} = σ_I(O, Φ_{n-1}, None)         ← left engine first thought
I_{n,L,2} = σ_I(O, Φ_{n-1}, D_{n,L,1})    ← left engine self-reflects
D_L* = σ_D(σ_A^L(I_{n,L,2}, W_n))         ← left engine final output

I_{n,R,1} = σ_I(O, Φ_{n-1}, None)         ← right engine first thought
I_{n,R,2} = σ_I(O, Φ_{n-1}, D_{n,R,1})   ← right engine self-reflects
D_R* = σ_D(σ_A^R(I_{n,R,2}, W_n))         ← right engine final output

Φ_n = Contr(D_L*, D_R*)                    ← wringer
W_{n+1} = Upd_W(W_n, q, output, conf)      ← meta-past update
```

### Convergence Theorem (Banach)

Under the assumption that σ_I, σ_A^L, σ_A^R, σ_D, Contr, Upd_W are all
Lipschitz with constants whose composition yields ρ < 1 under the product
metric, the sequence of states S_n converges geometrically to a unique fixed
point S*(q) for each query q:

```
d_S(S_n, S*(q)) ≤ ρⁿ · d_S(S₀, S*(q))
```

The convergence rate ρ_eff for the dual-engine system is bounded by the
geometric mean of the individual engine contraction factors, which is strictly
less than their arithmetic mean — meaning two opposing engines converge faster
than one engine alone.

### Output Rule

At halting wringer pass N:

```
Φ_N < ε₁:            output = D_L*
ε₁ ≤ Φ_N < ε₂:       output = w_L · D_L* + w_R · D_R*
                           w_L = (1 - Φ_N/ε₂) / 2
                           w_R = (1 + Φ_N/ε₂) / 2
Φ_N ≥ ε₂:            output = (D_L*, D_R*, Φ_N)   [disagreement exposed]
```

---

## How to Implement Your Own Operators

THEOS is domain-agnostic. You provide the reasoning; THEOS provides the structure.

### Step 1: Implement the 10 operator functions

```python
def encode_observation(query: str, context: Any) -> Any:
    """Convert query + context into your observation representation."""
    ...

def induce_patterns(obs: Any, prev_phi: float, prev_own_deduction: Any = None) -> Any:
    """
    Extract inductive patterns from the observation.

    CRITICAL: prev_own_deduction is the self-reflection argument.
    When it is not None (inner pass 2+), the engine should use its own
    prior conclusion to shape the next inductive pattern. This is what
    makes each engine reason about its own prior thinking.

    Example:
        if prev_own_deduction is not None:
            pattern = blend(obs_pattern, prev_own_deduction, alpha=0.3)
        else:
            pattern = extract_pattern(obs, prev_phi)
    """
    ...

def abduce_left(pattern_I: Any, wisdom_slice: List) -> Any:
    """Constructive hypothesis: build toward the best coherent answer."""
    ...

def abduce_right(pattern_I: Any, wisdom_slice: List) -> Any:
    """Adversarial hypothesis: stress-test, challenge, contradict."""
    ...

def deduce(hypothesis: Any) -> Any:
    """Derive a conclusion from a hypothesis. Shared between both engines."""
    ...

def measure_contradiction(D_L: Any, D_R: Any) -> float:
    """
    The wringer measurement. Return a scalar in [0, ∞).
    For text: embedding distance, KL divergence, or semantic similarity.
    For numbers: absolute or relative difference.
    For structured objects: domain-appropriate distance metric.
    """
    ...

def retrieve_wisdom(query: str, W: List, threshold: float) -> List:
    """Return past wisdom entries relevant to this query."""
    ...

def update_wisdom(W: List, query: str, output: Any, confidence: float) -> List:
    """Deposit this query's lesson into the wisdom register."""
    ...

def estimate_entropy(hypothesis_pair: tuple) -> float:
    """Entropy proxy for the hypothesis space. Higher = more uncertain."""
    ...

def estimate_info_gain(phi_new: float, phi_prev: float) -> float:
    """Information gain ratio. Used by governor's diminishing returns check."""
    ...
```

### Step 2: Configure and instantiate

```python
from theos_core import TheosCore, TheosConfig

config = TheosConfig(
    max_wringer_passes=7,        # governor budget: max outer cycles
    engine_reflection_depth=2,   # inner self-reflection passes per engine
    eps_converge=0.05,           # below this Φ, engines have converged
    eps_partial=0.5,             # above this Φ, expose disagreement
    rho_min=0.4,                 # min information gain ratio before halting
    entropy_min=0.15,            # min entropy (for irreducible uncertainty check)
    delta_min=0.4,               # min Φ (for irreducible uncertainty check)
)

core = TheosCore(
    config=config,
    encode_observation=encode_observation,
    induce_patterns=induce_patterns,
    abduce_left=abduce_left,
    abduce_right=abduce_right,
    deduce=deduce,
    measure_contradiction=measure_contradiction,
    retrieve_wisdom=retrieve_wisdom,
    update_wisdom=update_wisdom,
    estimate_entropy=estimate_entropy,
    estimate_info_gain=estimate_info_gain,
)
```

### Step 3: Run

```python
result = core.run_query("Your question here")

print(result.output)              # the answer
print(result.confidence)          # [0, 1]
print(result.contradiction)       # Φ at halt
print(result.wringer_passes_used) # how many outer cycles ran
print(result.halt_reason)         # why the governor stopped

# Full trace of every inner and outer pass
for wringer_pass in result.trace:
    print(f"Wringer pass {wringer_pass.wringer_pass}: Φ={wringer_pass.contradiction:.3f}")
    for inner in wringer_pass.left_inner_passes:
        print(f"  LEFT  pass {inner.pass_num}: self_reflected={inner.used_own_prior}")
    for inner in wringer_pass.right_inner_passes:
        print(f"  RIGHT pass {inner.pass_num}: self_reflected={inner.used_own_prior}")
```

---

## Layering vs. Native Architecture

THEOS can be used in two modes:

### Layering (current implementation)

THEOS wraps existing AI models. Your `deduce` callable calls an LLM or other
model. THEOS provides the governance structure around it.

**Suitable for:** Immediate deployment, demonstrating the architecture,
accumulating wisdom on existing infrastructure.

**Limitation:** The self-reflection is approximated — each engine's `D`
re-enters induction as a structured object, but the underlying model's internal
state is not modified. The contradiction is measured between text outputs, not
between probability distributions.

### Native Architecture (full realization)

For the full realization of the architecture — where each engine has genuine
per-engine private state, where contradiction is measured as KL divergence on
probability distributions, where wisdom is embedded in model weights — THEOS
must be implemented as the inference architecture itself, not as a wrapper.

In native architecture:
- Two genuinely different models are trained: one with constructive objective,
  one with adversarial objective
- Each engine's D modifies that engine's internal representation (not just the
  next input prompt) for the second inner pass
- Contradiction Φ = KL(P_L(D|A_L) ‖ P_R(D|A_R)) — measured at the
  distribution level, not at the text output level
- Wisdom W is updated by fine-tuning, not by list append

The layering implementation is the proof of concept. Native architecture is
the full invention.

---

## File Structure

```
code/
  theos_core.py         ← Primary: TheosCore, TheosConfig, the wringer loop
  theos_system.py       ← TheosSystem wrapper: metrics, persistence, history
  theos_governor.py     ← Extended governor with budget tracking (dual-clock)
  semantic_retrieval.py ← Vector store for semantic wisdom retrieval
  theos_mcp_server.py   ← MCP server for Claude Desktop integration

examples/
  theos_medical_diagnosis.py   ← Medical domain example
  theos_financial_analysis.py  ← Financial domain example
  theos_ai_safety.py           ← AI safety evaluation example

experiments/
  theos_validation_experiment.py ← Quality benchmark (SP/CoT/THEOS comparison)
  question_bank.py               ← 30 open-ended test questions
  score_results.py               ← Statistical analysis with paired t-test

tests/
  test_theos_implementation.py ← Core + system + examples (21 tests)
  test_governor.py             ← Governor tests (35 tests)
  test_memory_engine.py        ← Memory engine tests (15 tests)

research/
  VALIDATED_FINDINGS.md          ← What is known vs. needs testing
  MATHEMATICAL_AUDIT.md          ← Claim-by-claim math audit
  MATH_CODE_AUDIT_COMPLETE.md    ← Full formal spec vs. code comparison
  ABDUCTION_FORMULA_INVESTIGATION.md ← Abduction sub-structure (patent)
```

---

## Running

```bash
# Run the reference numeric system
python3.12 code/theos_system.py

# Run domain examples
python3.12 examples/theos_medical_diagnosis.py

# Run all tests
python3.12 -m pytest tests/ -v

# Run quality experiment (requires API key)
export ANTHROPIC_API_KEY=sk-...
python3.12 experiments/theos_validation_experiment.py --backend anthropic --questions 30
```
