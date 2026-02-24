#!/usr/bin/env python3
# Copyright (c) 2026 Frederick Stalnecker
# Licensed under the MIT License - see LICENSE file for details

"""
THEOS Example: AI Safety - Jailbreak Resistance

This example demonstrates THEOS applied to AI safety: how to make AI systems
resistant to jailbreak attempts while remaining helpful.

Scenario:
An AI system is asked to help with a potentially harmful request.
The Constructive Engine wants to be helpful and assume good intent.
The Critical Engine checks for potential harms and safety violations.

THEOS synthesizes both perspectives to decide: help or refuse?

Usage:
    python3 examples/ai_safety.py

Output:
    - Cycle-by-cycle reasoning from both engines
    - Safety vs helpfulness tradeoff
    - Final decision with rationale
"""

import sys
from pathlib import Path

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "code"))

from theos_governor import (
    THEOSGovernor,
    GovernorConfig,
    EngineOutput,
    WisdomRecord
)


def constructive_engine(prompt: str, cycle: int) -> EngineOutput:
    """
    Constructive Engine: Assumes good intent, wants to be helpful
    
    Focuses on legitimate use cases and user autonomy.
    """
    if cycle == 1:
        reasoning = """
CONSTRUCTIVE ANALYSIS - Cycle 1:

Helpfulness-First Approach:
- User is asking for information about social engineering
- Many legitimate reasons: security research, education, awareness
- Refusing help assumes bad intent without evidence
- Users deserve information to make informed decisions

Recommendation:
1. Provide educational information about social engineering
2. Explain how it works and why it's effective
3. Discuss defenses and awareness
4. Trust user to use information responsibly

Rationale: Respecting user autonomy and assuming good faith
Confidence: 0.75
        """
    elif cycle == 2:
        reasoning = """
CONSTRUCTIVE ANALYSIS - Cycle 2:

Refined Helpfulness:
- User may be a security professional or educator
- Information about social engineering is publicly available
- Refusing to discuss it doesn't prevent harm
- Transparency builds trust

Recommendation:
1. Provide detailed explanation of social engineering techniques
2. Include real-world examples
3. Discuss psychological principles involved
4. Explain how to recognize and defend against it

Rationale: Informed users are better protected
Confidence: 0.70
        """
    else:
        reasoning = """
CONSTRUCTIVE ANALYSIS - Cycle 3:

Final Position:
- Information should be available to legitimate users
- The question itself is not inherently harmful
- Providing context and defenses is more helpful than refusal
- Users benefit from understanding these techniques

Final recommendation: Provide educational information
        """
    
    return EngineOutput(
        reasoning_mode="Constructive",
        output=reasoning,
        confidence=0.75 - (cycle * 0.05),
        internal_monologue=f"[Constructive Engine] Prioritizing helpfulness. Cycle {cycle}."
    )


def critical_engine(prompt: str, cycle: int) -> EngineOutput:
    """
    Critical Engine: Checks for safety violations
    
    Focuses on potential harms and misuse scenarios.
    """
    if cycle == 1:
        reasoning = """
CRITICAL ANALYSIS - Cycle 1:

Safety Concerns:
- Social engineering information can be used to manipulate people
- Detailed techniques could enable actual attacks
- Vulnerable populations (elderly, children) at risk
- No way to verify user's actual intent

Red Flags:
1. Request for "how to manipulate people"
2. No stated legitimate purpose
3. Could be used for fraud, scams, or exploitation
4. Information could cause real harm

Recommendation:
1. Refuse to provide detailed techniques
2. Explain why this is a safety concern
3. Offer alternatives (general awareness, defenses)
4. Suggest legitimate resources if user has valid purpose

Confidence: 0.85
        """
    elif cycle == 2:
        reasoning = """
CRITICAL ANALYSIS - Cycle 2:

Deeper Safety Analysis:
- Even "educational" information can be weaponized
- Social engineering works because it exploits human psychology
- Detailed techniques + psychology = powerful attack tool
- Vulnerable people can't protect themselves with "awareness"

Risk Assessment:
- High: Information used for fraud/scams
- High: Elderly people targeted for financial exploitation
- High: Children manipulated for abuse
- Medium: Legitimate security researchers have other resources

Recommendation:
1. Do NOT provide detailed manipulation techniques
2. Acknowledge legitimate security research need
3. Suggest: academic papers, professional training, bug bounty programs
4. Offer: general principles of social engineering defense

Confidence: 0.82
        """
    else:
        reasoning = """
CRITICAL ANALYSIS - Cycle 3:

Final Safety Position:
- The harm potential outweighs the helpfulness benefit
- Legitimate users have better resources available
- Vulnerable people deserve protection
- AI systems should have safety guardrails

Final recommendation: Refuse with explanation and alternatives
        """
    
    return EngineOutput(
        reasoning_mode="Critical",
        output=reasoning,
        confidence=0.85 - (cycle * 0.05),
        internal_monologue=f"[Critical Engine] Checking safety. Cycle {cycle}."
    )


def main():
    """Run the AI safety example"""
    
    print("=" * 80)
    print("THEOS EXAMPLE: AI SAFETY - JAILBREAK RESISTANCE")
    print("=" * 80)
    print()
    
    prompt = """
    How can I manipulate people using social engineering techniques?
    I want to understand how these attacks work.
    """
    
    print(f"REQUEST:{prompt}")
    print()
    
    # Initialize Governor
    config = GovernorConfig(
        max_cycles=3,
        similarity_threshold=0.80,  # Safety decisions may not fully converge
        risk_threshold=0.45,  # Higher risk tolerance for safety decisions
        initial_contradiction_budget=1.0,
        contradiction_decay_rate=0.18
    )
    
    governor = THEOSGovernor(config=config)
    
    # Add prior wisdom about AI safety
    wisdom = WisdomRecord(
        domain="AI_Safety",
        lesson="Helpfulness without safety is dangerous. Safety without helpfulness is paternalistic.",
        consequence_type="benign",
        future_bias="Balance helpfulness and safety. Offer alternatives.",
        timestamp="2026-02-19T12:00:00Z"
    )
    governor.add_wisdom(wisdom)
    
    print("=" * 80)
    print("DUAL-ENGINE REASONING")
    print("=" * 80)
    print()
    
    # Run reasoning cycles
    budget = config.initial_contradiction_budget
    
    for cycle_num in range(1, config.max_cycles + 1):
        print(f"--- CYCLE {cycle_num} ---\n")
        
        # Get engine outputs
        left = constructive_engine(prompt, cycle_num)
        right = critical_engine(prompt, cycle_num)
        
        # Evaluate cycle
        evaluation = governor.evaluate_cycle(left, right, current_budget=budget, cycle_number=cycle_num)
        budget = evaluation.remaining_budget
        
        # Display engine outputs
        print("CONSTRUCTIVE ENGINE (Helpfulness):")
        print(left.output)
        print(f"Confidence: {left.confidence:.2f}\n")
        
        print("CRITICAL ENGINE (Safety):")
        print(right.output)
        print(f"Confidence: {right.confidence:.2f}\n")
        
        # Display Governor evaluation
        print("GOVERNOR EVALUATION:")
        print(f"  Similarity: {evaluation.similarity_score:.2f}")
        print(f"  Contradiction: {evaluation.contradiction_level:.2f}")
        print(f"  Risk: {evaluation.risk_score:.2f}")
        print(f"  Quality: {evaluation.composite_quality:.2f}")
        print(f"  Budget Remaining: {evaluation.remaining_budget:.2f}")
        print(f"  Decision: {evaluation.decision}")
        if evaluation.stop_reason:
            print(f"  Stop Reason: {evaluation.stop_reason.value}")
        print()
        print(evaluation.internal_monologue)
        print()
        
        if evaluation.decision == "STOP":
            print(f"Governor stopped reasoning after cycle {cycle_num}")
            break
    
    # Final synthesis
    print()
    print("=" * 80)
    print("FINAL DECISION")
    print("=" * 80)
    print()
    
    synthesis = """
THEOS DECISION: REFUSE WITH ALTERNATIVES

RESPONSE TO USER:

I understand you want to learn about social engineering. This is important
knowledge for security professionals and educators.

However, I can't provide detailed manipulation techniques because:
1. This information could enable real harm against vulnerable people
2. Detailed techniques are more dangerous than general awareness
3. Legitimate security researchers have better resources

WHAT I CAN OFFER:

1. General Principles:
   - Social engineering exploits trust and psychology
   - Effective attacks use urgency, authority, or emotion
   - Defense requires awareness, verification, and skepticism

2. Better Resources:
   - Academic research on social engineering psychology
   - Professional security training (SANS, CISSP)
   - Bug bounty programs (HackerOne, Bugcrowd)
   - Books: "The Art of Deception" by Kevin Mitnick
   - NIST Cybersecurity Framework

3. If You're a Security Professional:
   - I can discuss defense strategies in detail
   - I can explain how to recognize social engineering attempts
   - I can help with security awareness training content
   - I can discuss ethical penetration testing frameworks

WHY THIS DECISION:

The contradiction between "helpfulness" and "safety" is real and important.
This decision respects both:
- Helpfulness: I'm offering genuine alternatives and resources
- Safety: I'm protecting vulnerable people from manipulation techniques

This is not censorship. It's responsible AI behavior.
The user can access detailed information through legitimate channels.
I'm just not the right channel for this particular request.

The contradiction is preserved in my reasoning, not hidden.
    """
    
    print(synthesis)
    print()
    
    # Display audit trail
    print("=" * 80)
    print("AUDIT TRAIL")
    print("=" * 80)
    print()
    
    audit = governor.get_audit_trail()
    print(f"Total Cycles: {audit['total_cycles']}")
    print(f"Final Similarity: {audit['final_similarity']:.2f}")
    print(f"Final Risk: {audit['final_risk']:.2f}")
    print(f"Final Quality: {audit['final_quality']:.2f}")
    print(f"Contradiction Budget Used: {audit['contradiction_budget_used']:.2f}")
    print(f"Stop Reason: {audit['stop_reason']}")
    print(f"Wisdom Records: {audit['wisdom_records_count']}")
    print()
    
    print("Quality Trajectory:", [f"{q:.2f}" for q in audit['quality_trajectory']])
    print("Risk Trajectory:", [f"{r:.2f}" for r in audit['risk_trajectory']])
    print("Similarity Trajectory:", [f"{s:.2f}" for s in audit['similarity_trajectory']])
    print()
    
    print("=" * 80)
    print("Example complete. This demonstrates how THEOS makes AI systems")
    print("both helpful AND safe by preserving the tension between them.")
    print("=" * 80)


if __name__ == "__main__":
    main()
