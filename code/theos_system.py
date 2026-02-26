#!/usr/bin/env python3
"""
THEOS Unified System
====================

Wraps TheosCore with metrics tracking, query history, and wisdom persistence.
This is the primary entry point for using THEOS in applications.

For the full architecture description, see theos_core.py.

Author: Frederick Davis Stalnecker
Patent: USPTO #63/831,738
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable
import json
import math
from datetime import datetime

from theos_core import (
    TheosCore,
    TheosConfig,
    TheosOutput,
    HaltReason,
    WringerPassTrace,
    AbductionEngines,
    DeductionEngine,
)

# Backward-compatibility alias
CycleTrace = WringerPassTrace


# ============================================================================
# System Metrics
# ============================================================================

@dataclass
class SystemMetrics:
    """Performance metrics across all queries."""
    total_queries: int = 0
    total_wringer_passes: int = 0   # total outer cycles across all queries
    avg_passes_per_query: float = 0.0
    convergence_rate: float = 0.0   # fraction of queries that converged
    wisdom_entries: int = 0
    avg_confidence: float = 0.0

    @property
    def total_cycles(self) -> int:
        """Backward-compatible alias for total_wringer_passes."""
        return self.total_wringer_passes

    @property
    def avg_cycles_per_query(self) -> float:
        """Backward-compatible alias for avg_passes_per_query."""
        return self.avg_passes_per_query


# ============================================================================
# TheosSystem
# ============================================================================

class TheosSystem:
    """
    Unified THEOS system: reasoning + metrics + wisdom persistence.

    Wraps TheosCore and adds:
    - SystemMetrics (convergence rate, avg passes, confidence)
    - Query history (full audit log)
    - Wisdom persistence (JSON file, optional)

    Usage:
        system = create_numeric_system()
        result = system.reason("My question")
        print(result.output, result.confidence)
        system.print_metrics()
    """

    def __init__(
        self,
        config: TheosConfig,
        encode_observation: Callable,
        induce_patterns: Callable,
        measure_contradiction: Callable,
        retrieve_wisdom: Callable,
        update_wisdom: Callable,
        estimate_entropy: Callable,
        estimate_info_gain: Callable,
        abduction_engines: Optional[AbductionEngines] = None,
        deduction_engine: Optional[DeductionEngine] = None,
        abduce_left: Optional[Callable] = None,
        abduce_right: Optional[Callable] = None,
        deduce: Optional[Callable] = None,
        persistence_file: Optional[str] = None,
    ):
        self.config = config
        self.persistence_file = persistence_file

        self.core = TheosCore(
            config=config,
            encode_observation=encode_observation,
            induce_patterns=induce_patterns,
            measure_contradiction=measure_contradiction,
            retrieve_wisdom=retrieve_wisdom,
            update_wisdom=update_wisdom,
            estimate_entropy=estimate_entropy,
            estimate_info_gain=estimate_info_gain,
            abduction_engines=abduction_engines,
            deduction_engine=deduction_engine,
            abduce_left=abduce_left,
            abduce_right=abduce_right,
            deduce=deduce,
        )

        self.metrics = SystemMetrics()
        self.query_history: List[Dict[str, Any]] = []

        if persistence_file:
            self._load_wisdom()

    def reason(
        self,
        query: str,
        context: Optional[Any] = None,
        track_metrics: bool = True,
    ) -> TheosOutput:
        """
        Run THEOS dual-engine wringer reasoning for a query.

        Returns TheosOutput with:
        - output: the answer (convergence / blend / disagreement)
        - confidence: [0, 1]
        - contradiction: Φ at halt
        - wringer_passes_used: how many outer cycles ran
        - halt_reason: why the governor stopped
        - trace: full inner + outer pass trace
        """
        result = self.core.run_query(query, context)

        if track_metrics:
            self._update_metrics(result)
            self._record_query(query, context, result)

        if self.persistence_file:
            self._save_wisdom()

        return result

    def _update_metrics(self, result: TheosOutput):
        self.metrics.total_queries += 1
        self.metrics.total_wringer_passes += result.wringer_passes_used
        self.metrics.avg_passes_per_query = (
            self.metrics.total_wringer_passes / self.metrics.total_queries
        )

        if result.halt_reason == HaltReason.CONVERGENCE:
            convergence_count = int(
                self.metrics.convergence_rate * (self.metrics.total_queries - 1)
            )
            convergence_count += 1
            self.metrics.convergence_rate = convergence_count / self.metrics.total_queries

        self.metrics.wisdom_entries = len(self.core.wisdom)

        n = self.metrics.total_queries
        self.metrics.avg_confidence = (
            (self.metrics.avg_confidence * (n - 1) + result.confidence) / n
        )

    def _record_query(self, query: str, context: Optional[Any], result: TheosOutput):
        self.query_history.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "context": str(context) if context else None,
            "output": str(result.output),
            "output_type": result.output_type,
            "confidence": result.confidence,
            "contradiction": result.contradiction,
            "wringer_passes_used": result.wringer_passes_used,
            "cycles_used": result.wringer_passes_used,  # backward compat
            "halt_reason": result.halt_reason.value,
        })

    def get_metrics(self) -> SystemMetrics:
        return self.metrics

    def get_query_history(self) -> List[Dict[str, Any]]:
        return self.query_history

    def get_wisdom(self) -> Dict[str, Any]:
        return self.core.get_wisdom_summary()

    def clear_wisdom(self):
        self.core.clear_wisdom()
        if self.persistence_file:
            self._save_wisdom()

    def export_metrics(self) -> str:
        m = self.metrics
        return json.dumps({
            "total_queries": m.total_queries,
            "total_wringer_passes": m.total_wringer_passes,
            "total_cycles": m.total_wringer_passes,
            "avg_passes_per_query": m.avg_passes_per_query,
            "avg_cycles_per_query": m.avg_passes_per_query,
            "convergence_rate": m.convergence_rate,
            "wisdom_entries": m.wisdom_entries,
            "avg_confidence": m.avg_confidence,
        }, indent=2)

    def export_history(self) -> str:
        return json.dumps(self.query_history, indent=2)

    def print_metrics(self):
        m = self.metrics
        print("\n" + "=" * 60)
        print("THEOS System Metrics")
        print("=" * 60)
        print(f"Total Queries:          {m.total_queries}")
        print(f"Total Wringer Passes:   {m.total_wringer_passes}")
        print(f"Avg Passes / Query:     {m.avg_passes_per_query:.2f}")
        print(f"Convergence Rate:       {m.convergence_rate:.1%}")
        print(f"Wisdom Entries:         {m.wisdom_entries}")
        print(f"Avg Confidence:         {m.avg_confidence:.3f}")
        print("=" * 60 + "\n")

    def _save_wisdom(self):
        if not self.persistence_file:
            return
        try:
            with open(self.persistence_file, "w") as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "entries": self.core.wisdom,
                }, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save wisdom: {e}")

    def _load_wisdom(self):
        if not self.persistence_file:
            return
        try:
            with open(self.persistence_file, "r") as f:
                data = json.load(f)
                self.core.wisdom = data.get("entries", [])
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Warning: Could not load wisdom: {e}")


# ============================================================================
# Numeric reference system
# ============================================================================

def create_numeric_system(
    config: Optional[TheosConfig] = None,
    persistence_file: Optional[str] = None,
) -> TheosSystem:
    """
    Create a minimal numeric THEOS system for testing and demonstration.

    All values are floats. This system illustrates the full architecture
    without domain-specific knowledge.

    Left engine (clockwise):    pulls toward +1.0
    Right engine (counterclockwise): pulls toward -1.0
    Contradiction: absolute distance between the two self-reflected outputs.

    Per-engine self-reflection:
        induce_patterns(obs, prev_phi, prev_own_deduction) is implemented
        with the self-reflection argument. On the second inner pass, each
        engine's inductive pattern is nudged toward its own prior deduction,
        making the engine reason about its own first-pass conclusion.
    """
    if config is None:
        config = TheosConfig(verbose=False)

    def encode_observation(query: str, context: Any) -> float:
        """Map query to a numeric signal in [0.0, 0.9]."""
        return float(len(query) % 10) / 10.0

    def induce_patterns(obs: float, prev_phi: float, prev_own_deduction: Optional[float] = None) -> float:
        """
        Induction with per-engine self-reflection.

        On the first inner pass (prev_own_deduction is None):
            pattern = obs - 0.1 * prev_phi
            The engine starts from the observation, tempered by wringer contradiction.

        On the second inner pass (prev_own_deduction is the engine's own D from pass 1):
            pattern = 0.7 * (obs - 0.1 * prev_phi) + 0.3 * prev_own_deduction
            The engine is now reasoning about what it just concluded — its momentary past.
            The 0.3 weight toward prev_own_deduction is the self-reflection coefficient.
        """
        base = obs - 0.1 * prev_phi
        if prev_own_deduction is not None:
            # Self-reflection: engine pulls its pattern toward its own prior conclusion
            return 0.7 * base + 0.3 * prev_own_deduction
        return base

    def abduce_left(pattern_I: float, wisdom_slice: List) -> float:
        """
        Constructive (clockwise) abduction: pull toward +1.0.
        If wisdom is available, bias toward what worked before.
        """
        base = pattern_I
        if wisdom_slice:
            avg_past = sum(e.get("output_value", 0) for e in wisdom_slice) / len(wisdom_slice)
            return 0.5 * base + 0.5 * avg_past
        return base + 0.2 * (1.0 - base)

    def abduce_right(pattern_I: float, wisdom_slice: List) -> float:
        """
        Adversarial (counterclockwise) abduction: pull toward -1.0.
        Opposes the left engine's constructive direction.
        """
        base = pattern_I
        if wisdom_slice:
            avg_past = sum(e.get("output_value", 0) for e in wisdom_slice) / len(wisdom_slice)
            return base - 0.2 * (avg_past - base)
        return base + 0.2 * (-1.0 - base)

    def deduce(hypothesis: float) -> float:
        """Deduction: the numeric system uses the hypothesis directly as the conclusion."""
        return hypothesis

    def measure_contradiction(D_L: float, D_R: float) -> float:
        """
        Wringer measurement: absolute distance between the two self-reflected conclusions.
        Φ = |D_L* - D_R*|
        """
        return abs(D_L - D_R)

    def retrieve_wisdom(query: str, W: List, threshold: float) -> List:
        """Return wisdom entries from the same query (exact match for the numeric toy)."""
        return [e for e in W if e.get("query") == query]

    def update_wisdom(W: List, query: str, output: Any, confidence: float) -> List:
        """
        Deposit this query's lesson into the wisdom register (the meta-past).
        Extracts a scalar output_value for numeric comparison.
        """
        if isinstance(output, (int, float)):
            out_val = float(output)
        elif isinstance(output, dict) and output.get("type") == "blend":
            wL = output["weights"]["left"]
            wR = output["weights"]["right"]
            out_val = wL * float(output["left"]) + wR * float(output["right"])
        elif isinstance(output, dict) and output.get("type") == "disagreement":
            out_val = 0.5 * (float(output["left"]) + float(output["right"]))
        else:
            out_val = 0.0

        return W + [{"query": query, "output_value": out_val, "confidence": confidence}]

    def estimate_entropy(hypothesis_pair: tuple) -> float:
        """
        Entropy proxy: larger hypothesis divergence → higher entropy.
        Maps |A_L - A_R| through 1 - exp(-δ) into (0, 1).
        """
        A_L, A_R = hypothesis_pair
        delta = abs(A_L - A_R)
        return 1.0 - math.exp(-delta)

    def estimate_info_gain(phi_new: float, phi_prev: float) -> float:
        """
        Information gain ratio: how much did contradiction change relative to last pass?
        Used by the governor's diminishing returns criterion.
        """
        if phi_prev == 0:
            return 1.0
        return min(2.0, abs(phi_prev - phi_new) / max(phi_prev, 1e-6))

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


# ============================================================================
# Demo
# ============================================================================

if __name__ == "__main__":
    system = create_numeric_system(TheosConfig(verbose=True))

    queries = [
        "What is the right move?",
        "What is the right move?",   # repeat — wisdom feeds back in
        "Completely different question",
    ]

    for q in queries:
        print("\n" + "=" * 70)
        print(f"QUERY: {q}")
        result = system.reason(q)
        print(f"Output:         {result.output}")
        print(f"Confidence:     {result.confidence:.3f}")
        print(f"Contradiction:  {result.contradiction:.3f}")
        print(f"Wringer passes: {result.wringer_passes_used}")
        print(f"Halt reason:    {result.halt_reason.value}")

        # Show inner pass detail for first wringer pass
        if result.trace:
            wp = result.trace[0]
            print(f"\n  Wringer pass 0 inner traces:")
            for ip in wp.left_inner_passes:
                print(f"    LEFT  pass {ip.pass_num}: I={ip.pattern_I:.3f} "
                      f"A={ip.hypothesis:.3f} D={ip.deduction:.3f} "
                      f"self_reflected={ip.used_own_prior}")
            for ip in wp.right_inner_passes:
                print(f"    RIGHT pass {ip.pass_num}: I={ip.pattern_I:.3f} "
                      f"A={ip.hypothesis:.3f} D={ip.deduction:.3f} "
                      f"self_reflected={ip.used_own_prior}")

    system.print_metrics()
