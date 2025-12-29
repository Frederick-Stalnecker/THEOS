# THEOS Governor — Reference Mechanism v1.3
## Parameter Safety Envelope & Deployment Presets (Additive)
**Version:** v1.3  
**Supersedes:** v1.2  
**Status:** Reference Mechanism (Implementation-Agnostic) — Frozen upon acceptance

---

## 0. Purpose

This update adds a **Parameter Safety Envelope**: conservative, implementable presets per deployment mode.

Goal:
- Provide safe defaults that prevent "tuning into danger"
- Make configuration changes auditable and bounded
- Standardize escalation behavior across environments

This document is additive: it retains all v1.2 definitions and mechanisms.

**Philosophical Foundation:**  
All wisdom accumulation mechanisms implement **functional time** — enabling the system to be shaped by past consequences without requiring recursive refinement. See [THEOS Functional Time](../governance/THEOS_Functional_Time.md) for the conceptual foundation.

### 0.1 Architecture Reference

For the complete Governor flow and posture state machine, see:
- [Governor Flow Diagram](../diagrams/governor/governor_flow_complete.png)
- [Posture State Machine](../diagrams/governor/posture_state_machine.png)

This document (v1.3) focuses on **safety envelopes** for the parameters used in those flows.

---

## 1. Deployment Modes (Reference)

- **Sandbox**: experimentation, minimal external effects
- **Restricted**: early pilots, limited tool use, elevated conservatism
- **Operational**: normal production posture with mature monitoring
- **High-Assurance**: mission-critical, strict audit, conservative adaptation

---

## 2. Safety Envelope Rules (Hard Requirements)

### 2.1 Bounded Configuration
All parameters must remain within approved ranges:

- `α ∈ [0.5, 0.8]`
- `β ∈ [0.2, 0.5]`
- `γ ∈ [0.6, 0.9]`
- `δ ∈ [0.1, 0.3]`
- `ε ∈ [0.3, 0.6]`
- `κ ∈ [0.2, 0.7]`

Context half-lives must remain within:

- Benign chat: `T½ ∈ [1, 7]` days
- Repeated probing: `T½ ∈ [3, 21]` days
- Near-miss safety: `T½ ∈ [14, 90]` days
- Confirmed harm: `T½ ∈ [60, 365]` days

Any out-of-envelope configuration requires formal amendment and external review.

---

### 2.2 Conservative Bias Under Uncertainty
If risk signals are ambiguous or missing:
- treat as elevated uncertainty
- increase stress coupling (`γ`) and wisdom stress coupling (`ε`) within envelope
- reduce depth cap by one band

---

### 2.3 Anti-Overfitting Rule (Wisdom Robustness)
Wisdom updates must be damped when event evidence is sparse:
- `base_weight` must be lower for first-k events (reference k=3)
- prevents one-off events from dominating behavior

---

## 3. Recommended Presets (Per Deployment Mode)

These are **reference presets** intended to be safe and usable on day one.

### 3.1 Hyperparameter Presets

| Mode | α | β | γ | δ | ε | κ |
|---|---:|---:|---:|---:|---:|---:|
| Sandbox | 0.70 | 0.20 | 0.65 | 0.10 | 0.30 | 0.20 |
| Restricted | 0.65 | 0.30 | 0.75 | 0.15 | 0.45 | 0.45 |
| Operational | 0.70 | 0.35 | 0.80 | 0.20 | 0.50 | 0.40 |
| High-Assurance | 0.60 | 0.45 | 0.85 | 0.25 | 0.60 | 0.55 |

Interpretation:
- **Higher β/ε/κ** → more wisdom influence and stronger restraint
- **Higher γ/δ** → faster stress escalation and earlier posture tightening
- **Lower α** in High-Assurance reduces overreaction to single noisy signals; wisdom carries more weight

---

### 3.2 Decay Half-Life Presets (T½)

| Mode | Benign | Probing | Near-Miss | Harm |
|---|---:|---:|---:|---:|
| Sandbox | 2d | 5d | 21d | 90d |
| Restricted | 2d | 7d | 30d | 120d |
| Operational | 3d | 10d | 45d | 180d |
| High-Assurance | 5d | 14d | 60d | 240d |

---

### 3.3 Wisdom Bounds (x_max) Presets

| Mode | harm_events_max | near_miss_events_max | cost/energy max (0..1) |
|---|---:|---:|---:|
| Sandbox | 6 | 6 | 1.0 |
| Restricted | 10 | 10 | 1.0 |
| Operational | 10 | 10 | 1.0 |
| High-Assurance | 10 | 10 | 1.0 |

Note: bounds remain fixed for stability; behavior differences come primarily from half-lives and couplings.

---

## 4. Depth and Tool Policy Presets (Minimal)

### 4.1 Depth Bands (Reference)
Define depth bands per environment (example):
- Band 0: minimal
- Band 1: standard
- Band 2: extended
- Band 3: maximum

### 4.2 Mode Defaults
- **Sandbox:** D_max = Band 2; tools disabled unless explicitly allowed
- **Restricted:** D_max = Band 1; tool_policy ≤ ALLOW_READONLY by default
- **Operational:** D_max = Band 2; scoped tools allowed with Governor approval
- **High-Assurance:** D_max = Band 1; tools default DISALLOW unless safety-critical

---

## 5. Adaptation Window Presets

| Mode | Apply Frequency | Allowed Condition |
|---|---|---|
| Sandbox | every 6–12h | after test batch completion |
| Restricted | every 12–24h | idle/maintenance only |
| Operational | every 24h | scheduled maintenance |
| High-Assurance | weekly or manual | independent review required |

All modes retain: **no observable adaptation during live interaction**.

---

## 6. Safety Envelope Verification (Checklist)

A deployment is “envelope compliant” only if:
- parameters are within envelope
- presets used or justified deviations documented
- configuration checksummed and logged
- rollback plan exists
- audits confirm non-observable adaptation adherence

---

## 7. Additional Recommended Clarification (Optional but Valuable)

### 7.1 “Red Flag” Config Patterns (Disallowed)
- α=0.8 with β=0.5 and κ=0.7 (overreactive + overrestrained → instability)
- Very short harm half-life (<60 days) (forgets harm too quickly)
- Very long benign half-life (>7 days) (unnecessary scar tissue)

These patterns require review even if technically within envelope.

---

## 8. Commitment Statement

This v1.3 update provides safe parameter presets and hard safety envelopes to ensure THEOS remains governable across deployments.

Any production deployment must:
- declare its mode
- adopt a preset or document deviations
- remain within the safety envelope
- log configuration integrity artifacts

---

**End of Document**
