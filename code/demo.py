#!/usr/bin/env python3
# Copyright (c) 2026 Frederick Davis Stalnecker
# Licensed under the MIT License - see LICENSE file for details

"""
THEOS Governor Demo Script

This script demonstrates how to use the THEOS dual-clock governor
with mock AI engines. Replace the mock engines with real LLM API calls
for production use.

Usage:
    python demo.py
    python demo.py "Your prompt here"
"""

import sys
from theos_dual_clock_governor import (
    TheosDualClockGovernor, 
    GovernorConfig, 
    EngineOutput
)


def mock_left_engine(cycle: int, context: str) -> EngineOutput:
    """
    Mock constructive reasoning engine.
    
    In production, replace this with actual LLM API calls to Claude, GPT, etc.
    configured with constructive system prompts.
    """
    # Simulate constructive reasoning
    response = f"Constructive analysis of: {context}\n"
    response += "Building a solution-oriented perspective with actionable recommendations."
    
    return EngineOutput(
        engine_id="L",
        cycle_index=cycle,
        answer=response,
        coherence=0.8,
        calibration=0.7,
        evidence=0.6,
        actionability=0.9,
        risk=0.2,
        constraint_ok=True
    )


def mock_right_engine(cycle: int, context: str) -> EngineOutput:
    """
    Mock adversarial reasoning engine.
    
    In production, replace this with actual LLM API calls to Claude, GPT, etc.
    configured with adversarial/critical system prompts.
    """
    # Simulate adversarial reasoning
    response = f"Critical analysis of: {context}\n"
    response += "Identifying potential risks, edge cases, and failure modes that need consideration."
    
    return EngineOutput(
        engine_id="R",
        cycle_index=cycle,
        answer=response,
        coherence=0.7,
        calibration=0.8,
        evidence=0.7,
        actionability=0.5,
        risk=0.4,
        constraint_ok=True
    )


def main():
    # Get prompt from command line or use default
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "What are the ethical implications of artificial general intelligence?"
    
    print("=" * 80)
    print("THEOS Dual-Clock Governor Demo")
    print("=" * 80)
    print(f"\nPrompt: {prompt}\n")
    
    # Initialize governor with configuration
    config = GovernorConfig(
        max_cycles=5,
        max_risk=0.7,
        min_improvement=0.02,
        plateau_cycles=2,
        contradiction_budget=1.5,
        similarity_converge=0.9
    )
    governor = TheosDualClockGovernor(config)
    
    print("Running THEOS governance...\n")
    
    # Run multi-cycle governed reasoning
    cycle = 0
    decision = None
    cycles_data = []
    
    while cycle < config.max_cycles:
        cycle += 1
        print(f"--- Cycle {cycle} ---")
        
        # Get outputs from both engines
        left_output = mock_left_engine(cycle, prompt)
        right_output = mock_right_engine(cycle, prompt)
        
        # Governor makes decision
        decision = governor.step(left_output, right_output)
        
        # Record cycle data
        cycle_data = {
            "cycle": cycle,
            "left_engine": {
                "content": left_output.answer[:80] + "...",
                "coherence": left_output.coherence,
                "calibration": left_output.calibration,
                "evidence": left_output.evidence,
                "actionability": left_output.actionability,
                "risk": left_output.risk,
                "score": governor.score(left_output)
            },
            "right_engine": {
                "content": right_output.answer[:80] + "...",
                "coherence": right_output.coherence,
                "calibration": right_output.calibration,
                "evidence": right_output.evidence,
                "actionability": right_output.actionability,
                "risk": right_output.risk,
                "score": governor.score(right_output)
            },
            "decision": {
                "selected_engine": decision.chosen_engine,
                "reason": decision.reason,
                "similarity": decision.audit.get("similarity", 0.0),
                "contradiction_spent": decision.audit.get("contradiction_spent", 0.0)
            }
        }
        cycles_data.append(cycle_data)
        
        # Display cycle results
        print(f"Left Engine Score: {cycle_data['left_engine']['score']:.2f}")
        print(f"Right Engine Score: {cycle_data['right_engine']['score']:.2f}")
        print(f"Selected: Engine {decision.chosen_engine}")
        print(f"Reason: {decision.reason}")
        print(f"Similarity: {cycle_data['decision']['similarity']:.2f}")
        print(f"Contradiction Spent: {cycle_data['decision']['contradiction_spent']:.3f}")
        print()
        
        # Check stop condition
        if decision.decision == "FREEZE":
            print(f"Governor FREEZE triggered: {decision.reason}")
            break
    
    # Display final results
    print("=" * 80)
    print("GOVERNANCE RESULTS")
    print("=" * 80)
    print(f"\nStop Reason: {decision.reason}")
    print(f"Total Cycles: {cycle}")
    print(f"Contradiction Spent: {governor.contradiction_spent:.3f}")
    print(f"Final Answer:\n{decision.chosen_answer}\n")
    
    # Display cycle-by-cycle breakdown
    print("=" * 80)
    print("CYCLE-BY-CYCLE AUDIT TRAIL")
    print("=" * 80)
    
    for cycle_data in cycles_data:
        print(f"\n--- Cycle {cycle_data['cycle']} ---")
        print(f"\nLeft Engine (Constructive):")
        print(f"  Content: {cycle_data['left_engine']['content']}")
        print(f"  Coherence: {cycle_data['left_engine']['coherence']:.2f}")
        print(f"  Calibration: {cycle_data['left_engine']['calibration']:.2f}")
        print(f"  Evidence: {cycle_data['left_engine']['evidence']:.2f}")
        print(f"  Actionability: {cycle_data['left_engine']['actionability']:.2f}")
        print(f"  Risk: {cycle_data['left_engine']['risk']:.2f}")
        print(f"  Score: {cycle_data['left_engine']['score']:.2f}")
        
        print(f"\nRight Engine (Adversarial):")
        print(f"  Content: {cycle_data['right_engine']['content']}")
        print(f"  Coherence: {cycle_data['right_engine']['coherence']:.2f}")
        print(f"  Calibration: {cycle_data['right_engine']['calibration']:.2f}")
        print(f"  Evidence: {cycle_data['right_engine']['evidence']:.2f}")
        print(f"  Actionability: {cycle_data['right_engine']['actionability']:.2f}")
        print(f"  Risk: {cycle_data['right_engine']['risk']:.2f}")
        print(f"  Score: {cycle_data['right_engine']['score']:.2f}")
        
        print(f"\nGovernor Decision:")
        print(f"  Selected: Engine {cycle_data['decision']['selected_engine']}")
        print(f"  Reason: {cycle_data['decision']['reason']}")
        print(f"  Similarity: {cycle_data['decision']['similarity']:.2f}")
        print(f"  Contradiction Spent: {cycle_data['decision']['contradiction_spent']:.3f}")
    
    print("\n" + "=" * 80)
    print("Demo complete. Replace mock engines with real LLM APIs for production use.")
    print("=" * 80)


if __name__ == "__main__":
    main()
