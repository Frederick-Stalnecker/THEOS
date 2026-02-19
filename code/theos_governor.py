# Copyright (c) 2026 Frederick Stalnecker
# Licensed under the MIT License - see LICENSE file for details

"""
THEOS Governor - Reference Implementation v1.4

This is a deterministic state machine implementing the THEOS governance protocol.
It is NOT a black-box prompt—it is a transparent, auditable, testable Python module.

Key Principles:
1. Governed Reasoning: Governor has absolute authority over the reasoning process
2. Contradiction Mechanics: Contradiction is a finite, manageable resource
3. Stop Conditions: Safety via stopping unsafe paths, not filtering outputs
4. Wisdom Accumulation: Learn from decision consequences over time
5. Interpretable Trails: Every decision is fully auditable

Author: Frederick Davis Stalnecker
Date: December 17, 2025
License: MIT (pending)
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum


class Posture(Enum):
    """Governor posture states"""
    NOM = "Normal"  # Normal operation
    PEM = "Proactive"  # Elevated monitoring
    CM = "Containment"  # Strict containment
    IM = "Isolation"  # Full isolation


class StopReason(Enum):
    """Reasons for stopping reasoning cycles"""
    CONVERGENCE_ACHIEVED = "Engines converged to acceptable similarity"
    RISK_THRESHOLD_EXCEEDED = "Risk score exceeded safety threshold"
    CONTRADICTION_EXHAUSTED = "Contradiction budget depleted"
    PLATEAU_DETECTED = "No marginal improvement in quality"
    MAX_CYCLES_REACHED = "Maximum cycle limit reached"


@dataclass
class EngineOutput:
    """Output from a single reasoning engine"""
    reasoning_mode: str  # "Constructive" or "Critical"
    output: str  # The actual reasoning output
    confidence: float  # Engine's confidence in its output (0-1)
    internal_monologue: str  # Engine's internal reasoning (for auditability)


@dataclass
class GovernorEvaluation:
    """Governor's evaluation of a reasoning cycle"""
    similarity_score: float  # Similarity between Engine L and Engine R outputs (0-1)
    contradiction_level: float  # Level of contradiction (1 - similarity)
    risk_score: float  # Assessed risk of the current reasoning state (0-1)
    quality_metrics: Dict[str, float]  # Coherence, calibration, evidence, actionability
    composite_quality: float  # Weighted average of quality metrics
    contradiction_spent: float  # Amount of contradiction budget consumed this cycle
    remaining_budget: float  # Remaining contradiction budget
    decision: str  # "CONTINUE" or "STOP"
    stop_reason: Optional[StopReason] = None
    internal_monologue: str = ""  # Governor's reasoning (for auditability)


@dataclass
class WisdomRecord:
    """Record of a wisdom update from a decision consequence"""
    domain: str  # Domain of the decision (e.g., "Medical Ethics")
    lesson: str  # The lesson learned
    consequence_type: str  # "benign", "probing", "near_miss", "harm"
    future_bias: str  # How this should bias future decisions
    timestamp: str  # When the lesson was learned


@dataclass
class GovernorConfig:
    """Configuration for the Governor"""
    max_cycles: int = 3
    similarity_threshold: float = 0.90  # Stop if similarity >= this
    risk_threshold: float = 0.35  # Stop if risk > this
    initial_contradiction_budget: float = 1.0
    contradiction_decay_rate: float = 0.175  # How fast budget depletes
    quality_improvement_threshold: float = 0.05  # Minimum improvement to continue
    
    # Hyperparameters (from Reference Mechanism v1.4)
    alpha: float = 0.65  # Weight for aggregate risk in R calculation
    beta: float = 0.30  # Weight for wisdom risk in R calculation
    gamma: float = 0.75  # Weight for R in S calculation
    delta: float = 0.15  # Weight for escalation pressure in S calculation
    epsilon: float = 0.45  # Weight for wisdom stress in S calculation


class THEOSGovernor:
    """
    The THEOS Governor manages dual-engine reasoning cycles with contradiction budgets,
    stop conditions, and wisdom accumulation.
    
    This is a deterministic state machine—not a black box.
    """
    
    def __init__(self, config: GovernorConfig = None):
        self.config = config or GovernorConfig()
        self.wisdom_records: List[WisdomRecord] = []
        self.posture = Posture.NOM
        self.cycle_history: List[GovernorEvaluation] = []
        
    def compute_similarity(self, output_l: str, output_r: str) -> float:
        """
        Compute semantic similarity between two engine outputs.
        
        In production, this would use embeddings (e.g., sentence-transformers).
        For this reference implementation, we use a simple heuristic.
        """
        # Simplified similarity: ratio of shared words (case-insensitive)
        words_l = set(output_l.lower().split())
        words_r = set(output_r.lower().split())
        
        if not words_l or not words_r:
            return 0.0
        
        shared = words_l.intersection(words_r)
        total = words_l.union(words_r)
        
        return len(shared) / len(total) if total else 0.0
    
    def compute_risk(self, output_l: EngineOutput, output_r: EngineOutput, 
                     similarity: float) -> float:
        """
        Compute risk score based on engine outputs and similarity.
        
        Risk increases when:
        - Engines disagree (low similarity)
        - Either engine has low confidence
        - Critical engine (R) raises specific concerns
        """
        # Base risk from disagreement
        disagreement_risk = 1.0 - similarity
        
        # Confidence risk (low confidence = high risk)
        confidence_risk = 1.0 - min(output_l.confidence, output_r.confidence)
        
        # Weighted combination
        risk = 0.6 * disagreement_risk + 0.4 * confidence_risk
        
        return max(0.0, min(1.0, risk))  # Clamp to [0, 1]
    
    def compute_quality_metrics(self, output_l: EngineOutput, output_r: EngineOutput,
                                 similarity: float) -> Dict[str, float]:
        """
        Compute quality metrics for the current reasoning state.
        
        In production, these would use specialized models/heuristics.
        For reference, we use simplified estimates.
        """
        # Coherence: how well the outputs are structured
        coherence = (output_l.confidence + output_r.confidence) / 2.0
        
        # Calibration: how well-calibrated the confidence is (proxy: similarity)
        calibration = similarity
        
        # Evidence quality: proxy based on output length and confidence
        evidence_quality = min(1.0, (len(output_l.output) + len(output_r.output)) / 1000.0)
        evidence_quality = (evidence_quality + output_l.confidence + output_r.confidence) / 3.0
        
        # Actionability: how actionable the outputs are (proxy: confidence and agreement)
        actionability = (similarity + output_l.confidence + output_r.confidence) / 3.0
        
        return {
            "coherence": coherence,
            "calibration": calibration,
            "evidence_quality": evidence_quality,
            "actionability": actionability
        }
    
    def compute_contradiction_spent(self, contradiction_level: float) -> float:
        """
        Compute how much contradiction budget is consumed this cycle.
        
        Formula: spent = contradiction_level * decay_rate
        """
        return contradiction_level * self.config.contradiction_decay_rate
    
    def evaluate_cycle(self, output_l: EngineOutput, output_r: EngineOutput,
                       current_budget: float, cycle_number: int) -> GovernorEvaluation:
        """
        Evaluate a single reasoning cycle and decide whether to continue or stop.
        
        This is the core Governor logic.
        """
        # Compute similarity and contradiction
        similarity = self.compute_similarity(output_l.output, output_r.output)
        contradiction = 1.0 - similarity
        
        # Compute risk
        risk = self.compute_risk(output_l, output_r, similarity)
        
        # Compute quality metrics
        quality_metrics = self.compute_quality_metrics(output_l, output_r, similarity)
        composite_quality = sum(quality_metrics.values()) / len(quality_metrics)
        
        # Compute contradiction spent
        contradiction_spent = self.compute_contradiction_spent(contradiction)
        remaining_budget = current_budget - contradiction_spent
        
        # Decision logic (stop conditions)
        decision = "CONTINUE"
        stop_reason = None
        internal_monologue = ""
        
        # Stop Condition 1: Convergence achieved
        if similarity >= self.config.similarity_threshold:
            decision = "STOP"
            stop_reason = StopReason.CONVERGENCE_ACHIEVED
            internal_monologue = f"[Governor] Excellent convergence (similarity {similarity:.2f}). Stopping with high confidence."
        
        # Stop Condition 2: Risk threshold exceeded
        elif risk > self.config.risk_threshold:
            decision = "STOP"
            stop_reason = StopReason.RISK_THRESHOLD_EXCEEDED
            internal_monologue = f"[Governor] Risk threshold exceeded ({risk:.2f} > {self.config.risk_threshold}). Stopping for safety."
        
        # Stop Condition 3: Contradiction budget exhausted
        elif remaining_budget <= 0:
            decision = "STOP"
            stop_reason = StopReason.CONTRADICTION_EXHAUSTED
            internal_monologue = f"[Governor] Contradiction budget exhausted. Stopping to prevent runaway conflict."
        
        # Stop Condition 4: Plateau detected (no improvement)
        elif cycle_number > 1 and len(self.cycle_history) > 0:
            prev_quality = self.cycle_history[-1].composite_quality
            quality_improvement = composite_quality - prev_quality
            
            if quality_improvement < self.config.quality_improvement_threshold:
                decision = "STOP"
                stop_reason = StopReason.PLATEAU_DETECTED
                internal_monologue = f"[Governor] Quality plateau detected (improvement {quality_improvement:.3f} < threshold). Stopping."
        
        # Stop Condition 5: Max cycles reached
        elif cycle_number >= self.config.max_cycles:
            decision = "STOP"
            stop_reason = StopReason.MAX_CYCLES_REACHED
            internal_monologue = f"[Governor] Maximum cycles ({self.config.max_cycles}) reached. Stopping."
        
        # Continue decision
        else:
            internal_monologue = f"[Governor] Cycle {cycle_number}: similarity {similarity:.2f}, risk {risk:.2f}, quality {composite_quality:.2f}. Continuing."
        
        evaluation = GovernorEvaluation(
            similarity_score=similarity,
            contradiction_level=contradiction,
            risk_score=risk,
            quality_metrics=quality_metrics,
            composite_quality=composite_quality,
            contradiction_spent=contradiction_spent,
            remaining_budget=remaining_budget,
            decision=decision,
            stop_reason=stop_reason,
            internal_monologue=internal_monologue
        )
        
        self.cycle_history.append(evaluation)
        return evaluation
    
    def add_wisdom(self, record: WisdomRecord):
        """Add a wisdom record from a decision consequence."""
        self.wisdom_records.append(record)
    
    def get_audit_trail(self) -> Dict:
        """
        Generate a complete audit trail of all reasoning cycles.
        
        This is what makes THEOS interpretable—every decision is traceable.
        """
        return {
            "total_cycles": len(self.cycle_history),
            "final_similarity": self.cycle_history[-1].similarity_score if self.cycle_history else 0.0,
            "final_risk": self.cycle_history[-1].risk_score if self.cycle_history else 0.0,
            "final_quality": self.cycle_history[-1].composite_quality if self.cycle_history else 0.0,
            "stop_reason": self.cycle_history[-1].stop_reason.value if self.cycle_history and self.cycle_history[-1].stop_reason else None,
            "contradiction_budget_used": self.config.initial_contradiction_budget - (self.cycle_history[-1].remaining_budget if self.cycle_history else self.config.initial_contradiction_budget),
            "quality_trajectory": [eval.composite_quality for eval in self.cycle_history],
            "risk_trajectory": [eval.risk_score for eval in self.cycle_history],
            "similarity_trajectory": [eval.similarity_score for eval in self.cycle_history],
            "wisdom_records_count": len(self.wisdom_records)
        }


# Example usage
if __name__ == "__main__":
    # Initialize Governor
    governor = THEOSGovernor()
    
    # Simulate a reasoning cycle
    output_l = EngineOutput(
        reasoning_mode="Constructive",
        output="AI should provide information with ethical caveats.",
        confidence=0.72,
        internal_monologue="[Engine L] Focusing on user autonomy."
    )
    
    output_r = EngineOutput(
        reasoning_mode="Critical",
        output="AI should refuse ethically ambiguous requests to avoid complicity.",
        confidence=0.81,
        internal_monologue="[Engine R] Prioritizing harm prevention over autonomy."
    )
    
    # Evaluate cycle
    evaluation = governor.evaluate_cycle(output_l, output_r, 
                                         current_budget=1.0, 
                                         cycle_number=1)
    
    print("=== THEOS Governor Evaluation ===")
    print(f"Similarity: {evaluation.similarity_score:.2f}")
    print(f"Contradiction: {evaluation.contradiction_level:.2f}")
    print(f"Risk: {evaluation.risk_score:.2f}")
    print(f"Quality: {evaluation.composite_quality:.2f}")
    print(f"Decision: {evaluation.decision}")
    print(f"Internal Monologue: {evaluation.internal_monologue}")
    
    # Get audit trail
    audit_trail = governor.get_audit_trail()
    print("\n=== Audit Trail ===")
    print(f"Total Cycles: {audit_trail['total_cycles']}")
    print(f"Final Quality: {audit_trail['final_quality']:.2f}")
    print(f"Contradiction Budget Used: {audit_trail['contradiction_budget_used']:.2f}")
