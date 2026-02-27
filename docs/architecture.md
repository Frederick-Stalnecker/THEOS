---
layout: default
title: Architecture — THEOS
---

<p align="center"><img src="{{ site.baseurl }}/assets/theos_logo.png" alt="THEOS" width="110"></p>

# Architecture — The Human Thought Model Made Computable

## The Architecture of Human Thought

Every great answer a human being produces emerges from a tension between two forces: the creative mind that generates possibility, and the critical mind that challenges it. This tension is not a flaw in human cognition. It is the mechanism of it.

THEOS makes that mechanism explicit and computable.

---

## The Two Engines

**The left engine runs clockwise.**
It is constructive — generative, language-forward, hypothesis-building. It takes the question, induces patterns, abduces its strongest hypothesis, and deduces a conclusion. Then it does something no single-pass AI does: it feeds that conclusion back into its own induction for a second pass, refining what it just thought in light of having thought it. This is the *momentary past*. The engine has a lived record of its own reasoning.

**The right engine runs counterclockwise.**
It is adversarial — skeptical, contradiction-seeking, structurally opposed. It runs the same I→A→D→I cycle but from the opposite posture. Its job is not to be wrong. Its job is to find every place the left engine's answer could fail.

These two engines do not compete. They collaborate through opposition — the same way the left and right hemispheres of the human brain produce thought together precisely *because* they see differently.

The governor holds the position the frontal lobe holds in the human brain: judgment, restraint, and the decision of when enough has been thought.

---

## The Wringer

THEOS structures reasoning as a wringer: two engines press against each other, with each cycle reducing contradiction until the governor halts.

```
           QUESTION / OBSERVATION
                    │
              ┌─────▼─────┐
              │  INDUCTION │  Extract patterns, identify tensions
              └─────┬─────┘
                    │
           ┌────────┴────────┐
           ▼                 ▼
    ┌─────────────┐   ┌─────────────┐
    │ ABDUCTION-L │   │ ABDUCTION-R │
    │ constructive│   │ adversarial │
    │ (best hyp.) │   │ (worst hyp.)│
    └──────┬──────┘   └──────┬──────┘
           │                 │
    ┌──────▼──────┐   ┌──────▼──────┐
    │ DEDUCTION-L │   │ DEDUCTION-R │
    │  D_L pass 1 │   │  D_R pass 1 │
    └──────┬──────┘   └──────┬──────┘
           │  private        │  private
           │  reflection     │  reflection
    ┌──────▼──────┐   ┌──────▼──────┐
    │  D_L* final │   │  D_R* final │
    └──────┬──────┘   └──────┬──────┘
           └────────┬────────┘
                    │
              ┌─────▼──────────────────────┐
              │  GOVERNOR                  │
              │  Φ = contradiction(D_L*, D_R*)│
              │                            │
              │  if Φ < ε:    CONVERGE ✓  │
              │  if Δ < ρ:    DIMINISH ✓  │
              │  if budget:   BUDGET  ✓   │
              │  else:        CONTINUE ↺  │
              └─────┬──────────────────────┘
                    │
             ┌──────▼──────┐
             │   OUTPUT    │
             │  + WISDOM   │  Accumulated for next query
             └─────────────┘
```

---

## The Three Output Types

When the governor halts, the output takes one of three forms:

| Type | When | Meaning |
|------|------|---------|
| **Convergence** | Φ < ε_converge | Engines agree. Output is D_L* directly. |
| **Blend** | Φ < ε_partial | Partial agreement. Output is w_L·D_L* + w_R·D_R*. |
| **Disagreement** | All else | Engines cannot converge. Output is the structured disagreement. |

The `disagreement` output is not a failure. It means: *this question cannot be answered without first deciding which frame applies.* Callers must handle all three cases.

---

## The Governor

The governor measures the contradiction Φ between the two deductions after every cycle. It does not stop at the first satisfactory answer — it sustains cycles of I→A→D→I until the best available answer has emerged from the tension between them. For a simple question this may take two or three cycles. For deeply nuanced questions — constitutional interpretation, novel scientific hypotheses, medical safety determinations — the engines may run through many cycles of contradiction and refinement, each pass surfacing structure the previous pass missed. Unexpected theoretical resolutions can emerge that neither engine could have produced alone. When Φ finally shrinks below ε, the engines have genuinely converged on a real answer. When Φ cannot shrink further, the governor reports irreducible disagreement — an honest answer in domains where certainty is impossible. In every case, the full reasoning trace is preserved and auditable.

**Transparency is not optional.** Every step — every induction, every hypothesis, every contradiction measurement, every governor decision — is observable and auditable. This is the design, not a feature. The glass cube is not a metaphor. You can see through it because nothing is hidden.

The governor (`code/theos_governor.py`) implements five stop conditions:

```python
# Stop if engines converged
if contradiction < config.eps_converge:
    return halt(HaltReason.CONVERGED)

# Stop on diminishing returns
if info_gain / prev_info_gain < config.rho_min:
    return halt(HaltReason.DIMINISHING_RETURNS)

# Stop if budget exhausted
if total_tokens > config.budget:
    return halt(HaltReason.BUDGET_EXHAUSTED)

# Stop on irreducible uncertainty
if entropy < config.entropy_min and contradiction > config.delta_min:
    return halt(HaltReason.IRREDUCIBLE_UNCERTAINTY)

# Stop after max cycles
if cycle >= config.max_wringer_passes:
    return halt(HaltReason.MAX_CYCLES)
```

The governor tracks a `contradiction_budget` across a session and adjusts its posture:
- **NOM** (Normal Operating Mode) — full capability
- **PEM** (Probationary Escalation) — reduced verbosity
- **CM** (Containment Mode) — restricted tool access
- **IM** (Isolation Mode) — human escalation required

---

## The Formal Math

The abduction step uses quality-bracket shrinkage:

```
A_L = argmax QA(H; I)    [left: highest explanatory quality]
A_R = argmin QA(H; I)    [right: lowest explanatory quality — adversarial]

Width_n = q_max - q_min  → 0 exponentially (Theorem 3.5)
```

Convergence is guaranteed when both engines update toward the center of the quality bracket each cycle. The width decreases exponentially with each pass.

The full formal proofs are in: `THEOS_Architecture/governor/` and the iCloud document *Theos Math version 2.pdf*.

---

## Key Implementation Files

| File | Purpose |
|------|---------|
| `code/theos_core.py` | TheosCore — I→A→D→I cycle, TheosConfig, TheosOutput, HaltReason |
| `code/theos_system.py` | TheosSystem — wrapper with metrics, history, wisdom persistence |
| `code/theos_governor.py` | THEOSGovernor — unified canonical governor (post-Feb 2026 rebuild) |
| `code/semantic_retrieval.py` | VectorStore ABC, InMemoryVectorStore, Chroma/FAISS stubs |
| `code/theos_mcp_server.py` | MCP server — exposes THEOS to Claude Desktop via stdio |
| `code/llm_adapter.py` | LLMAdapter ABC for Claude, GPT-4, Llama |

---

## Patent Status

Provisional patent application filed: USPTO 63/831,738

The I→A→D→I loop is claimed in the provisional. The specific abduction sub-structure (A_L = argmax QA(H; I), A_R = argmin QA(H; I), bracket shrinkage to zero) may be separately patentable — the patent attorney is being briefed.

Window: 12-month provisional closes approximately June 2026.

---

## License

MIT License — Frederick Davis Stalnecker, 2026

Commercial licensing available. Contact: see repository.
