---
layout: default
title: Architecture — THEOS
---

<p align="center"><img src="{{ site.baseurl }}/assets/theos_logo.png" alt="THEOS" width="110"></p>

# Architecture

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
