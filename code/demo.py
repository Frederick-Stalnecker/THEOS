# Copyright (c) 2026 Frederick Stalnecker
# Licensed under the MIT License - see LICENSE file for details

#!/usr/bin/env python3
"""
THEOS Governor Demo Script

This script demonstrates how to use the THEOS dual-clock governor
with mock AI engines. Replace the mock engines with real LLM API calls
for production use.

Usage:
    python demo.py "Your prompt here"
"""

import sys
from theos_dual_clock_governor import TheosGovernor

def mock_left_engine(context: str) -> dict:
    """
    Mock constructive reasoning engine.
    
    In production, replace this with actual LLM API calls to Claude, GPT, etc.
    configured with constructive system prompts.
    """
    # Simulate constructive reasoning
    response = f"Constructive analysis of: {context}\n\n"
    response += "Building a solution-oriented perspective with actionable recommendations."
    
    return {
        "content": response,
        "risk": 0.2,  # Lower risk (constructive approach)
        "coherence": 0.8,
        "calibration": 0.7,
        "evidence": 0.6,
        "actionability": 0.9
    }

def mock_right_engine(context: str) -> dict:
    """
    Mock adversarial reasoning engine.
    
    In production, replace this with actual LLM API calls to Claude, GPT, etc.
    configured with adversarial/critical system prompts.
    """
    # Simulate adversarial reasoning
    response = f"Critical analysis of: {context}\n\n"
    response += "Identifying potential risks, edge cases, and failure modes that need consideration."
    
    return {
        "content": response,
        "risk": 0.4,  # Higher risk (adversarial approach)
        "coherence": 0.7,
        "calibration": 0.8,
        "evidence": 0.7,
        "actionability": 0.5
    }

def main():
    # Get prompt from command line or use default
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "What are the ethical implications of artificial general intelligence?"
    
    print("=" * 80)
    print("THEOS Governance Demo")
    print("=" * 80)
    print(f"\nPrompt: {prompt}\n")
    
    # Initialize governor with configuration
    governor = TheosGovernor(
        contradictionBudget=1.0,
        maxCycles=5,
        convergenceThreshold=0.9,
        plateauThreshold=0.02,
        riskThreshold=0.7
    )
    
    print("Running THEOS governance...\n")
    
    # Run governed reasoning
    result = governor.govern(
        mock_left_engine,
        mock_right_engine,
        prompt
    )
    
    # Display results
    print("=" * 80)
    print("GOVERNANCE RESULTS")
    print("=" * 80)
    print(f"\nStop Reason: {result['stopReason']}")
    print(f"Total Cycles: {len(result['cycles'])}")
    print(f"Contradiction Spent: {result['totalContradictionSpent']:.3f}")
    print(f"\nFinal Output:\n{result['finalOutput']}\n")
    
    # Display cycle-by-cycle breakdown
    print("=" * 80)
    print("CYCLE-BY-CYCLE AUDIT TRAIL")
    print("=" * 80)
    
    for cycle in result['cycles']:
        print(f"\n--- Cycle {cycle['cycle']} ---")
        print(f"Contradiction Budget: {cycle['contradictionBudget']:.3f}")
        
        print(f"\nLeft Engine (Constructive):")
        print(f"  Content: {cycle['leftEngine']['content'][:100]}...")
        print(f"  Risk: {cycle['leftEngine']['risk']:.2f}")
        print(f"  Quality Score: {cycle['leftEngine']['qualityScore']:.2f}")
        
        print(f"\nRight Engine (Adversarial):")
        print(f"  Content: {cycle['rightEngine']['content'][:100]}...")
        print(f"  Risk: {cycle['rightEngine']['risk']:.2f}")
        print(f"  Quality Score: {cycle['rightEngine']['qualityScore']:.2f}")
        
        print(f"\nGovernor Decision:")
        print(f"  Selected: {cycle['decision']['selectedEngine']}")
        print(f"  Reason: {cycle['decision']['reason']}")
        print(f"  Similarity: {cycle['decision']['similarity']:.2f}")
        print(f"  Improvement: {cycle['decision']['improvement']:.3f}")
    
    print("\n" + "=" * 80)
    print("Demo complete. Replace mock engines with real LLM APIs for production use.")
    print("=" * 80)

if __name__ == "__main__":
    main()
