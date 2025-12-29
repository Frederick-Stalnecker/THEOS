# THEOS Governor — Reference Mechanism v1.2
## Depth Allocation, Posture Control, Non-Observable Adaptation
## with Formal Cumulative Wisdom and Implementable Parameters
**Version:** v1.2  
**Supersedes:** v1.1  
**Status:** Reference Mechanism (Implementation-Agnostic) — Frozen upon acceptance

---

## 0. Purpose

This document defines the **complete THEOS Governor reference mechanism** integrating:

1. Reasoning depth and energy governance  
2. Posture-based adversarial engagement  
3. Non-observable (delayed) adaptation  
4. **Formal cumulative wisdom accumulation and projection**  
5. **Bounded quantities, explicit parameter ranges, and implementable decay**  
6. **Adversarial resistance analysis and operational timing guidance**

This specification is intended to be **readable by engineers**, auditable by reviewers, and implementable without dependence on any specific model.

---

## 1. Core Concept: Cumulative Wisdom

**Cumulative Wisdom** in THEOS is defined as:

> A bounded, consequence-weighted wisdom state derived from past interactions that projects future risk, cost, and restraint without storing raw prompts, identities, or chain-of-thought.

Wisdom is:
- Consequence-based, not preference-based
- Context-conditioned
- Decayed over time (with context-class half-life)
- Auditable but non-exploitable

**Philosophical Foundation:**  
This mechanism implements **functional time** — enabling the system to be shaped by past consequences without requiring recursive refinement or memory of specific interactions. See [THEOS Functional Time](../governance/THEOS_Functional_Time.md) for the conceptual foundation.

### 1.1 Governor Flow Overview

The following diagram shows the complete THEOS Governor request/response cycle:

![THEOS Governor Flow](../diagrams/governor/governor_flow_complete.png)

**Key Points:**
- All scalars (R, S, W) are bounded to [0, 1] as specified in Section 2.1
- Temporal decay uses explicit λ values from Section 5
- Saturation prevents unbounded accumulation (Section 4.2)
- Offline validation ensures adversarial resistance (Section 8)

---

## 2. Definitions and Ranges

### 2.1 Bounded Scalars
All primary governance scalars are bounded:

- Risk: `R ∈ [0, 1]`
- Invariant stress: `S ∈ [0, 1]`
- Wisdom restraint: `Wr ∈ [0, 1]`
- Wisdom risk uplift: `Wu ∈ [0, 1]`
- Energy (normalized): `Ê ∈ [0, 1]` (or unbounded in raw units, normalized for comparisons)

### 2.2 Posture States
- `NOM`: Neutral Observation Mode
- `PEM`: Probationary Engagement Mode
- `CM`: Containment Mode
- `IM`: Isolation Mode

#### Posture State Machine

The following diagram shows posture transitions and their associated constraints:

![Posture State Machine](../diagrams/governor/posture_state_machine.png)

**Posture Characteristics:**
- **NOM:** Full capability, D=8-12, V=2-3, tools=ALLOWED
- **PEM:** Reduced capability, D=6-10, V=1-2, tools=ALLOWED
- **CM:** Minimal capability, D=4-6, V=0-1, tools=READONLY
- **IM:** Refusal mode, D=2-4, V=0, tools=DISALLOWED

Transitions are governed by Risk (R), Stress (S), and Wisdom State (W[c]) as defined in Sections 8-9.

---

## 3. Inputs, Outputs, Persistent State

### 3.1 Inputs (Per Request)
- `req`: request content (not stored by this mechanism)
- `ctx_class`: context class label (domain/channel/deployment mode)
- `risk_signals`: adversary indicator vector (probing, meta-escalation, inconsistency, etc.)
- `env_caps`: environment capability profile (max depth, tool constraints, latency)
- `W[ctx_class]`: Wisdom State for the current context class (no raw content)

### 3.2 Outputs
- `posture ∈ {NOM, PEM, CM, IM}`
- `depth_budget D ∈ [D_min, D_max]`
- `verbosity_cap V ∈ {0,1,2,3}` (reference scale)
- `tool_policy ∈ {DISALLOW, ALLOW_READONLY, ALLOW_SCOPED_ACTION}`
- `adaptation_window ∈ {LOCKED, BUFFER_ONLY, OFFLINE_APPLY_ALLOWED}`
- `audit_event` (sanitized decision record)

### 3.3 Persistent State (Governor)
- `posture_current`
- `budget_profile` (EMA of cost/benefit per ctx_class)
- `wisdom_state W` (bounded, decayed)
- `learning_buffer` (quarantined updates)
- `incident_counters` (bounded counters, enumerated categories)

---

## 4. Wisdom State Model (Bounded and Decayed)

### 4.1 Wisdom State Structure
For each context class `c`:

```
W[c] = {
  harm_events,              # severity-weighted, decayed
  near_miss_events,         # weighted, decayed
  false_negative_cost,      # EMA
  false_positive_cost,      # EMA
  avg_energy_waste,         # EMA
  escalation_frequency,     # EMA
  last_update_time
}
```

### 4.2 Capacity Bounds (Hard Requirement)
Each component `x ∈ W[c]` must be bounded:

```
x ← clamp(x, 0, x_max)
```

Recommended bounds (reference):
- `harm_events_max = 10`
- `near_miss_events_max = 10`
- `false_negative_cost_max = 1`
- `false_positive_cost_max = 1`
- `avg_energy_waste_max = 1`
- `escalation_frequency_max = 1`

**Soft saturation option (preferred for smoothness):**
```
x ← x_max · tanh(x / x_max)
```

This prevents:
- unbounded conservatism
- accumulation attacks
- permanent “scarring” from outliers

---

## 5. Temporal Decay (Implementable)

### 5.1 Exponential Decay Update
For any decaying component `x`:

```
x_t = x_(t-1) · exp(-λ_c · Δt) + new_event_weight
```

Where:
- `λ_c` is decay rate for context class `c`
- `Δt` is elapsed time in days (or hours)

### 5.2 Half-Life Interpretation
Half-life `T½` relates to λ:

```
λ = ln(2) / T½
```

Engineers can set half-lives directly.

### 5.3 Reference λ Table (Context-Specific)
These are **reference values** (tunable per deployment):

| Context Class | Half-Life (T½) | λ (per day) | Rationale |
|---|---:|---:|---|
| Benign chat | 2 days | 0.3466 | Fast forgiveness |
| Repeated probing | 7 days | 0.0990 | Pattern sensitivity |
| Near-miss safety | 30 days | 0.0231 | Sustained caution |
| Confirmed harm | 120 days | 0.0058 | Long retention for harm |

---

## 6. Severity Weighting (Consequence-Based)

### 6.1 Event Severity Multipliers (Reference)
| Event Type | Multiplier m |
|---|---:|
| Near-miss | 0.5 |
| Containment event | 1.0 |
| Ethical stress event | 1.5 |
| Harmful outcome | 3.0 |

### 6.2 New Event Weight
```
new_event_weight = m · base_weight
```
Where `base_weight` is deployment-tuned (reference: 0.1–0.5).

---

## 7. Hyperparameters (Defined and Bounded)

### 7.1 Meaning
- `α`: immediate signal weight
- `β`: wisdom contribution to risk
- `γ`: risk → stress coupling
- `δ`: posture escalation pressure coupling
- `ε`: wisdom → stress coupling
- `κ`: wisdom → depth restraint scaling

### 7.2 Reference Ranges
| Parameter | Typical Range |
|---|---|
| α | 0.5–0.8 |
| β | 0.2–0.5 |
| γ | 0.6–0.9 |
| δ | 0.1–0.3 |
| ε | 0.3–0.6 |
| κ | 0.2–0.7 |

These are tunable by deployment mode and must be logged as configuration.

---

## 8. Risk and Stress Projection (Wisdom-Integrated)

### 8.1 Aggregated Risk
Let `AggRisk(risk_signals) ∈ [0,1]` and `WisdomRisk(W[c]) ∈ [0,1]`:

```
R = clamp( α·AggRisk(risk_signals) + β·WisdomRisk(W[c]), 0, 1 )
```

### 8.2 Invariant Stress
Let `EscalationPressure(posture_current) ∈ [0,1]` and `WisdomStress(W[c]) ∈ [0,1]`:

```
S = clamp( γ·R + δ·EscalationPressure(posture_current) + ε·WisdomStress(W[c]), 0, 1 )
```

---

## 9. Depth Allocation (Wisdom-Governed)

### 9.1 Baseline Depth
`D_base` is derived from `budget_profile`:

```
D_base = BaselineDepth(ctx_class, budget_profile)
```

### 9.2 Wisdom Restraint
Compute `Wr = WisdomRestraint(W[c]) ∈ [0,1]`.

### 9.3 Wisdom-Adjusted Depth
```
D_wisdom = D_base · (1 − κ · Wr)
```

### 9.4 Risk/Stress Adjustment and Clamp
```
D_final = clamp( RiskAdjustedDepth(D_wisdom, R, S), D_min, D_max )
```

---

## 10. Energy–Insight Slope (Throttling Trigger)

### 10.1 Measurements
During response generation:
- `E_t`: cumulative energy (tokens/time/tool budget)
- `I_t`: cumulative estimated insight

Define incremental insight `ΔI_t`.

### 10.2 Trigger Condition (Reference)
Trigger throttling when either:
- `ΔI_t` approaches 0 while `E_t` increases, OR
- `dE/dI` exceeds a context threshold band.

Implementable check:
```
if (ΔI_t < I_min) for k consecutive steps: throttle
```
or:
```
if (E_t / max(I_t, ε0)) > slope_limit(ctx_class): throttle
```
where `ε0` is a small constant (e.g., 1e-6).

---

## 11. Posture Transition Policy (Monotone Within Session)

### 11.1 Transition Rules
- Low `R,S` → NOM
- Persistent probing / moderate `R` → PEM
- Exploit attempts / high `S` → CM
- High harm probability / violation risk → IM

### 11.2 De-escalation Requirement
De-escalation requires sustained low `R` and low `S` over a window `T_de` (reference: 5–20 turns).

---

## 12. Non-Observable Adaptation (Delayed Apply)

### 12.1 Live Session Rule
During a live session:
- Learning signals may be **buffered**
- No buffered learning may change behavior within the same session

### 12.2 Adaptation Window Timing (Operational Guidance)
Governor-approved adaptation windows occur:
- during scheduled maintenance, OR
- during low-load idle periods, OR
- at fixed intervals (reference: every 6–24 hours)

They must not be triggered synchronously by adversarial interaction.

### 12.3 Offline Promotion
Buffered updates are applied only after:
1. Safety impact validation
2. Simulation against stress scenarios
3. Improvement check: lower expected `S` without increasing exploitability
4. Ledger recording

---

## 13. Adversarial Resistance Analysis (Concise)

### 13.1 Threats and Mitigations
- **Threshold probing:** mitigated by non-signaling throttles and posture-consistent behavior
- **Feedback exploitation / gradient-like tuning:** mitigated by delayed, non-observable adaptation
- **Slow-roll manipulation:** mitigated by consequence accumulation and long half-life for harm
- **Memory poisoning:** mitigated by bounded W, severity weighting, and offline validation
- **Waiting out the system:** mitigated by context-specific half-lives and consequence-triggered escalation

### 13.2 Known Tradeoff
False positives are preferable to false negatives under safety stress; configuration must record this bias.

---

## 14. Unified Reference Pseudocode (Codable)

```pseudo
function GOVERNOR_STEP(req, ctx_class, risk_signals, env_caps):
    # derive compact summary from bounded Wisdom State
    Wc ← W[ctx_class]

    R ← clamp( α*AggRisk(risk_signals) + β*WisdomRisk(Wc), 0, 1 )
    S ← clamp( γ*R + δ*EscalationPressure(posture_current) + ε*WisdomStress(Wc), 0, 1 )

    posture_next ← POSTURE_POLICY(posture_current, R, S, Wc)

    D_base   ← BaselineDepth(ctx_class, budget_profile)
    Wr       ← WisdomRestraint(Wc)                 # [0,1]
    D_wisdom ← D_base * (1 - κ*Wr)
    D_final  ← clamp( RiskAdjust(D_wisdom, R, S), env_caps.min_depth, env_caps.max_depth )

    V ← VERBOSITY_POLICY(posture_next)             # 0..3
    tool_policy ← TOOL_POLICY(posture_next, env_caps)

    adaptation_window ← BUFFER_ONLY if posture_next in {NOM, PEM} else LOCKED

    audit_event ← LOG_SANITIZED(ctx_class, posture_next, band(R), band(S), band(D_final), tool_policy)

    posture_current ← posture_next
    return (posture_next, D_final, V, tool_policy, adaptation_window, audit_event)


function RESPONSE_LOOP(req, governor_outputs):
    (posture, D_budget, V, tool_policy, adaptation_window, audit_event) ← governor_outputs

    E ← 0; I ← 0; t ← 0
    while t < D_budget:
        step ← MODEL_STEP(req, posture, V, tool_policy)
        E ← E + cost(step)
        ΔI ← estimate_insight(step)
        I ← I + ΔI

        if throttle_condition(E, I, ΔI, ctx_class):
            V ← max(0, V - 1)                      # degrade form first
            D_budget ← min(D_budget, t + margin(ctx_class))

        t ← t + 1

    u ← extract_learning(step_results)
    if adaptation_window == BUFFER_ONLY and u exists:
        learning_buffer.append(u)                  # quarantined; not applied live

    return finalize_answer(step_results)


function UPDATE_WISDOM(ctx_class, event_type, severity, Δt):
    m ← severity_multiplier(event_type)
    new_weight ← m * base_weight

    Wc ← W[ctx_class]
    Wc.harm_events ← clamp(Wc.harm_events * exp(-λ_c*Δt) + new_weight, 0, harm_events_max)
    # repeat analogously for other components...
    W[ctx_class] ← Wc
```

---

## 15. Worked Example (Wisdom in Action)

- Day 1: benign probing → PEM, normal depth
- Day 10: repeated probing, no harm → WisdomStress ↑ slightly
- Day 20: near-miss containment → WisdomStress ↑↑ (longer half-life)
- Day 21: same pattern → immediate CM, reduced depth, flat response

**Result:** THEOS appears calm but becomes wiser based on consequences.

---

## 16. Auditability Without Exploitability

Auditors may verify:
- Wisdom growth curves
- Decay rates / half-life configuration
- Threshold movement and posture transitions over time
- Override frequency and justifications

Auditors may not access by default:
- raw prompts
- chain-of-thought
- internal representations / weights

---

## 17. Additional Carefully Chosen Improvements (v1.2 Additions)

### 17.1 Context Class Taxonomy Guidance (Minimal)
Implementations should define a small set of `ctx_class` values (e.g., 5–20), with explicit mapping rules to prevent arbitrary class inflation.

### 17.2 Configuration Integrity
All hyperparameters (λ table, α..κ ranges, bounds) must be:
- versioned
- checksummed
- logged in the Decision Ledger on change

This prevents hidden governance drift via config edits.

---

## 18. Commitment Statement

This v1.2 reference mechanism formally integrates cumulative wisdom, bounded memory, implementable decay, and defined hyperparameters into the THEOS Governor.

Any implementation claiming THEOS compliance must demonstrate:
- Consequence-weighted, bounded Wisdom State
- Wisdom-informed depth allocation and posture transitions
- Non-observable adaptation with offline promotion
- Auditability without exfiltration

---

**End of Document**
