# THEOS Latest #56
## Engine Interaction & Governor Control State Machine

### Purpose
This document defines the **formal state machine** governing interaction between:
- Engine A (CW)
- Engine B (CCW)
- The Governor

This is the execution backbone of THEOS.

---

## Core States

State {
    INIT
    SINGLE_ENGINE_ACTIVE
    DUAL_ENGINE_ACTIVE
    CONTRADICTION_COMPRESSION
    GOVERNOR_EVALUATION
    TERMINAL_OUTPUT
}

---

## State Transitions

INIT →
    SINGLE_ENGINE_ACTIVE
    OR
    DUAL_ENGINE_ACTIVE

SINGLE_ENGINE_ACTIVE →
    GOVERNOR_EVALUATION

DUAL_ENGINE_ACTIVE →
    CONTRADICTION_COMPRESSION →
    GOVERNOR_EVALUATION

GOVERNOR_EVALUATION →
    CONTINUE → (back to engine state)
    SWAP → DUAL_ENGINE_ACTIVE
    DISENGAGE → SINGLE_ENGINE_ACTIVE
    STOP → TERMINAL_OUTPUT
    REFUSE → TERMINAL_OUTPUT

---

## Governor Control Rules

1. Governor selects initial state based on task risk profile.
2. Governor determines:
   - Number of triadic cycles
   - Engine engagement
   - Contradiction pressure
3. Governor may disengage Engine B if:
   - Similarity exceeds convergence threshold
4. Governor may re-engage Engine B if:
   - Stagnation or asymmetry is detected
5. Engines may never self-terminate or self-swap.

---

## Contradiction Compression Phase

During CONTRADICTION_COMPRESSION:
- Outputs from Engine A and Engine B are aligned
- Differences are isolated
- Noise is discarded
- Structured disagreement is preserved
- Resulting delta is passed upward to Governor

This phase is mandatory whenever both engines are active.

---

## Temporal Consequence Handling

Each completed cycle creates:
- A prior state
- A measurable consequence
- A candidate wisdom delta

Governor decides whether:
- The delta is written to Wisdom Store
- The delta is discarded
- Additional cycles are required

---

## Hard Invariants

- Engines cannot bypass the Governor
- Governor cannot skip contradiction evaluation
- No terminal output without Governor authorization
- No recursion without state carry-forward

---

## Status
LOCKED — EXECUTION CANONICAL — NON-OPTIONAL
