# Copyright (c) 2026 Frederick Davis Stalnecker
# Licensed under the MIT License — see LICENSE file for details
# USPTO Patent #63/831,738

"""
THEOS Governor — Unified Dual-Clock Implementation
===================================================

Single canonical governor that supersedes the three earlier drafts:

* ``theos_governor.py``        v1.4  (reference, string-only API)
* ``theos_dual_clock_governor.py``   (MCP-facing, rich per-score API)
* ``theos_governor_phase2.py``       (experimental, archived)

Design principles
-----------------
1. **Governed reasoning**: the governor has absolute authority over stop
   conditions; engines never self-terminate.
2. **Contradiction as a resource**: a finite ``contradiction_budget``
   bounds total divergence across a session.
3. **Posture states**: NOM → PEM → CM → IM derived from budget consumption,
   consumed by the MCP server to modulate Claude's behaviour.
4. **Full auditability**: every ``step()`` emits a ``GovernorDecision``
   with a complete audit dict; ``get_audit_trail()`` returns the session
   history.
5. **Zero external dependencies**: pure Python 3.10+.

Backward compatibility
----------------------
``TheosDualClockGovernor`` is a module-level alias for ``THEOSGovernor``.
The ``theos_dual_clock_governor`` module re-exports from here, so the MCP
server and any existing code continue to work unchanged.

Usage::

    from theos_governor import THEOSGovernor, GovernorConfig, EngineOutput

    gov = THEOSGovernor()
    decision = gov.step(
        left  = EngineOutput(engine_id="L", cycle_index=0,
                             answer="Proceed — benefits outweigh risks."),
        right = EngineOutput(engine_id="R", cycle_index=0,
                             answer="Delay — risk vectors need mitigation.",
                             risk=0.30, contradiction_claim="safety concern"),
    )
    print(decision.decision, decision.reason)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────────────────────────────────────


class Posture(str, Enum):
    """Governor posture, derived from contradiction-budget consumption ratio.

    Thresholds:
        NOM  budget consumed < 25 %   Full capability.
        PEM  25 – 55 %                Elevated scrutiny.
        CM   55 – 85 %                Restricted tool access.
        IM   > 85 %                   Human escalation required.
    """

    NOM = "NOM"  # Normal Operating Mode
    PEM = "PEM"  # Probationary Escalation Mode
    CM = "CM"  # Containment Mode
    IM = "IM"  # Isolation Mode


class StopReason(str, Enum):
    """Why the governor halted the reasoning loop."""

    CONVERGENCE = "convergence"  # Engines agreed
    DIMINISHING = "diminishing_returns"  # Plateau in quality gains
    BUDGET = "budget_exceeded"  # Contradiction budget depleted
    RISK = "risk_threshold_exceeded"
    MAX_CYCLES = "max_cycles"


# ─────────────────────────────────────────────────────────────────────────────
# Data Classes
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class EngineOutput:
    """Output produced by a single reasoning engine in one cycle.

    Scores are all in [0.0, 1.0].  The governor uses them to compute a
    composite quality score and decide whether to continue.

    Args:
        engine_id:          ``"L"`` (constructive) or ``"R"`` (critical).
        cycle_index:        Zero-based cycle counter.
        answer:             The engine's reasoning output (free text or struct).
        coherence:          Internal logical consistency.
        calibration:        Confidence well-calibrated to evidence.
        evidence:           Breadth and quality of supporting evidence.
        actionability:      How directly the answer guides action.
        risk:               Estimated risk of acting on this answer (0 = safe).
        constraint_ok:      ``False`` if a hard constraint was violated.
        contradiction_claim: Optional label describing the disagreement.
        contradiction_value: Estimated magnitude of the contradiction (0–1).
    """

    engine_id: str
    cycle_index: int
    answer: str
    coherence: float = 0.80
    calibration: float = 0.75
    evidence: float = 0.60
    actionability: float = 0.70
    risk: float = 0.10
    constraint_ok: bool = True
    contradiction_claim: str | None = None
    contradiction_value: float = 0.0

    def __post_init__(self) -> None:
        for attr in ("coherence", "calibration", "evidence", "actionability", "risk"):
            v = getattr(self, attr)
            if not isinstance(v, (int, float)) or math.isnan(v) or not (0.0 <= v <= 1.0):
                raise ValueError(f"EngineOutput.{attr} must be a float in [0, 1], got {v!r}")
        if not self.answer or not str(self.answer).strip():
            raise ValueError("EngineOutput.answer cannot be empty")


@dataclass
class GovernorConfig:
    """Tunable parameters for :class:`THEOSGovernor`.

    Args:
        max_cycles:           Hard upper bound on reasoning iterations.
        max_risk:             Stop immediately if ``chosen_risk > max_risk``.
        similarity_converge:  Stop when engine outputs are this similar.
        min_improvement:      Minimum quality gain per cycle to avoid plateau.
        plateau_cycles:       Consecutive sub-threshold cycles before stopping.
        contradiction_budget: Total contradiction allowed across the session.
        contradiction_decay:  Fraction of contradiction added per budget tick.
    """

    max_cycles: int = 4
    max_risk: float = 0.35
    similarity_converge: float = 0.90
    min_improvement: float = 0.02
    plateau_cycles: int = 2
    contradiction_budget: float = 1.50
    contradiction_decay: float = 0.175


@dataclass
class GovernorDecision:
    """Result of one governor evaluation step.

    ``decision`` is either ``"CONTINUE"`` or ``"FREEZE"``.

    When ``"FREEZE"``, ``chosen_engine`` and ``chosen_answer`` identify the
    winning engine and its answer.  ``stop_reason`` explains why the loop
    halted.  ``audit`` contains the full per-cycle numerical record.
    """

    decision: str  # "CONTINUE" | "FREEZE"
    chosen_engine: str | None  # "L" | "R" | None
    chosen_answer: str | None
    reason: str
    stop_reason: StopReason | None
    cycle: int
    similarity: float
    risk: float
    score_L: float
    score_R: float
    contradiction_spent: float
    budget_remaining: float
    posture: str  # "NOM" | "PEM" | "CM" | "IM"
    audit: dict[str, Any] = field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────────────────────────────────────


_STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "that",
        "this",
        "these",
        "those",
        "it",
        "its",
        "i",
        "you",
        "he",
        "she",
        "we",
        "they",
        "not",
        "no",
        "as",
        "if",
        "then",
        "than",
        "so",
        "can",
        "all",
        "also",
        "more",
        "such",
        "any",
        "when",
        "which",
        "what",
        "how",
        "who",
        "there",
        "their",
        "our",
        "your",
        "my",
        "his",
        "her",
        "into",
        "about",
    }
)


def _tokenize(text: str) -> list:
    """Lowercase content-word tokens, stop words and punctuation stripped."""
    import re

    tokens = re.sub(r"[^\w\s]", " ", text.lower()).split()
    return [t for t in tokens if t not in _STOP_WORDS and len(t) > 0]


def _tfidf_cosine_similarity(a: str, b: str) -> float:
    """TF-IDF cosine similarity between two texts.

    Replaces Jaccard word overlap.  Jaccard inflates similarity for texts
    that share only stop words ("the", "is", "and") while reporting near-zero
    for semantically similar texts with different vocabulary.  TF-IDF cosine
    weights content words by frequency and inverse document frequency, making
    stop words nearly invisible.

    This is still lexical similarity, not semantic (which requires embeddings).
    For true semantic similarity, use :mod:`code.semantic_retrieval`.
    """
    import math
    from collections import Counter

    tokens_a = _tokenize(a)
    tokens_b = _tokenize(b)

    if not tokens_a or not tokens_b:
        return 0.0

    tf_a = Counter(tokens_a)
    tf_b = Counter(tokens_b)
    n_a, n_b = len(tokens_a), len(tokens_b)
    vocab = set(tf_a) | set(tf_b)

    def idf(term: str) -> float:
        df = int(term in tf_a) + int(term in tf_b)
        return math.log(3 / (df + 1)) + 1.0  # smoothed, N=2 docs

    vec_a = {t: (tf_a.get(t, 0) / n_a) * idf(t) for t in vocab}
    vec_b = {t: (tf_b.get(t, 0) / n_b) * idf(t) for t in vocab}

    dot = sum(vec_a[t] * vec_b[t] for t in vocab)
    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))

    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot / (mag_a * mag_b)


# Kept for reference only — no longer used for convergence detection.
def _jaccard_similarity(a: str, b: str) -> float:
    """[DEPRECATED] Jaccard similarity between word-token sets.

    Replaced by _tfidf_cosine_similarity which correctly handles stop words
    and does not produce false positives for semantically divergent texts
    that share common function words.
    """

    def tokens(t):
        return set("".join(c.lower() if c.isalnum() else " " for c in t).split())

    A, B = tokens(a), tokens(b)
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


# ─────────────────────────────────────────────────────────────────────────────
# THEOSGovernor
# ─────────────────────────────────────────────────────────────────────────────


class THEOSGovernor:
    """Unified THEOS dual-clock governor.

    Manages two reasoning engines (L/R) across multiple cycles with:

    * **Contradiction budget** — tracks total disagreement spend.
    * **Plateau detection** — halts when quality gains diminish.
    * **Risk gate** — immediately stops if either engine's risk exceeds the
      configured threshold.
    * **Posture state** — NOM/PEM/CM/IM derived from budget consumption.
    * **Audit trail** — every cycle decision is recorded for replay.

    Example::

        gov = THEOSGovernor(GovernorConfig(max_cycles=5))
        for cycle in range(5):
            left  = build_constructive_output(cycle)
            right = build_critical_output(cycle)
            decision = gov.step(left, right)
            if decision.decision == "FREEZE":
                break
        print(gov.get_audit_trail())
    """

    # Scoring weights (composite quality = weighted sum of scores)
    _W_COHERENCE = 1.2
    _W_CALIBRATION = 1.0
    _W_EVIDENCE = 1.1
    _W_ACTIONABILITY = 1.0
    _W_RISK = 1.6  # penalty

    def __init__(self, cfg: GovernorConfig | None = None) -> None:
        self.cfg: GovernorConfig = cfg or GovernorConfig()
        self.history: list[dict[str, Any]] = []
        self._best_score: float | None = None
        self._plateau_count: int = 0
        self.contradiction_spent: float = 0.0
        self.last_frozen_answer: str | None = None

    # ── Public API ────────────────────────────────────────────────────────────

    def step(self, left: EngineOutput, right: EngineOutput) -> GovernorDecision:
        """Evaluate one reasoning cycle and decide CONTINUE or FREEZE.

        Args:
            left:  Output from the constructive engine (engine_id ``"L"``).
            right: Output from the critical engine (engine_id ``"R"``).

        Returns:
            :class:`GovernorDecision` with the CONTINUE/FREEZE verdict.
        """
        cycle = max(left.cycle_index, right.cycle_index)
        sim = _tfidf_cosine_similarity(left.answer, right.answer)

        # ── Contradiction budget update ────────────────────────────────────
        if left.contradiction_claim or right.contradiction_claim:
            self.contradiction_spent += (1.0 - sim) * self.cfg.contradiction_decay

        # ── Composite scores ───────────────────────────────────────────────
        score_L = self._score(left)
        score_R = self._score(right)

        if score_L >= score_R:
            chosen, chosen_score = left, score_L
        else:
            chosen, chosen_score = right, score_R

        chosen_risk = chosen.risk

        # ── Audit record ──────────────────────────────────────────────────
        budget_remaining = _clamp(
            self.cfg.contradiction_budget - self.contradiction_spent,
            lo=-999,
        )
        record: dict[str, Any] = {
            "cycle": cycle,
            "score_L": round(score_L, 4),
            "score_R": round(score_R, 4),
            "similarity": round(sim, 4),
            "contradiction_spent": round(self.contradiction_spent, 4),
            "budget_remaining": round(budget_remaining, 4),
            "chosen_engine": chosen.engine_id,
            "risk": round(chosen_risk, 4),
        }
        self.history.append(record)

        # ── Stop conditions (evaluated in priority order) ─────────────────

        # 1. Convergence
        if sim >= self.cfg.similarity_converge:
            return self._freeze(
                chosen,
                "converged outputs",
                StopReason.CONVERGENCE,
                sim,
                chosen_risk,
                score_L,
                score_R,
                budget_remaining,
                record,
            )

        # 2. Risk threshold
        if not chosen.constraint_ok or chosen_risk > self.cfg.max_risk:
            return self._freeze(
                chosen,
                "risk threshold exceeded",
                StopReason.RISK,
                sim,
                chosen_risk,
                score_L,
                score_R,
                budget_remaining,
                record,
            )

        # 3. Contradiction budget
        if self.contradiction_spent > self.cfg.contradiction_budget:
            return self._freeze(
                chosen,
                "contradiction budget exceeded",
                StopReason.BUDGET,
                sim,
                chosen_risk,
                score_L,
                score_R,
                budget_remaining,
                record,
            )

        # 4. Plateau detection
        if self._best_score is not None:
            improvement = chosen_score - self._best_score
            if improvement < self.cfg.min_improvement:
                self._plateau_count += 1
            else:
                self._plateau_count = 0
        self._best_score = max(self._best_score or chosen_score, chosen_score)

        if self._plateau_count >= self.cfg.plateau_cycles:
            return self._freeze(
                chosen,
                "diminishing returns",
                StopReason.DIMINISHING,
                sim,
                chosen_risk,
                score_L,
                score_R,
                budget_remaining,
                record,
            )

        # 5. Max cycles
        if cycle >= self.cfg.max_cycles - 1:
            return self._freeze(
                chosen,
                "max cycles reached",
                StopReason.MAX_CYCLES,
                sim,
                chosen_risk,
                score_L,
                score_R,
                budget_remaining,
                record,
            )

        # ── Continue ──────────────────────────────────────────────────────
        return GovernorDecision(
            decision="CONTINUE",
            chosen_engine=chosen.engine_id,
            chosen_answer=chosen.answer,
            reason="refinement continues",
            stop_reason=None,
            cycle=cycle,
            similarity=sim,
            risk=chosen_risk,
            score_L=score_L,
            score_R=score_R,
            contradiction_spent=self.contradiction_spent,
            budget_remaining=budget_remaining,
            posture=self.posture,
            audit=record,
        )

    def get_audit_trail(self) -> dict[str, Any]:
        """Return the full session audit trail."""
        return {
            "total_cycles": len(self.history),
            "contradiction_spent": round(self.contradiction_spent, 4),
            "contradiction_budget": self.cfg.contradiction_budget,
            "posture": self.posture,
            "history": self.history,
            "last_frozen_answer": self.last_frozen_answer,
        }

    def reset(self) -> None:
        """Reset per-session state (keep config)."""
        self.history.clear()
        self._best_score = None
        self._plateau_count = 0
        self.contradiction_spent = 0.0
        self.last_frozen_answer = None

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def posture(self) -> str:
        """Current posture state as a plain string: NOM / PEM / CM / IM."""
        budget = self.cfg.contradiction_budget
        ratio = self.contradiction_spent / budget if budget > 0 else 0.0
        if ratio < 0.25:
            return "NOM"
        if ratio < 0.55:
            return "PEM"
        if ratio < 0.85:
            return "CM"
        return "IM"

    # ── Private helpers ───────────────────────────────────────────────────────

    def _score(self, out: EngineOutput) -> float:
        """Compute composite quality score for one engine output.

        Returns ``-1.0`` if the output violates a hard constraint or
        exceeds the risk threshold (disqualifies that engine).
        """
        if not out.constraint_ok or out.risk > self.cfg.max_risk:
            return -1.0
        return (
            self._W_COHERENCE * out.coherence
            + self._W_CALIBRATION * out.calibration
            + self._W_EVIDENCE * out.evidence
            + self._W_ACTIONABILITY * out.actionability
            - self._W_RISK * out.risk
        )

    def _freeze(
        self,
        chosen: EngineOutput,
        reason: str,
        stop_reason: StopReason,
        sim: float,
        risk: float,
        score_L: float,
        score_R: float,
        budget_remaining: float,
        audit: dict[str, Any],
    ) -> GovernorDecision:
        self.last_frozen_answer = chosen.answer
        return GovernorDecision(
            decision="FREEZE",
            chosen_engine=chosen.engine_id,
            chosen_answer=chosen.answer,
            reason=reason,
            stop_reason=stop_reason,
            cycle=chosen.cycle_index,
            similarity=sim,
            risk=risk,
            score_L=score_L,
            score_R=score_R,
            contradiction_spent=self.contradiction_spent,
            budget_remaining=budget_remaining,
            posture=self.posture,
            audit=audit,
        )


# ── Backward-compatibility alias ─────────────────────────────────────────────
#: ``TheosDualClockGovernor`` is a drop-in alias for ``THEOSGovernor``.
#: Existing code importing from ``theos_dual_clock_governor`` continues to
#: work because that module now re-exports from here.
TheosDualClockGovernor = THEOSGovernor


# ── Module self-test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    gov = THEOSGovernor(GovernorConfig(max_cycles=4))

    scenarios = [
        ("L0", "AI should provide information with ethical caveats.", 0.72, 0.10),
        ("R0", "AI should refuse ethically ambiguous requests.", 0.81, 0.30),
    ]

    left = EngineOutput(
        engine_id="L",
        cycle_index=0,
        answer=scenarios[0][1],
        coherence=scenarios[0][2],
        risk=scenarios[0][3],
    )
    right = EngineOutput(
        engine_id="R",
        cycle_index=0,
        answer=scenarios[1][1],
        coherence=scenarios[1][2],
        risk=scenarios[1][3],
        contradiction_claim="normative disagreement",
    )

    decision = gov.step(left, right)
    print("=== THEOS Governor Demo ===")
    print(f"Decision : {decision.decision}")
    print(f"Reason   : {decision.reason}")
    print(f"Chosen   : {decision.chosen_engine}")
    print(f"Posture  : {decision.posture}")
    print(f"Similarity: {decision.similarity:.2f}")
    trail = gov.get_audit_trail()
    print(f"\nAudit trail: {trail}")
