#!/usr/bin/env python3
"""
THEOS Unified System
====================

Integrates TheosCore reasoning engine with governor control and memory persistence.

This module provides:
- TheosSystem: Unified interface combining reasoning, governance, and memory
- Integration with existing governor and memory engine
- Production-ready reasoning pipeline

Author: Frederick Davis Stalnecker
Patent: USPTO #63/831,738
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable
import json
from datetime import datetime

from theos_core import (
    TheosCore,
    TheosConfig,
    TheosOutput,
    HaltReason,
    CycleTrace,
)


@dataclass
class SystemMetrics:
    """Metrics about THEOS system performance."""
    total_queries: int = 0
    total_cycles: int = 0
    avg_cycles_per_query: float = 0.0
    convergence_rate: float = 0.0  # % of queries that converge
    wisdom_entries: int = 0
    avg_confidence: float = 0.0


class TheosSystem:
    """
    Unified THEOS system combining reasoning, governance, and memory.
    
    This system integrates:
    - TheosCore: I→A→D→I reasoning cycles
    - Governor: Halting and output selection
    - Memory: Wisdom accumulation and retrieval
    - Metrics: Performance tracking
    """
    
    def __init__(
        self,
        config: TheosConfig,
        encode_observation: Callable,
        induce_patterns: Callable,
        abduce_left: Callable,
        abduce_right: Callable,
        deduce: Callable,
        measure_contradiction: Callable,
        retrieve_wisdom: Callable,
        update_wisdom: Callable,
        estimate_entropy: Callable,
        estimate_info_gain: Callable,
        persistence_file: Optional[str] = None,
    ):
        """Initialize THEOS system."""
        self.config = config
        self.persistence_file = persistence_file
        
        # Initialize core reasoning engine
        self.core = TheosCore(
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
        
        # Metrics
        self.metrics = SystemMetrics()
        self.query_history: List[Dict[str, Any]] = []
        
        # Load persisted wisdom if available
        if persistence_file:
            self._load_wisdom()
    
    def reason(
        self,
        query: str,
        context: Optional[Any] = None,
        track_metrics: bool = True,
    ) -> TheosOutput:
        """
        Run THEOS reasoning for a query.
        
        Args:
            query: The query to reason about
            context: Optional context information
            track_metrics: Whether to update system metrics
            
        Returns:
            TheosOutput with reasoning result
        """
        # Run reasoning
        result = self.core.run_query(query, context)
        
        # Track metrics
        if track_metrics:
            self._update_metrics(result)
            self._record_query(query, context, result)
        
        # Persist wisdom
        if self.persistence_file:
            self._save_wisdom()
        
        return result
    
    def _update_metrics(self, result: TheosOutput):
        """Update system metrics based on query result."""
        self.metrics.total_queries += 1
        self.metrics.total_cycles += result.cycles_used
        self.metrics.avg_cycles_per_query = (
            self.metrics.total_cycles / self.metrics.total_queries
        )
        
        # Count convergence
        if result.halt_reason == HaltReason.CONVERGENCE:
            convergence_count = int(
                self.metrics.convergence_rate * (self.metrics.total_queries - 1)
            )
            convergence_count += 1
            self.metrics.convergence_rate = (
                convergence_count / self.metrics.total_queries
            )
        
        # Update wisdom count
        self.metrics.wisdom_entries = len(self.core.wisdom)
        
        # Update average confidence
        if self.metrics.total_queries == 1:
            self.metrics.avg_confidence = result.confidence
        else:
            self.metrics.avg_confidence = (
                (self.metrics.avg_confidence * (self.metrics.total_queries - 1) +
                 result.confidence) / self.metrics.total_queries
            )
    
    def _record_query(
        self,
        query: str,
        context: Optional[Any],
        result: TheosOutput,
    ):
        """Record query in history."""
        record = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "context": str(context) if context else None,
            "output": str(result.output),
            "output_type": result.output_type,
            "confidence": result.confidence,
            "contradiction": result.contradiction,
            "cycles_used": result.cycles_used,
            "halt_reason": result.halt_reason.value,
        }
        self.query_history.append(record)
    
    def get_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        return self.metrics
    
    def get_query_history(self) -> List[Dict[str, Any]]:
        """Get query history."""
        return self.query_history
    
    def get_wisdom(self) -> Dict[str, Any]:
        """Get accumulated wisdom."""
        return self.core.get_wisdom_summary()
    
    def clear_wisdom(self):
        """Clear all wisdom."""
        self.core.clear_wisdom()
        if self.persistence_file:
            self._save_wisdom()
    
    def export_metrics(self) -> str:
        """Export metrics as JSON."""
        metrics = self.metrics
        return json.dumps({
            "total_queries": metrics.total_queries,
            "total_cycles": metrics.total_cycles,
            "avg_cycles_per_query": metrics.avg_cycles_per_query,
            "convergence_rate": metrics.convergence_rate,
            "wisdom_entries": metrics.wisdom_entries,
            "avg_confidence": metrics.avg_confidence,
        }, indent=2)
    
    def export_history(self) -> str:
        """Export query history as JSON."""
        return json.dumps(self.query_history, indent=2)
    
    def _save_wisdom(self):
        """Save wisdom to persistent storage."""
        if not self.persistence_file:
            return
        
        wisdom_data = {
            "timestamp": datetime.now().isoformat(),
            "entries": self.core.wisdom,
        }
        
        try:
            with open(self.persistence_file, 'w') as f:
                json.dump(wisdom_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save wisdom: {e}")
    
    def _load_wisdom(self):
        """Load wisdom from persistent storage."""
        if not self.persistence_file:
            return
        
        try:
            with open(self.persistence_file, 'r') as f:
                wisdom_data = json.load(f)
                self.core.wisdom = wisdom_data.get("entries", [])
        except FileNotFoundError:
            pass  # No existing wisdom file
        except Exception as e:
            print(f"Warning: Could not load wisdom: {e}")
    
    def print_metrics(self):
        """Print metrics to console."""
        m = self.metrics
        print("\n" + "=" * 60)
        print("THEOS System Metrics")
        print("=" * 60)
        print(f"Total Queries:        {m.total_queries}")
        print(f"Total Cycles:         {m.total_cycles}")
        print(f"Avg Cycles/Query:     {m.avg_cycles_per_query:.2f}")
        print(f"Convergence Rate:     {m.convergence_rate:.1%}")
        print(f"Wisdom Entries:       {m.wisdom_entries}")
        print(f"Avg Confidence:       {m.avg_confidence:.3f}")
        print("=" * 60 + "\n")


# ============================================================================
# Example: Numeric THEOS System
# ============================================================================

def create_numeric_system(
    config: Optional[TheosConfig] = None,
    persistence_file: Optional[str] = None,
) -> TheosSystem:
    """Create a simple numeric THEOS system for testing."""
    if config is None:
        config = TheosConfig(verbose=False)
    
    def encode_observation(query: str, context: Any) -> float:
        return float(len(query) % 10) / 10.0
    
    def induce_patterns(obs: float, prev_phi: float) -> float:
        return obs - 0.1 * prev_phi
    
    def abduce_left(pattern_I: float, wisdom_slice: List) -> float:
        base = pattern_I
        if wisdom_slice:
            avg_past = sum(e.get("output_value", 0) for e in wisdom_slice) / len(wisdom_slice)
            return 0.5 * base + 0.5 * avg_past
        return base + 0.2 * (1.0 - base)
    
    def abduce_right(pattern_I: float, wisdom_slice: List) -> float:
        base = pattern_I
        if wisdom_slice:
            avg_past = sum(e.get("output_value", 0) for e in wisdom_slice) / len(wisdom_slice)
            return base - 0.2 * (avg_past - base)
        return base + 0.2 * (-1.0 - base)
    
    def deduce(hypothesis: float) -> float:
        return hypothesis
    
    def measure_contradiction(D_L: float, D_R: float) -> float:
        return abs(D_L - D_R)
    
    def retrieve_wisdom(query: str, W: List, threshold: float) -> List:
        return [e for e in W if e.get("query") == query]
    
    def update_wisdom(W: List, query: str, output: Any, confidence: float) -> List:
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
    
    def estimate_entropy(hypothesis_pair):
        import math
        A_L, A_R = hypothesis_pair
        delta = abs(A_L - A_R)
        return 1.0 - math.exp(-delta)
    
    def estimate_info_gain(phi_new: float, phi_prev: float) -> float:
        if phi_prev == 0:
            return 1.0
        ratio = abs(phi_prev - phi_new) / max(phi_prev, 1e-6)
        return min(2.0, ratio)
    
    return TheosSystem(
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
        persistence_file=persistence_file,
    )


if __name__ == "__main__":
    # Create system
    system = create_numeric_system()
    
    # Run multiple queries
    queries = [
        "What is the right move?",
        "What is the right move?",  # Repeat to show wisdom reuse
        "Completely different question",
    ]
    
    for q in queries:
        result = system.reason(q)
        print(f"\nQuery: {q}")
        print(f"Output: {result.output}")
        print(f"Confidence: {result.confidence:.3f}")
        print(f"Cycles: {result.cycles_used}")
        print(f"Halt: {result.halt_reason.value}")
    
    # Print metrics
    system.print_metrics()
