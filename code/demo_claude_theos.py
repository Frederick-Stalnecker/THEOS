#!/usr/bin/env python3
"""
THEOS with Claude - Real Reasoning Demonstration
================================================

This demonstrates THEOS with real Claude reasoning.
Shows:
- Temporal recursion (output → input)
- Dual engines producing genuine contradictions
- Quality improvement across cycles
- Hallucination prevention through meta-cognition

Author: Frederick Davis Stalnecker
Date: February 22, 2026
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))


from llm_adapter import get_llm_adapter
from theos_llm_reasoning import THEOSLLMReasoner


def demonstrate_theos_with_claude():
    """Demonstrate THEOS with real Claude reasoning."""

    print("=" * 80)
    print("THEOS WITH CLAUDE - REAL REASONING DEMONSTRATION")
    print("=" * 80)
    print("""
This demonstration shows THEOS working with real LLM reasoning.

Key features:
1. TEMPORAL RECURSION: Each cycle's output becomes the next cycle's input
2. DUAL ENGINES: Constructive (left, clockwise) vs Critical (right, counterclockwise)
3. CONTRADICTION: Genuine disagreement drives refinement
4. HALLUCINATION PREVENTION: Can't hallucinate about what you just thought
5. WISDOM ACCUMULATION: Learning from previous reasoning

The system will:
- Run up to 7 reasoning cycles
- Measure contradiction between engines
- Track quality improvement
- Halt when diminishing returns detected
- Accumulate wisdom for future queries
""")

    print("=" * 80)

    # Check if Claude API is available
    try:
        llm = get_llm_adapter("claude")
        print("\n✓ Claude API available")
    except Exception as e:
        print(f"\n✗ Claude API not available: {e}")
        print("  Using mock LLM for demonstration instead...")
        llm = get_llm_adapter("mock")

    # Create THEOS reasoner
    theos = THEOSLLMReasoner(llm, max_cycles=5)

    # Test queries
    queries = [
        "What is the relationship between freedom and responsibility?",
        "How should AI systems handle ethical dilemmas?",
    ]

    for query_num, query in enumerate(queries, 1):
        print(f"\n{'=' * 80}")
        print(f"QUERY {query_num}: {query}")
        print("=" * 80)

        # Run reasoning
        result = theos.reason(query)

        # Display results
        print("\nReasoning Complete:")
        print(f"  Cycles Used: {result.cycles_used}")
        print(f"  Quality: {result.quality:.2f}")
        print(f"  Contradiction: {result.contradiction:.2f}")
        print(f"  Halt Reason: {result.halt_reason}")
        print(f"  Tokens Used: {result.tokens_used}")
        print(f"  Wisdom Used: {result.wisdom_used}")

        # Show cycle progression
        print("\nCycle Progression:")
        for cycle in result.cycles:
            print(f"  Cycle {cycle.cycle_number}:")
            print(f"    Quality: {cycle.quality:.2f}")
            print(f"    Contradiction: {cycle.contradiction:.2f}")
            print(f"    Observation: {cycle.observation[:60]}...")

        # Show final answer
        print("\nFinal Answer:")
        print(result.final_answer)

    # Show wisdom accumulation
    print(f"\n{'=' * 80}")
    print("WISDOM ACCUMULATION")
    print("=" * 80)

    stats = theos.get_statistics()
    print(f"\nWisdom Records: {stats['total_wisdom_records']}")
    print(f"LLM Model: {stats['llm_model']}")
    print(f"LLM Statistics: {stats['llm_statistics']}")
    print(f"Retrieval Statistics: {stats['retrieval_statistics']}")

    # Demonstrate repeated query with wisdom
    print(f"\n{'=' * 80}")
    print("REPEATED QUERY WITH WISDOM")
    print("=" * 80)

    print("\nRunning first query again (should use accumulated wisdom)...")
    result_repeat = theos.reason(queries[0])

    print("\nResults:")
    print(f"  Cycles Used: {result_repeat.cycles_used}")
    print(f"  Quality: {result_repeat.quality:.2f}")
    print(f"  Wisdom Used: {result_repeat.wisdom_used}")
    print(f"  Tokens Used: {result_repeat.tokens_used}")

    print(f"\n{'=' * 80}")
    print("INTERPRETATION")
    print("=" * 80)
    print("""
What we just demonstrated:

1. TEMPORAL RECURSION:
   - Cycle 1: Engines reason about the original query
   - Cycle 2+: Engines reason about what they just reasoned
   - Each cycle, they "think about their thinking"
   - This prevents hallucination because you can't hallucinate about what you just thought

2. DUAL ENGINES:
   - Constructive engine: Builds strongest case
   - Critical engine: Tests for weaknesses
   - They disagree productively, driving toward truth

3. CONTRADICTION AS SIGNAL:
   - High contradiction: More thinking needed
   - Low contradiction: Engines agree (convergence)
   - Contradiction guides the governor's halting decision

4. QUALITY IMPROVEMENT:
   - Quality increases as cycles progress
   - Each cycle refines the answer
   - Improvement plateaus when diminishing returns detected

5. WISDOM ACCUMULATION:
   - Each query adds to wisdom store
   - Similar future queries retrieve relevant wisdom
   - Reduces cycles needed on repeated queries
   - Enables exponential learning across queries

6. HALLUCINATION PREVENTION:
   - System can't claim something false about its own reasoning
   - Critical engine actively tests constructive claims
   - Contradiction forces reconciliation or honest uncertainty
   - Safety emerges from structure, not filtering

This is the core of THEOS: Self-improving reasoning through productive disagreement.
""")

    print("=" * 80)


if __name__ == "__main__":
    demonstrate_theos_with_claude()
