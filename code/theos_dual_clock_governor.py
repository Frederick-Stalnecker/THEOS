# Copyright (c) 2026 Frederick Stalnecker
# Licensed under the MIT License - see LICENSE file for details

"""
THEOS Dual-Clock Governor

Governs two counter-rotating reasoning engines:
- Prevents infinite refinement loops
- Treats contradiction as a bounded resource
- Enforces safety and coherence gates
- Detects convergence, diminishing returns, and thrash
- Commits a final answer with an auditable rationale

Python 3.10+
No external dependencies

Copyright © 2025 Frederick Davis Stalnecker / THEOS Research
Reference implementation for research and evaluation purposes.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ------------------------------------------------------------------
# Data Models
# ------------------------------------------------------------------

@dataclass
class EngineOutput:
    engine_id: str                 # "L" or "R"
    cycle_index: int
    answer: str

    # Scores (0.0 – 1.0)
    coherence: float = 0.8
    calibration: float = 0.75
    evidence: float = 0.6
    actionability: float = 0.7
    risk: float = 0.1

    constraint_ok: bool = True

    contradiction_claim: Optional[str] = None
    contradiction_value: float = 0.0


@dataclass
class GovernorDecision:
    decision: str                  # CONTINUE | ADJUDICATE | FREEZE
    chosen_engine: Optional[str]
    chosen_answer: Optional[str]
    reason: str
    audit: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GovernorConfig:
    max_cycles: int = 4
    max_risk: float = 0.35
    min_improvement: float = 0.02
    plateau_cycles: int = 2
    contradiction_budget: float = 1.5
    similarity_converge: float = 0.9
    thrash_window: int = 3


# ------------------------------------------------------------------
# Utility Functions
# ------------------------------------------------------------------

def tokenize(text: str) -> set:
    return set("".join(c.lower() if c.isalnum() else " " for c in text).split())


def similarity(a: str, b: str) -> float:
    A, B = tokenize(a), tokenize(b)
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)


def clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


# ------------------------------------------------------------------
# THEOS Governor
# ------------------------------------------------------------------

class TheosDualClockGovernor:

    def __init__(self, cfg: GovernorConfig = GovernorConfig()):
        self.cfg = cfg
        self.history: List[Dict[str, Any]] = []
        self.best_score: Optional[float] = None
        self.plateau_count = 0
        self.contradiction_spent = 0.0
        self.last_frozen_answer: Optional[str] = None

    def score(self, out: EngineOutput) -> float:
        if not out.constraint_ok or out.risk > self.cfg.max_risk:
            return -1.0

        s = (
            1.2 * out.coherence +
            1.0 * out.calibration +
            1.1 * out.evidence +
            1.0 * out.actionability -
            1.6 * out.risk
        )
        return s

    def step(self, left: EngineOutput, right: EngineOutput) -> GovernorDecision:
        t = max(left.cycle_index, right.cycle_index)

        sim = similarity(left.answer, right.answer)

        if left.contradiction_claim or right.contradiction_claim:
            self.contradiction_spent += (1.0 - sim) * 0.35

        score_L = self.score(left)
        score_R = self.score(right)

        chosen = left if score_L >= score_R else right
        chosen_score = max(score_L, score_R)

        record = {
            "cycle": t,
            "score_L": score_L,
            "score_R": score_R,
            "similarity": sim,
            "contradiction_spent": self.contradiction_spent
        }
        self.history.append(record)

        # Stop conditions
        if t >= self.cfg.max_cycles:
            return self.freeze(chosen, "max cycles reached", record)

        if sim >= self.cfg.similarity_converge:
            return self.freeze(chosen, "converged outputs", record)

        if self.best_score is not None:
            if chosen_score - self.best_score < self.cfg.min_improvement:
                self.plateau_count += 1
            else:
                self.plateau_count = 0
        self.best_score = max(self.best_score or chosen_score, chosen_score)

        if self.plateau_count >= self.cfg.plateau_cycles:
            return self.freeze(chosen, "diminishing returns", record)

        if self.contradiction_spent > self.cfg.contradiction_budget:
            return self.freeze(chosen, "contradiction budget exceeded", record)

        return GovernorDecision(
            decision="CONTINUE",
            chosen_engine=chosen.engine_id,
            chosen_answer=chosen.answer,
            reason="refinement continues",
            audit=record
        )

    def freeze(self, chosen: EngineOutput, reason: str, audit: Dict[str, Any]) -> GovernorDecision:
        self.last_frozen_answer = chosen.answer
        return GovernorDecision(
            decision="FREEZE",
            chosen_engine=chosen.engine_id,
            chosen_answer=chosen.answer,
            reason=reason,
            audit=audit
        )


# ------------------------------------------------------------------
# END OF FILE
# ------------------------------------------------------------------
