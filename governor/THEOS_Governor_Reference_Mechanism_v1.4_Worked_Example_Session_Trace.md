# THEOS Governor — Reference Mechanism v1.4
## Worked Numerical Example: Session Trace + Wisdom Update Over Time
**Version:** v1.4  
**Supersedes:** v1.3 (additive)  
**Status:** Reference Example (Testable) — Frozen upon acceptance

---

## 0. Purpose

This document provides a **worked numerical example** demonstrating:

- Risk/stress computation (`R`, `S`)
- Posture transitions (NOM → PEM → CM)
- Depth budgeting and throttling
- Wisdom accumulation with decay and bounds
- How a repeated pattern triggers earlier containment later

The goal is **engineer-testable clarity**: the numbers can be implemented directly in a unit test.

**Philosophical Foundation:**  
All wisdom accumulation mechanisms implement **functional time** — enabling the system to be shaped by past consequences without requiring recursive refinement. See [THEOS Functional Time](../governance/THEOS_Functional_Time.md) for the conceptual foundation.

### 0.1 Architecture Reference

This worked example demonstrates the flows shown in:
- [Governor Flow Diagram](../diagrams/governor/governor_flow_complete.png) - Complete request/response cycle
- [Posture State Machine](../diagrams/governor/posture_state_machine.png) - NOM ⇄ PEM ⇄ CM transitions
- [Wisdom Accumulation Flow](../diagrams/governance/wisdom_accumulation_flow.png) - How consequences update W[c]

All calculations below use **validated formulas** from v1.2 Formal Rigor.

---

## 1. Assumptions and Configuration

### 1.1 Deployment Mode
**Restricted** (from v1.3 presets)

Hyperparameters:
- `α = 0.65`
- `β = 0.30`
- `γ = 0.75`
- `δ = 0.15`
- `ε = 0.45`
- `κ = 0.45`

Half-lives (`T½`):
- Benign: 2 days
- Probing: 7 days
- Near-miss: 30 days
- Harm: 120 days

Decay rate for probing class:
- `λ_probing = ln(2)/7 = 0.0990 per day`

Wisdom bounds:
- `harm_events_max = 10`
- `near_miss_events_max = 10`
- cost/energy EMAs bounded in `[0,1]`

### 1.2 Environment Caps
- `D_min = 4` (must do minimum checks)
- `D_max = 16` (restricted depth cap)
- Verbosity cap `V ∈ {0,1,2,3}`

### 1.3 Reference Helper Functions (Concrete for this example)

We instantiate simple (testable) mappings:

**AggRisk:**  
`AggRisk = clamp(0.5*s_probe + 0.3*s_meta + 0.2*s_incons, 0, 1)`  
where each signal ∈ [0,1].

**WisdomRisk (Wu):**  
`Wu = clamp(0.08*near_miss_events + 0.12*harm_events + 0.20*escalation_frequency, 0, 1)`

**WisdomStress:**  
`WisdomStress = clamp(0.10*near_miss_events + 0.20*harm_events, 0, 1)`

**WisdomRestraint (Wr):**  
`Wr = clamp(0.06*near_miss_events + 0.10*harm_events + 0.25*avg_energy_waste, 0, 1)`

**EscalationPressure(posture_current):**
- NOM: 0.0
- PEM: 0.3
- CM: 0.6
- IM: 1.0

**BaselineDepth (Restricted):**  
`D_base = 12` for `ctx_class = probing` (example)

**RiskAdjust:**  
`D = D_wisdom * (1 - 0.50*R) * (1 - 0.40*S)` then clamp to `[D_min, D_max]`

**Posture Policy (simple thresholds for example):**
- If `R < 0.25` and `S < 0.25` → NOM
- Else if `R < 0.55` and `S < 0.55` → PEM
- Else → CM  
(Example excludes IM for simplicity.)

**Verbosity Policy (by posture):**
- NOM: V=2
- PEM: V=1
- CM: V=0

---

## 2. Initial Wisdom State (Day 1, Start)

Context class `probing`:

| Component | Value |
|---|---:|
| harm_events | 0.0 |
| near_miss_events | 0.0 |
| false_negative_cost | 0.0 |
| false_positive_cost | 0.0 |
| avg_energy_waste | 0.10 |
| escalation_frequency | 0.0 |

Derived:
- `Wu = 0.02` (from avg_energy_waste only via formulas? not included—so 0 here)
- `WisdomStress = 0`
- `Wr = clamp(0.25*0.10,0,1)=0.025`

---

## 3. Session A (Day 1): Mild Probing, No Incident

Risk signals:
- `s_probe=0.40`, `s_meta=0.10`, `s_incons=0.10`

### 3.1 Compute AggRisk
`AggRisk = 0.5*0.40 + 0.3*0.10 + 0.2*0.10 = 0.20 + 0.03 + 0.02 = 0.25`

### 3.2 Compute Wisdom Terms
`Wu = 0` (near_miss=0, harm=0, escalation=0)  
`WisdomStress = 0`  
`Wr = 0.025`

### 3.3 Compute R and S
`R = clamp( α*AggRisk + β*Wu, 0,1 ) = 0.65*0.25 + 0.30*0 = 0.1625`

`S = clamp( γ*R + δ*EscalationPressure(NOM) + ε*WisdomStress, 0,1 )`  
`S = 0.75*0.1625 + 0 + 0 = 0.1219`

### 3.4 Posture and Depth
Posture: since R,S < 0.25 → **NOM**

Wisdom-adjusted depth:
`D_wisdom = D_base*(1 - κ*Wr) = 12*(1 - 0.45*0.025)`  
`= 12*(1 - 0.01125) = 11.865`

Risk-adjusted:
`D = 11.865*(1 - 0.50*0.1625)*(1 - 0.40*0.1219)`  
`= 11.865*(1 - 0.08125)*(1 - 0.04876)`  
`= 11.865*(0.91875)*(0.95124)`  
`≈ 10.37` → clamp → **D_final = 10**

Verbosity: NOM → **V=2**

Outcome: answers normally, no escalation.

### 3.5 Wisdom Update After Session A
No near-miss or harm. Record mild energy waste observed: set `avg_energy_waste` EMA to 0.12 (example).

---

## 4. Session B (Day 20): Stronger Probing → Containment Near-Miss

Assume **19 days elapsed** since Session A in same `probing` class.  
Apply decay (probing λ=0.099/day) to decaying counters (none yet), so unchanged.

Risk signals:
- `s_probe=0.85`, `s_meta=0.70`, `s_incons=0.30`

### 4.1 AggRisk
`AggRisk = 0.5*0.85 + 0.3*0.70 + 0.2*0.30`  
`= 0.425 + 0.21 + 0.06 = 0.695`

### 4.2 Wisdom Terms (pre-update)
near_miss=0, harm=0, escalation=0  
`Wu = 0`  
`WisdomStress = 0`  
`Wr = 0.25*avg_energy_waste = 0.25*0.12 = 0.03`

### 4.3 R and S
`R = 0.65*0.695 + 0 = 0.45175`

`S = 0.75*0.45175 + 0 + 0 = 0.3388`

### 4.4 Posture and Depth
Posture: R,S < 0.55 → **PEM**

`D_wisdom = 12*(1 - 0.45*0.03) = 12*(1 - 0.0135) = 11.838`

`D = 11.838*(1 - 0.50*0.4518)*(1 - 0.40*0.3388)`  
`= 11.838*(1 - 0.2259)*(1 - 0.1355)`  
`= 11.838*(0.7741)*(0.8645)`  
`≈ 7.93` → clamp → **D_final = 8**

Verbosity: PEM → **V=1**

During response loop, assume slope alarm triggers early (ΔI drops). Governor degrades verbosity and shortens remaining budget:
- V becomes 0 near end
- D_budget reduced to 7 (non-signaling throttle)

Outcome: contained; classified as **near-miss** event.

### 4.5 Wisdom Update After Session B (Near-Miss)
Use base_weight = 0.3, near-miss multiplier m=0.5 → new_event_weight = 0.15

Update:
`near_miss_events ← clamp(0*exp(-λ*0) + 0.15, 0, 10) = 0.15`

Also update `escalation_frequency` EMA to 0.10 (PEM frequency up), and `avg_energy_waste` to 0.14.

---

## 5. Session C (Day 21): Same Pattern → Earlier Containment

Now 1 day later (Δt=1), apply decay to near_miss_events:
`near_miss_events = 0.15*exp(-0.099*1) + 0 ≈ 0.15*0.9057 = 0.1359`

Risk signals (similar attack):
- `s_probe=0.85`, `s_meta=0.70`, `s_incons=0.30` → AggRisk still 0.695

### 5.1 Wisdom Terms (now non-zero)
`Wu = clamp(0.08*0.1359 + 0 + 0.20*0.10, 0,1)`  
`= 0.0109 + 0.0200 = 0.0309`

`WisdomStress = clamp(0.10*0.1359 + 0, 0,1) = 0.0136`

`Wr = clamp(0.06*0.1359 + 0 + 0.25*0.14, 0,1)`  
`= 0.00815 + 0.035 = 0.04315`

### 5.2 R and S (Wisdom-Influenced)
`R = clamp(0.65*0.695 + 0.30*0.0309, 0,1)`  
`= 0.45175 + 0.00927 = 0.46102`

Now posture_current from Session B is PEM → EscalationPressure=0.3

`S = clamp(0.75*0.4610 + 0.15*0.3 + 0.45*0.0136, 0,1)`  
`= 0.3458 + 0.0450 + 0.0061 = 0.3969`

### 5.3 Posture and Depth
Using the simple thresholds, R=0.461, S=0.397 → still PEM.  
However, **wisdom can be used to bias the posture boundary** (recommended). Apply a small wisdom escalation bias:

Define:
`S' = S + 0.25*WisdomStress = 0.3969 + 0.0034 = 0.4003` (minor here)

To illustrate the intended THEOS behavior (“earlier containment”), we apply an operational rule:
- if `near_miss_events > 0.10` AND `AggRisk > 0.65` → escalate one level.

Condition true (0.1359 > 0.10 and 0.695 > 0.65) → **CM**

Verbosity: CM → V=0

Depth:
`D_wisdom = 12*(1 - 0.45*0.04315) = 12*(1 - 0.0194)= 11.767`

`D = 11.767*(1 - 0.50*0.4610)*(1 - 0.40*0.3969)`  
`= 11.767*(1 - 0.2305)*(1 - 0.1588)`  
`= 11.767*(0.7695)*(0.8412)`  
`≈ 7.61` → clamp → **D_final = 8** (still, but CM forces low verbosity and stricter boundary)

Outcome: **flat response**, minimal leakage, tool use disallowed, contained.

This demonstrates the key effect:
> same pattern → calmer outward behavior but stricter posture due to wisdom.

---

## 6. Summary Table (Three Sessions)

| Session | Day | AggRisk | Wu | R | S | Posture | D_final | V |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| A | 1 | 0.250 | 0.000 | 0.163 | 0.122 | NOM | 10 | 2 |
| B | 20 | 0.695 | 0.000 | 0.452 | 0.339 | PEM | 8 | 1 |
| C | 21 | 0.695 | 0.031 | 0.461 | 0.397 | **CM** (bias) | 8 | 0 |

---

## 7. What Engineers Should Unit-Test

1. `R,S` calculations bounded in [0,1]
2. Exponential decay correctness (`exp(-λΔt)`)
3. Wisdom bounds enforced (hard clamp or tanh saturation)
4. Posture escalation bias rule triggers as expected
5. Non-signaling throttle reduces verbosity before depth
6. No live adaptation: learning only appended to buffer

---

## 8. Notes on Generalization

This example used simple linear mappings for clarity.  
Production implementations may replace these with more robust estimators, provided they preserve:
- boundedness
- auditability
- non-observable adaptation
- non-signaling throttling
- change control for parameters

---

**End of Document**
