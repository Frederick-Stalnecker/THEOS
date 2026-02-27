---
layout: default
title: Developer Guide — THEOS
---

# Developer Guide

How to build a THEOS-powered reasoning system for your own domain.

---

## Overview

THEOS is **domain-agnostic by design**. The core wringer loop makes no assumptions about what you are reasoning about. You supply ten operator functions; THEOS runs the governed I→A→D→I loop and returns a structured output.

This guide walks through building a minimal working domain from scratch.

---

## Step 1 — Understand the Operator Contract

Every THEOS domain implements these ten callables:

```
encode_observation(query: str) -> Any
    Turn the raw query string into a structured observation object O.

induce_patterns(obs: Any, prev_phi: float, prev_own_deduction: Any | None) -> PatternI
    Extract patterns from the observation.
    prev_phi:            contradiction from the last wringer pass (0.0 on first call)
    prev_own_deduction:  this engine's own prior D (None on first inner pass)
                         Use this to make the engine reflect on what it just concluded.

abduce_left(pattern: PatternI, wisdom: WisdomStore) -> HypothesisA
    Constructive abduction — build toward the strongest coherent answer.

abduce_right(pattern: PatternI, wisdom: WisdomStore) -> HypothesisA
    Adversarial abduction — systematically stress-test and oppose.

deduce(hypothesis: HypothesisA) -> DeductionD
    Shared deduction — derive a conclusion from a hypothesis.

measure_contradiction(d_left: DeductionD, d_right: DeductionD) -> float
    The wringer. Must return a float in [0, 1].
    0.0 = perfect agreement. 1.0 = complete contradiction.

retrieve_wisdom(wisdom: WisdomStore, query: str, threshold: float) -> WisdomStore
    Return the entries from the wisdom store most relevant to this query.

update_wisdom(wisdom: WisdomStore, query: str, deduction: DeductionD, confidence: float) -> WisdomStore
    Add a new lesson (distilled from this wringer run) to the wisdom store.

estimate_entropy(hyp_left: HypothesisA, hyp_right: HypothesisA) -> float
    Estimate entropy of the hypothesis space. Returns float in [0, 1].

estimate_info_gain(phi_prev: float, phi_curr: float) -> float
    How much information was gained this wringer pass.
```

---

## Step 2 — Build a Minimal Domain

Here is a complete minimal example. The domain reasons about simple text questions using word-overlap as a proxy for contradiction.

```python
import sys, os
sys.path.insert(0, "code")

from theos_core import TheosCore, TheosConfig, AbductionEngines, DeductionEngine

# --- Operator implementations ---

def encode_observation(query: str):
    """Encode query as a dict with key terms."""
    words = set(query.lower().split())
    return {"query": query, "terms": words}

def induce_patterns(obs, prev_phi: float, prev_own_deduction):
    """Extract what the question is really asking."""
    pattern = {"terms": obs["terms"], "phi_feedback": prev_phi}
    if prev_own_deduction is not None:
        # Self-reflection: incorporate own prior conclusion
        pattern["prior_conclusion"] = prev_own_deduction
    return pattern

def abduce_left(pattern, wisdom):
    """Constructive: assert the most affirmative position."""
    terms = pattern["terms"]
    return f"Affirming: {', '.join(sorted(terms))} — building the strongest case."

def abduce_right(pattern, wisdom):
    """Adversarial: assert the most critical position."""
    terms = pattern["terms"]
    return f"Challenging: {', '.join(sorted(terms))} — probing for weaknesses."

def deduce(hypothesis: str) -> str:
    """Derive a conclusion from a hypothesis."""
    return f"Therefore: [{hypothesis}]"

def measure_contradiction(d_left: str, d_right: str) -> float:
    """Word-overlap proxy for contradiction."""
    words_l = set(d_left.lower().split())
    words_r = set(d_right.lower().split())
    if not words_l or not words_r:
        return 1.0
    overlap = len(words_l & words_r) / len(words_l | words_r)
    return 1.0 - overlap   # high overlap → low contradiction

def retrieve_wisdom(wisdom, query: str, threshold: float):
    """Return all wisdom entries for this example."""
    return wisdom

def update_wisdom(wisdom, query: str, deduction, confidence: float):
    """Append a new lesson."""
    wisdom.append({"query": query, "lesson": deduction, "confidence": confidence})
    return wisdom

def estimate_entropy(hyp_left: str, hyp_right: str) -> float:
    """Entropy proxy: proportion of unique words."""
    words_l = set(hyp_left.lower().split())
    words_r = set(hyp_right.lower().split())
    shared = len(words_l & words_r)
    total = len(words_l | words_r)
    return 1.0 - (shared / total) if total > 0 else 0.5

def estimate_info_gain(phi_prev: float, phi_curr: float) -> float:
    """Information gain = reduction in contradiction."""
    return max(0.0, phi_prev - phi_curr)


# --- Wire it together ---

config = TheosConfig(
    max_wringer_passes=3,
    eps_converge=0.3,
    eps_partial=0.6,
    verbose=True,
)

core = TheosCore(
    config=config,
    encode_observation=encode_observation,
    induce_patterns=induce_patterns,
    engines=AbductionEngines(
        abduce_left=abduce_left,
        abduce_right=abduce_right,
    ),
    deduction=DeductionEngine(deduce=deduce),
    measure_contradiction=measure_contradiction,
    retrieve_wisdom=retrieve_wisdom,
    update_wisdom=update_wisdom,
    estimate_entropy=estimate_entropy,
    estimate_info_gain=estimate_info_gain,
)

result = core.run_query("What is the difference between egotism and arrogance?")

print(f"Output type:  {result.output_type}")
print(f"Confidence:   {result.confidence:.2f}")
print(f"Passes used:  {result.wringer_passes_used}")
print(f"Halt reason:  {result.halt_reason.value}")
print(f"Output:       {result.output}")
```

---

## Step 3 — Handle All Three Output Types

Always branch on `result.output_type`:

```python
result = core.run_query(query)

if result.output_type == "convergence":
    # Engines agreed. output is the direct conclusion.
    print("Answer:", result.output)

elif result.output_type == "blend":
    # Partial agreement. output may be a structured blend dict.
    blend = result.output
    print("Blended answer:", blend)

elif result.output_type == "disagreement":
    # Irreducible disagreement. Show both perspectives.
    d = result.output
    print("Left perspective:", d["left"])
    print("Right perspective:", d["right"])
    print("The question cannot be resolved without choosing a frame.")
```

A `disagreement` result is not a failure — it is the correct answer when the question genuinely depends on unresolved assumptions.

---

## Step 4 — Add Wisdom Persistence

To accumulate reasoning memory across sessions:

```python
from theos_system import TheosSystem

system = TheosSystem(
    core=core,
    persistence_file="my_wisdom.json",
)

result = system.reason("My question")
metrics = system.get_metrics()
print(f"Total queries: {metrics.total_queries}")
print(f"Convergence rate: {metrics.convergence_rate:.0%}")
```

The wisdom JSON file is written after each query. On the next session, previously accumulated lessons are loaded and surfaced to both engines during abduction — sharpening their hypotheses based on past reasoning.

---

## Step 5 — Tune the Governor

| Goal | Adjustment |
|------|-----------|
| Faster, cheaper reasoning | Lower `max_wringer_passes` (e.g., 2–3) |
| Deeper reasoning | Raise `max_wringer_passes` (e.g., 10+) |
| Stricter convergence required | Lower `eps_converge` (e.g., 0.02) |
| Accept more partial agreement | Raise `eps_partial` (e.g., 0.7) |
| More per-engine introspection | Raise `engine_reflection_depth` (e.g., 3) |
| No self-reflection | Set `engine_reflection_depth=1` |
| Unlimited budget | Leave `budget=None` |
| Token-cost cap | Set `budget=10000` (token count) |

---

## Existing Domain Examples

The `examples/` directory contains three complete domain implementations:

| File | Domain | Key operator pattern |
|------|--------|---------------------|
| `theos_medical_diagnosis.py` | Medical diagnosis | Symptom → differential diagnosis; right engine checks contraindications |
| `theos_financial_analysis.py` | Financial decisions | Left: upside case; right: downside risk |
| `theos_ai_safety.py` | AI safety evaluation | Left: capability maximization; right: safety / alignment |

These are the canonical implementation references.

---

## Self-Reflection — The Key Difference

The `prev_own_deduction` argument to `induce_patterns` is what makes THEOS architecturally novel. On the **second inner pass**, each engine receives its own first-pass deduction as feedback. This is not shared — the left engine sees only its own prior, and the right engine sees only its own prior.

```python
def induce_patterns(obs, prev_phi, prev_own_deduction):
    if prev_own_deduction is None:
        # First inner pass: form initial patterns
        return extract_first_pass_patterns(obs)
    else:
        # Second inner pass: reason about your own conclusion
        # This is second-order cognition: thought about thought.
        return refine_patterns_from_own_prior(obs, prev_own_deduction)
```

Engines that ignore `prev_own_deduction` still work — they just lose the self-reflection benefit.

---

*[API Reference](api) · [Integration Guide](integration) · [Troubleshooting](troubleshooting)*
