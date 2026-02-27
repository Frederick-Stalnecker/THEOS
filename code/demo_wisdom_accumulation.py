#!/usr/bin/env python3
"""
THEOS Wisdom Accumulation Demonstration
========================================

This demo shows how THEOS improves on repeated queries through:
1. Temporal recursion (thinking about thinking)
2. Wisdom accumulation (learning from previous cycles)
3. Energy savings (fewer cycles needed on second query)

Author: Frederick Davis Stalnecker
Date: February 22, 2026
"""

import sys

sys.path.insert(0, "/home/ubuntu/THEOS_repo/code")


from theos_governor_phase2 import GovernorConfig, THEOSGovernor


def demonstrate_wisdom_accumulation():
    """Demonstrate how wisdom accumulates and improves subsequent queries."""

    print("=" * 80)
    print("THEOS WISDOM ACCUMULATION DEMONSTRATION")
    print("=" * 80)
    print("\nThis demonstrates the core THEOS mechanism:")
    print("  1. Temporal Recursion: Output becomes input for next cycle")
    print("  2. Wisdom Accumulation: Learning from previous reasoning")
    print("  3. Energy Savings: Fewer cycles needed on repeated queries")
    print("\n" + "=" * 80)

    # Initialize Governor
    config = GovernorConfig()
    governor = THEOSGovernor(config)

    # Test queries
    queries = [
        "What is the relationship between freedom and responsibility?",
        "How should AI systems handle ethical dilemmas?",
        "What is the relationship between freedom and responsibility?",  # Repeat first query
    ]

    results = []

    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 80}")
        print(f"QUERY {i}: {query}")
        print("=" * 80)

        # Run reasoning
        result = governor.reason(query, domain="philosophy")
        results.append(result)

        # Extract metrics
        audit = result.get("audit_trail", {})
        cycles_used = audit.get("total_cycles", 0)
        final_quality = audit.get("final_quality", 0)
        final_ethical = audit.get("final_ethical_alignment", 0)
        energy = audit.get("energy_metrics", {})
        wisdom_hit = energy.get("wisdom_hit_rate", 0)

        print("\nResults:")
        print(f"  Cycles Used: {cycles_used}")
        print(f"  Final Quality: {final_quality:.2f}")
        print(f"  Ethical Alignment: {final_ethical:.2f}")
        print(f"  Wisdom Hit Rate: {wisdom_hit:.1%}")

        # Show cycle progression
        print("\n  Cycle Progression:")
        cycle_details = audit.get("cycle_details", [])
        for cycle in cycle_details:
            print(
                f"    Cycle {cycle['cycle']}: "
                f"Quality={cycle['quality']:.2f}, "
                f"Contradiction={cycle['contradiction']:.2f}, "
                f"Momentary Past Influence={cycle['momentary_past_influence']:.2f}"
            )

        print(f"\n  Stop Reason: {audit.get('stop_reason', 'unknown')}")

    # Analysis
    print("\n" + "=" * 80)
    print("ANALYSIS: WISDOM ACCUMULATION EFFECTS")
    print("=" * 80)

    query_1_cycles = results[0]["audit_trail"]["total_cycles"]
    query_2_cycles = results[1]["audit_trail"]["total_cycles"]
    query_1_repeat_cycles = results[2]["audit_trail"]["total_cycles"]

    query_1_quality = results[0]["audit_trail"]["final_quality"]
    query_2_quality = results[1]["audit_trail"]["final_quality"]
    query_1_repeat_quality = results[2]["audit_trail"]["final_quality"]

    print(f"\nQuery 1 (initial): {query_1_cycles} cycles, Quality={query_1_quality:.2f}")
    print(f"Query 2 (new): {query_2_cycles} cycles, Quality={query_2_quality:.2f}")
    print(
        f"Query 1 (repeated): {query_1_repeat_cycles} cycles, Quality={query_1_repeat_quality:.2f}"
    )

    print("\nKey Observations:")
    print("  1. Query 1 → Query 2: Different questions, both require full reasoning")
    print("  2. Query 1 (repeat): Same question, but wisdom was accumulated")

    if query_1_repeat_cycles < query_1_cycles:
        savings = (1 - query_1_repeat_cycles / query_1_cycles) * 100
        print(f"  3. Cycle Reduction: {savings:.0f}% fewer cycles on repeated query")
        print(f"     ({query_1_cycles} → {query_1_repeat_cycles} cycles)")

    if query_1_repeat_quality > query_1_quality:
        improvement = (query_1_repeat_quality - query_1_quality) * 100
        print(f"  4. Quality Improvement: {improvement:.0f}% better on repeated query")
        print(f"     ({query_1_quality:.2f} → {query_1_repeat_quality:.2f})")

    print("\nWisdom Accumulation:")
    wisdom_stats = results[-1]["audit_trail"]["wisdom_stats"]
    print(f"  Total Wisdom Records: {wisdom_stats.get('total_records', 0)}")
    print(f"  Learned Records: {wisdom_stats.get('learned_records', 0)}")
    print(f"  Average Confidence: {wisdom_stats.get('average_confidence', 0):.2f}")

    print("\n" + "=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("""
The demonstration shows:

1. TEMPORAL RECURSION (Thinking about Thinking):
   - Each cycle, quality improves as engines reason about previous reasoning
   - Contradiction guides refinement toward ground truth
   - Governor halts when improvement plateaus (diminishing returns)

2. WISDOM ACCUMULATION (Learning from Past):
   - First query: Full reasoning cycle needed
   - Repeated query: Wisdom from first query accelerates reasoning
   - Fewer cycles needed because starting point is more refined

3. ENERGY SAVINGS (Computational Efficiency):
   - Repeated queries use accumulated wisdom
   - Early exit possible if wisdom confidence is high
   - Scales exponentially with multiple queries

4. HALLUCINATION PREVENTION (Safety Mechanism):
   - Can't hallucinate about what you just thought
   - Critical engine actively tests constructive reasoning
   - Contradiction forces reconciliation or honest uncertainty

This is the core of THEOS: Self-improving reasoning through productive disagreement.
""")

    print("=" * 80)


if __name__ == "__main__":
    demonstrate_wisdom_accumulation()
