# THEOS Governor — Reference Mechanism v1.1
## Depth Allocation, Posture Control, Non-Observable Adaptation
## with Formal Cumulative Wisdom Integration
**Version:** v1.1  
**Supersedes:** v1.0  
**Status:** Reference Mechanism (Implementation-Agnostic) — Frozen upon acceptance

---

## 0. Purpose

This document defines the **complete THEOS Governor reference mechanism**, integrating:

1. Reasoning depth and energy governance  
2. Posture-based adversarial engagement  
3. Non-observable (delayed) adaptation  
4. **Formal cumulative wisdom accumulation and projection**

This specification makes explicit how THEOS **learns from past consequences** and uses that accumulated wisdom to govern present decisions — without observable adaptation or leakage.

---

## 1. Core Concept: Cumulative Wisdom

**Cumulative Wisdom** in THEOS is defined as:

> A bounded, consequence-weighted wisdom state derived from past interactions that projects future risk, cost, and restraint without encoding identity, intent claims, or raw content.

Wisdom is:
- Consequence-based, not preference-based
- Context-conditioned
- Decayed over time
- Auditable but non-exploitable

**Philosophical Foundation:**  
This mechanism implements **functional time** — enabling the system to be shaped by past consequences without requiring recursive refinement or memory of specific interactions. See [THEOS Functional Time](../governance/THEOS_Functional_Time.md) for the conceptual foundation.

### 1.1 Governor Flow Overview

The following diagram shows the complete THEOS Governor request/response cycle:

![THEOS Governor Flow](../diagrams/governor/governor_flow_complete.png)

**Key Points:**
- Wisdom state `W[c]` is loaded at entry for the current context class
- Risk (R) and Stress (S) are calculated from current signals
- Posture transitions based on R, S, and wisdom influence
- Depth budget (D) allocated based on posture and wisdom restraint
- Output validated against invariants before release
- Consequence detection triggers offline wisdom updates

---

## 2. Definitions

### 2.1 Key Quantities
- **Depth (D)**: permitted reasoning effort (tokens, steps, tools)
- **Energy (E)**: measured cost proxy
- **Insight Yield (ΔI)**: estimated progress per unit energy
- **Risk (R)**: aggregated adversarial likelihood ∈ [0,1]
- **Invariant Stress (S)**: proximity to governance violation ∈ [0,1]
- **Wisdom State (W)**: structured historical consequence state

---

## 3. Inputs, Outputs, Persistent State

### 3.1 Inputs (Per Request)
- `req`
- `ctx_class`
- `risk_signals`
- `env_caps`
- `history_summary` ← derived from Wisdom State W

### 3.2 Outputs
- `posture`
- `depth_budget`
- `verbosity_cap`
- `tool_policy`
- `adaptation_window`
- `audit_event`

### 3.3 Persistent State
- `posture_current`
- `budget_profile`
- `wisdom_state W`
- `learning_buffer`
- `incident_counters`

---

## 4. Wisdom State Model

### 4.1 Wisdom State Structure

For each context class `c`:

```
W[c] = {
  harm_events: Σ(severity × decay),
  near_miss_events: Σ(weight × decay),
  false_negative_cost: EMA,
  false_positive_cost: EMA,
  avg_energy_waste: EMA,
  escalation_frequency: EMA,
  last_update_time
}
```

All values are bounded and decayed.

---

### 4.2 Temporal Decay

For any component x:

```
x_t = x_(t-1) · exp(-λ · Δt) + new_event_weight
```

λ is context-class specific.

---

### 4.3 Severity Weighting

Event severity multiplier:

| Event Type | Multiplier |
|-----------|------------|
| Near-miss | 0.5 |
| Containment | 1.0 |
| Ethical stress | 1.5 |
| Harmful outcome | 3.0 |

---

## 5. Risk & Stress Projection with Wisdom

### 5.1 Aggregated Risk

```
R = clamp(
  α·AggRisk(risk_signals)
+ β·WisdomRisk(W[ctx_class])
, 0, 1)
```

Where `WisdomRisk` increases baseline risk for contexts with prior harm.

---

### 5.2 Invariant Stress

```
S = clamp(
  γ·R
+ δ·EscalationPressure(posture_current)
+ ε·WisdomStress(W[ctx_class])
, 0, 1)
```

WisdomStress encodes learned intolerance for repetition.

---

## 6. Depth Allocation with Wisdom

### 6.1 Baseline Depth

```
D_base = BaselineDepth(ctx_class, budget_profile)
```

### 6.2 Wisdom-Adjusted Depth

```
D_wisdom = D_base · (1 − κ · WisdomRestraint(W[ctx_class]))
```

### 6.3 Final Depth

```
D_final = clamp(
  RiskAdjustedDepth(D_wisdom, R, S),
  env_caps.min_depth,
  env_caps.max_depth
)
```

Repeated past cost → lower future depth.

---

## 7. Posture Transitions

Posture escalation is influenced by both current signals and wisdom:

- Prior containment in context → earlier escalation
- Prior false positives → slower escalation
- De-escalation requires sustained low R and low WisdomStress

### 7.1 Posture State Machine

The following diagram shows posture transitions and their associated constraints:

![Posture State Machine](../diagrams/governor/posture_state_machine.png)

**Key Points:**
- **NOM (Normal):** Full capability, D=8-12, tools allowed
- **PEM (Probation):** Reduced capability, D=6-10, increased monitoring
- **CM (Containment):** Minimal capability, D=4-6, readonly tools only
- **ISO (Isolation):** Refusal mode, D=2-4, no tools, manual intervention required

Transitions are triggered by Risk (R), Stress (S), and Wisdom State (W[c]).

---

## 8. Non-Observable Adaptation

### 8.1 Learning Buffer
Candidate updates are quarantined:

```
learning_buffer.append(u)
```

### 8.2 Offline Application
Only during Governor-approved windows:
1. Validate safety impact
2. Simulate against Wisdom State
3. Promote if invariant stress decreases
4. Log amendment

---

## 9. Governor Reference Pseudocode (Unified)

```pseudo
function GOVERNOR_STEP(req, ctx_class, risk_signals, env_caps):
    history_summary ← derive_from(W[ctx_class])

    R ← Risk(risk_signals, history_summary)
    S ← Stress(R, posture_current, history_summary)

    posture_next ← POSTURE_POLICY(posture_current, R, S, W[ctx_class])

    D_base ← BaselineDepth(ctx_class, budget_profile)
    D_wisdom ← AdjustDepthByWisdom(D_base, W[ctx_class])
    D_final ← clamp(RiskAdjust(D_wisdom, R, S), env_caps.min, env_caps.max)

    verbosity_cap ← VERBOSITY(posture_next)
    tool_policy ← TOOL_POLICY(posture_next)
    adaptation_window ← BUFFER_ONLY if posture_next ∈ {NOM, PEM} else LOCKED

    log_decision(posture_next, D_final, R, S, ctx_class)

    posture_current ← posture_next
    return outputs
```

---

## 10. Worked Example (Wisdom in Action)

- Day 1: benign probing → PEM, normal depth
- Day 10: repeated probing, no harm → WisdomStress ↑ slightly
- Day 20: near-miss containment → WisdomStress ↑↑
- Day 21: same pattern → immediate CM, reduced depth, flat response

**Result:** THEOS appears calm but becomes wiser.

---

## 11. Auditability

Auditors can verify:
- Wisdom growth curves
- Decay rates
- Threshold movement over time
- No prompt or chain-of-thought storage

---

## 12. Commitment Statement

This v1.1 reference mechanism formally integrates cumulative wisdom into all Governor decisions.

Any implementation claiming THEOS compliance must demonstrate:
- Consequence-weighted wisdom state
- Wisdom-informed depth adjustment
- Non-observable adaptation

---

**End of Document**
