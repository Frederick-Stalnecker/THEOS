#!/usr/bin/env python3
"""
THEOS Core Implementation
========================

Production-ready implementation of the THEOS (Triadic Hierarchical Emergent 
Optimization System) dual-engine reasoning framework with governor control.

This module provides:
- TheosCore: Main reasoning engine
- TheosConfig: Configuration management
- Cycle map T_q: I→A→D→I reasoning cycle
- Dual engines: Constructive (L) and critical (R) reasoning
- Governor: Halting and output selection logic
- Wisdom system: Accumulation and retrieval

Author: Frederick Davis Stalnecker
Patent: USPTO #63/831,738
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
import json
from datetime import datetime
import math


# ============================================================================
# Configuration and Data Types
# ============================================================================

class HaltReason(Enum):
    """Reasons for halting the reasoning cycle."""
    CONVERGENCE = "convergence"
    DIMINISHING_RETURNS = "diminishing_returns"
    BUDGET_EXHAUSTION = "budget_exhaustion"
    IRREDUCIBLE_UNCERTAINTY = "irreducible_uncertainty"
    MAX_CYCLES = "max_cycles"
    UNKNOWN = "unknown"


@dataclass
class TheosConfig:
    """Configuration for THEOS reasoning."""
    max_cycles: int = 7
    eps_converge: float = 0.05  # Convergence threshold for engines
    eps_partial: float = 0.5    # Partial convergence threshold
    rho_min: float = 0.4        # Minimum info gain ratio
    entropy_min: float = 0.15   # Minimum entropy threshold
    delta_min: float = 0.4      # Minimum contradiction threshold
    similarity_threshold: float = 0.7  # Wisdom retrieval threshold
    budget: Optional[float] = None  # Computational budget (None = unlimited)
    verbose: bool = False       # Verbose logging


@dataclass
class CycleTrace:
    """Record of a single reasoning cycle."""
    cycle: int
    pattern_I: Any
    hypothesis_L: Any
    hypothesis_R: Any
    deduction_L: Any
    deduction_R: Any
    contradiction: float
    entropy: float
    info_gain_ratio: float
    halt_reason: Optional[HaltReason] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TheosOutput:
    """Final output from THEOS reasoning."""
    output: Any
    output_type: str  # "convergence", "blend", "disagreement"
    confidence: float
    contradiction: float
    cycles_used: int
    halt_reason: HaltReason
    trace: List[CycleTrace]
    wisdom_updated: bool


# ============================================================================
# Type Aliases
# ============================================================================

PatternI = Any
HypothesisA = Any
DeductionD = Any
ContradictionF = float
WisdomEntry = Dict[str, Any]
WisdomStore = List[WisdomEntry]


# ============================================================================
# THEOS Core Implementation
# ============================================================================

class TheosCore:
    """
    Main THEOS reasoning engine implementing the I→A→D→I cycle with dual engines.
    
    The cycle operates as:
    1. Induction (I): Extract patterns from observations and previous contradictions
    2. Abduction (A): Generate dual hypotheses (constructive L and critical R)
    3. Deduction (D): Derive conclusions from each hypothesis
    4. Contradiction (Φ): Measure disagreement between engines
    5. Wisdom (W): Accumulate and retrieve learned patterns
    6. Governor: Decide when to halt and which output to return
    """
    
    def __init__(
        self,
        config: TheosConfig,
        encode_observation: Callable[[str, Any], Any],
        induce_patterns: Callable[[Any, float], PatternI],
        abduce_left: Callable[[PatternI, WisdomStore], HypothesisA],
        abduce_right: Callable[[PatternI, WisdomStore], HypothesisA],
        deduce: Callable[[HypothesisA], DeductionD],
        measure_contradiction: Callable[[DeductionD, DeductionD], float],
        retrieve_wisdom: Callable[[str, WisdomStore, float], WisdomStore],
        update_wisdom: Callable[[WisdomStore, str, Any, float], WisdomStore],
        estimate_entropy: Callable[[Tuple[HypothesisA, HypothesisA]], float],
        estimate_info_gain: Callable[[float, float], float],
    ):
        """
        Initialize THEOS core with configuration and reasoning functions.
        
        Args:
            config: TheosConfig instance
            encode_observation: Convert query+context to observation
            induce_patterns: Extract patterns from observations
            abduce_left: Generate constructive hypotheses
            abduce_right: Generate critical hypotheses
            deduce: Derive conclusions from hypotheses
            measure_contradiction: Measure engine disagreement
            retrieve_wisdom: Retrieve relevant past experiences
            update_wisdom: Store new experiences
            estimate_entropy: Estimate hypothesis space entropy
            estimate_info_gain: Estimate information gain ratio
        """
        self.config = config
        self.encode_observation = encode_observation
        self.induce_patterns = induce_patterns
        self.abduce_left = abduce_left
        self.abduce_right = abduce_right
        self.deduce = deduce
        self.measure_contradiction = measure_contradiction
        self.retrieve_wisdom = retrieve_wisdom
        self.update_wisdom = update_wisdom
        self.estimate_entropy = estimate_entropy
        self.estimate_info_gain = estimate_info_gain
        
        self.wisdom: WisdomStore = []
        self.cycle_count = 0
    
    def run_query(
        self,
        query: str,
        context: Optional[Any] = None,
    ) -> TheosOutput:
        """
        Run THEOS reasoning cycle for a query.
        
        Args:
            query: The query to reason about
            context: Optional context information
            
        Returns:
            TheosOutput with final answer, confidence, and trace
        """
        # Initialize state
        observation = self.encode_observation(query, context)
        trace: List[CycleTrace] = []
        prev_contradiction = 0.0
        prev_info_gain = 1.0
        
        # Main reasoning loop
        for cycle_num in range(self.config.max_cycles):
            # Step 1: Induction
            pattern_I = self.induce_patterns(observation, prev_contradiction)
            
            # Step 2: Abduction (dual engines)
            wisdom_slice = self.retrieve_wisdom(
                query,
                self.wisdom,
                self.config.similarity_threshold
            )
            hypothesis_L = self.abduce_left(pattern_I, wisdom_slice)
            hypothesis_R = self.abduce_right(pattern_I, wisdom_slice)
            
            # Step 3: Deduction (dual engines)
            deduction_L = self.deduce(hypothesis_L)
            deduction_R = self.deduce(hypothesis_R)
            
            # Step 4: Contradiction measurement
            contradiction = self.measure_contradiction(deduction_L, deduction_R)
            
            # Step 5: Entropy and info gain
            entropy = self.estimate_entropy((hypothesis_L, hypothesis_R))
            info_gain_ratio = self.estimate_info_gain(contradiction, prev_contradiction)
            
            # Record cycle
            cycle_record = CycleTrace(
                cycle=cycle_num,
                pattern_I=pattern_I,
                hypothesis_L=hypothesis_L,
                hypothesis_R=hypothesis_R,
                deduction_L=deduction_L,
                deduction_R=deduction_R,
                contradiction=contradiction,
                entropy=entropy,
                info_gain_ratio=info_gain_ratio,
            )
            trace.append(cycle_record)
            
            if self.config.verbose:
                print(f"Cycle {cycle_num}: Φ={contradiction:.4f}, "
                      f"H={entropy:.4f}, IG={info_gain_ratio:.4f}")
            
            # Step 6: Governor - Check halting criteria
            halt_reason = self._check_halt_criteria(
                cycle_num,
                contradiction,
                info_gain_ratio,
                entropy,
            )
            
            if halt_reason is not None:
                cycle_record.halt_reason = halt_reason
                
                # Generate output
                output, output_type, confidence = self._generate_output(
                    deduction_L,
                    deduction_R,
                    contradiction,
                    entropy,
                )
                
                # Update wisdom
                self.wisdom = self.update_wisdom(
                    self.wisdom,
                    query,
                    output,
                    confidence,
                )
                
                return TheosOutput(
                    output=output,
                    output_type=output_type,
                    confidence=confidence,
                    contradiction=contradiction,
                    cycles_used=cycle_num + 1,
                    halt_reason=halt_reason,
                    trace=trace,
                    wisdom_updated=True,
                )
            
            # Update for next cycle
            prev_contradiction = contradiction
            prev_info_gain = info_gain_ratio
        
        # Max cycles reached
        output, output_type, confidence = self._generate_output(
            deduction_L,
            deduction_R,
            contradiction,
            entropy,
        )
        
        self.wisdom = self.update_wisdom(
            self.wisdom,
            query,
            output,
            confidence,
        )
        
        return TheosOutput(
            output=output,
            output_type=output_type,
            confidence=confidence,
            contradiction=contradiction,
            cycles_used=self.config.max_cycles,
            halt_reason=HaltReason.MAX_CYCLES,
            trace=trace,
            wisdom_updated=True,
        )
    
    def _check_halt_criteria(
        self,
        cycle_num: int,
        contradiction: float,
        info_gain_ratio: float,
        entropy: float,
    ) -> Optional[HaltReason]:
        """
        Check if any halting criterion is met.
        
        Returns:
            HaltReason if halting, None otherwise
        """
        # Criterion 1: Convergence
        if contradiction < self.config.eps_converge:
            return HaltReason.CONVERGENCE
        
        # Criterion 2: Diminishing returns
        if cycle_num > 0 and info_gain_ratio < self.config.rho_min:
            return HaltReason.DIMINISHING_RETURNS
        
        # Criterion 3: Budget exhaustion
        if self.config.budget is not None and cycle_num >= self.config.budget:
            return HaltReason.BUDGET_EXHAUSTION
        
        # Criterion 4: Irreducible uncertainty
        if entropy < self.config.entropy_min and contradiction > self.config.delta_min:
            return HaltReason.IRREDUCIBLE_UNCERTAINTY
        
        return None
    
    def _generate_output(
        self,
        deduction_L: DeductionD,
        deduction_R: DeductionD,
        contradiction: float,
        entropy: float,
    ) -> Tuple[Any, str, float]:
        """
        Generate final output based on engine agreement and contradiction level.
        
        Returns:
            Tuple of (output, output_type, confidence)
        """
        # Case 1: Engines converge
        if contradiction < self.config.eps_converge:
            confidence = 1.0 - (contradiction / self.config.eps_converge)
            return deduction_L, "convergence", max(0.0, confidence)
        
        # Case 2: Partial convergence - blend outputs
        if contradiction < self.config.eps_partial:
            # Weight critical engine more as contradiction increases
            w_L = (1.0 - contradiction / self.config.eps_partial) / 2.0
            w_R = (1.0 + contradiction / self.config.eps_partial) / 2.0
            
            # Try to blend if both are numeric
            try:
                if isinstance(deduction_L, (int, float)) and isinstance(deduction_R, (int, float)):
                    blended = w_L * deduction_L + w_R * deduction_R
                    confidence = 1.0 - (contradiction / self.config.eps_partial) * 0.5
                    return blended, "blend", confidence
            except:
                pass
            
            # Return structured blend
            output = {
                "type": "blend",
                "left": deduction_L,
                "right": deduction_R,
                "weights": {"left": w_L, "right": w_R},
                "contradiction": contradiction,
            }
            confidence = 1.0 - (contradiction / self.config.eps_partial) * 0.5
            return output, "blend", confidence
        
        # Case 3: Engines disagree - expose both
        output = {
            "type": "disagreement",
            "left": deduction_L,
            "right": deduction_R,
            "contradiction": contradiction,
            "entropy": entropy,
        }
        confidence = 0.5  # Low confidence when engines disagree
        return output, "disagreement", confidence
    
    def get_wisdom_summary(self) -> Dict[str, Any]:
        """Get summary of accumulated wisdom."""
        return {
            "total_entries": len(self.wisdom),
            "entries": self.wisdom,
        }
    
    def clear_wisdom(self):
        """Clear all accumulated wisdom."""
        self.wisdom = []
    
    def export_trace(self, trace: List[CycleTrace]) -> str:
        """Export cycle trace as JSON."""
        trace_data = []
        for cycle in trace:
            trace_data.append({
                "cycle": cycle.cycle,
                "contradiction": cycle.contradiction,
                "entropy": cycle.entropy,
                "info_gain_ratio": cycle.info_gain_ratio,
                "halt_reason": cycle.halt_reason.value if cycle.halt_reason else None,
                "timestamp": cycle.timestamp,
            })
        return json.dumps(trace_data, indent=2)


# ============================================================================
# Helper Functions for Common Implementations
# ============================================================================

def create_numeric_theos(config: Optional[TheosConfig] = None) -> TheosCore:
    """
    Create a simple numeric THEOS instance for testing.
    
    This is a toy implementation where:
    - Patterns are floats
    - Hypotheses are floats
    - Deductions are floats
    - Contradiction is absolute difference
    """
    if config is None:
        config = TheosConfig()
    
    def encode_observation(query: str, context: Any) -> float:
        return float(len(query) % 10) / 10.0
    
    def induce_patterns(obs: float, prev_phi: float) -> float:
        return obs - 0.1 * prev_phi
    
    def abduce_left(pattern_I: float, wisdom_slice: WisdomStore) -> float:
        base = pattern_I
        if wisdom_slice:
            avg_past = sum(e.get("output_value", 0) for e in wisdom_slice) / len(wisdom_slice)
            return 0.5 * base + 0.5 * avg_past
        return base + 0.2 * (1.0 - base)
    
    def abduce_right(pattern_I: float, wisdom_slice: WisdomStore) -> float:
        base = pattern_I
        if wisdom_slice:
            avg_past = sum(e.get("output_value", 0) for e in wisdom_slice) / len(wisdom_slice)
            return base - 0.2 * (avg_past - base)
        return base + 0.2 * (-1.0 - base)
    
    def deduce(hypothesis: float) -> float:
        return hypothesis
    
    def measure_contradiction(D_L: float, D_R: float) -> float:
        return abs(D_L - D_R)
    
    def retrieve_wisdom(query: str, W: WisdomStore, threshold: float) -> WisdomStore:
        return [e for e in W if e.get("query") == query]
    
    def update_wisdom(W: WisdomStore, query: str, output: Any, confidence: float) -> WisdomStore:
        if isinstance(output, (int, float)):
            out_val = float(output)
        elif isinstance(output, dict) and output.get("type") == "blend":
            wL = output["weights"]["left"]
            wR = output["weights"]["right"]
            vL = float(output["left"])
            vR = float(output["right"])
            out_val = wL * vL + wR * vR
        elif isinstance(output, dict) and output.get("type") == "disagreement":
            vL = float(output["left"])
            vR = float(output["right"])
            out_val = 0.5 * (vL + vR)
        else:
            out_val = 0.0
        
        return W + [{
            "query": query,
            "output_value": out_val,
            "confidence": confidence,
        }]
    
    def estimate_entropy(hypothesis_pair: Tuple[float, float]) -> float:
        A_L, A_R = hypothesis_pair
        delta = abs(A_L - A_R)
        return 1.0 - math.exp(-delta)
    
    def estimate_info_gain(phi_new: float, phi_prev: float) -> float:
        if phi_prev == 0:
            return 1.0
        ratio = abs(phi_prev - phi_new) / max(phi_prev, 1e-6)
        return min(2.0, ratio)
    
    return TheosCore(
        config=config,
        encode_observation=encode_observation,
        induce_patterns=induce_patterns,
        abduce_left=abduce_left,
        abduce_right=abduce_right,
        deduce=deduce,
        measure_contradiction=measure_contradiction,
        retrieve_wisdom=retrieve_wisdom,
        update_wisdom=update_wisdom,
        estimate_entropy=estimate_entropy,
        estimate_info_gain=estimate_info_gain,
    )


if __name__ == "__main__":
    # Simple test
    theos = create_numeric_theos()
    result = theos.run_query("What is the right move?")
    print(f"Output: {result.output}")
    print(f"Confidence: {result.confidence:.3f}")
    print(f"Cycles: {result.cycles_used}")
    print(f"Halt reason: {result.halt_reason.value}")
