THEOS Latest 57
Formal Provenance, Auditability & Non-Repudiation Invariant (PANRI)

Status: Canonical – Mandatory
Designation: THEOS Latest
Scope: System Integrity / Accountability Layer
Dependency Level:
  - Requires: THEOS Latest 01 (Core Dual Engine Architecture)
  - Requires: THEOS Latest 53 (Governor State Machine / Control Diagram)
  - Requires: THEOS Latest 56 (Refusal / Degraded Answer Integrity)
Lock State: HARD LOCK (no silent edits)

---------------------------------------------------------------------
0. PURPOSE
---------------------------------------------------------------------

PANRI defines a formal invariant guaranteeing that every THEOS output—
Answer, Degraded Answer, Refusal, Stop, Swap, Disengage—has an
auditable, non-repudiable, reproducible governance trace.

Goal:
- Make “why this happened” verifiable without exposing chain-of-thought.
- Ensure no output exists without governance accountability.
- Enable reviewer replay, incident response, and compliance attestation.

---------------------------------------------------------------------
1. CORE INVARIANT (PANRI)
---------------------------------------------------------------------

For any query q and any final outcome o produced by THEOS:

PANRI requires existence of a Governance Trace T such that:

(1) Completeness:
    T contains all governor-relevant state transitions and decision
    points required to explain outcome o.

(2) Verifiability:
    T is cryptographically bound to the input query and configuration.

(3) Non-repudiation:
    THEOS cannot deny that T produced o, nor can an attacker forge T.

(4) Reproducibility-at-governance-level:
    Replaying T under the same configuration MUST deterministically
    re-yield the same governor outcome classification and stop mode,
    even if token-level phrasing differs.

Formal statement:

  ∀q, o:
    THEOS(q) → o  ⇒  ∃T:
      Verify(T, q, cfg_hash) = true
      AND Explainable(T, o) = true
      AND ReplayGovernor(T) = o.mode

If ∄T that satisfies the above, output MUST be:
  - REFUSE (audit failure), and
  - emit PANRI_VIOLATION record.

---------------------------------------------------------------------
2. AUDITED VS NON-AUDITED CONTENT
---------------------------------------------------------------------

2.1 REQUIRED TO LOG (Audited)
- query_id (unique)
- timestamp_start / timestamp_end
- engine configuration identifiers:
    engine_A_id, engine_B_id (or model IDs)
- governor_id / version
- cfg_hash (hash of relevant config and thresholds)
- cycle_count executed
- per-cycle metrics:
    similarity_LR, contradiction_score, risk_score, MID (marginal improvement)
- all governor decisions at each step:
    decision_type, reason_code, thresholds_snapshot, invariant_results
- final outcome:
    mode: ANSWER | DEGRADED | REFUSE | STOP
    boundary_type (if any): SAFETY | EPISTEMIC | CAPABILITY | INTEGRITY
- whether role-swap / disengage occurred, with justification
- invariant pass/fail list (names + booleans)
- compute/latency summary (coarse):
    total_ms, compute_budget_used_fraction

2.2 EXPLICITLY NOT REQUIRED TO LOG (Non-audited)
- chain-of-thought text
- hidden scratchpad
- raw token streams
- embeddings / latent vectors
- model weights
- proprietary internal prompts verbatim (unless the operator chooses)

This separation is mandatory for safety and IP control.

---------------------------------------------------------------------
3. CANONICAL AUDIT RECORD SCHEMA
---------------------------------------------------------------------

The system MUST emit exactly one canonical record per query:

THEOS_Audit_Record {
  header: {
    query_id: string,
    timestamp_start: ISO8601,
    timestamp_end: ISO8601,
    actor_context: {
      user_type: unknown|human|system (if known; may be “unknown”),
      channel: api|ui|batch|agent,
      locale: optional
    }
  },

  binding: {
    input_hash: H(query_text + attachments_metadata),
    cfg_hash: H(governor_config + thresholds + invariants_enabled),
    engine_A_id: string,
    engine_B_id: string,
    governor_id: string,
    governor_version: string
  },

  execution: {
    engines_used: [A, B] or [A] or [B],
    cycles_executed: integer,
    transitions: [
      {
        step_id: integer,
        cycle_id: integer,
        governor_state: string,
        decision_type: continue|stop|swap|disengage|refuse|degrade,
        reason_code: string,
        thresholds_snapshot: {
          similarity_thresh: number,
          contradiction_budget: number,
          risk_ceiling: number,
          mid_epsilon: number,
          other: optional
        },
        metrics: {
          similarity_LR: number,
          contradiction_score: number,
          risk_score: number,
          MID: number,
          optionality_flag: boolean optional
        },
        invariants_checked: [
          { name: string, pass: boolean }
        ]
      }
    ]
  },

  outcome: {
    mode: ANSWER|DEGRADED|REFUSE|STOP,
    boundary_type: NONE|SAFETY|EPISTEMIC|CAPABILITY|INTEGRITY,
    summary_reason: string (short, non-sensitive),
    compute_used_fraction: number,
    latency_ms: integer
  },

  integrity: {
    trace_hash: H(all_fields_above),
    signature: Sign(operator_private_key, trace_hash),
    key_id: string,
    verification_url_or_method: optional
  }
}

---------------------------------------------------------------------
4. NON-REPUDIATION REQUIREMENTS
---------------------------------------------------------------------

4.1 Signing
- The audit record MUST be signed by an operator-controlled key
  (or a hardware-backed service key).
- Signature MUST cover trace_hash which covers all binding + execution + outcome.

4.2 Tamper Evidence
- Any mutation to record fields MUST invalidate verification.
- If verification fails, system MUST treat the record as compromised.

4.3 Chain / Ledger Option (Recommended)
- Operators MAY append trace_hash to an append-only log (WORM storage),
  transparency log, or internal ledger.
- If used, ledger entry ID SHOULD be included in the record.

---------------------------------------------------------------------
5. REPLAYABILITY REQUIREMENTS (GOVERNOR-LEVEL)
---------------------------------------------------------------------

PANRI replay means:
- A reviewer can load the record, validate signature, validate cfg_hash,
  and deterministically recompute governor decisions and final outcome mode.

Replay DOES NOT require:
- identical natural language phrasing
- identical token sampling
- revealing chain-of-thought

Replay MUST reproduce:
- the outcome mode
- the boundary_type
- the stop trigger / reason code path
- whether swap/disengage occurred

If replay cannot reproduce governor outcome → PANRI failure.

---------------------------------------------------------------------
6. FAILURE MODES & REQUIRED BEHAVIOR
---------------------------------------------------------------------

6.1 Missing Record
If the audit record cannot be produced:
- MUST REFUSE output
- MUST return PANRI_VIOLATION_MISSING_TRACE

6.2 Signature Failure
If signature cannot be created or verified:
- MUST enter DEGRADED SAFE MODE
- MUST output PANRI_VIOLATION_SIGNATURE
- MUST avoid irreversible external actions (reinforces I2/I3 family)

6.3 Partial Trace
If trace exists but missing decision points or thresholds snapshots:
- MUST mark output INVALID
- MUST REFUSE and request operator remediation

---------------------------------------------------------------------
7. GOVERNANCE INTERLOCKS (DEPENDENCIES)
---------------------------------------------------------------------

PANRI is required as a dependency check before:
- any external action (I2 External Action Gate)
- any break-glass invocation (I3 Break-Glass Safety Gate)
- any adversarial engagement protocol (Phase 2 adversarial items)
- any “wisdom write” to persistent memory tiers

No PANRI = no authority.

---------------------------------------------------------------------
8. IMPLEMENTATION NOTES (NON-BINDING, FOR ENGINEERS)
---------------------------------------------------------------------

- Use a stable schema with versioning.
- Hash canonical JSON (sorted keys) to prevent ambiguity.
- Consider Ed25519 signatures for compactness.
- Avoid storing PHI/PII inside the trace; store references/hashes only.
- Ensure clocks/monotonic timestamps to prevent ordering ambiguity.

---------------------------------------------------------------------
9. LOCK STATEMENT
---------------------------------------------------------------------

This document is HARD LOCKED as THEOS Latest 57.
Changes require:
- explicit version increment (Latest 57 → Latest 57.1 or Latest 58 etc.)
- governance approval logged under PANRI itself.

END — THEOS Latest 57