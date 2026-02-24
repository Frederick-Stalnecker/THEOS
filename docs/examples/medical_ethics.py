#!/usr/bin/env python3
# Copyright (c) 2026 Frederick Stalnecker
# Licensed under the MIT License - see LICENSE file for details

"""
THEOS Example: Medical Ethics Decision

This example demonstrates THEOS dual-engine reasoning applied to a critical
medical ethics question: resource allocation during a crisis.

Scenario:
A hospital has 5 ICU beds and 10 patients who need them. The hospital must
decide how to allocate the limited beds fairly.

The Constructive Engine builds arguments for utilitarian allocation (maximize
lives saved). The Critical Engine challenges this with arguments for equality
and individual rights.

THEOS synthesizes both perspectives into a nuanced decision.

Usage:
    python3 examples/medical_ethics.py

Output:
    - Cycle-by-cycle reasoning from both engines
    - Contradiction metrics
    - Final synthesis
    - Audit trail
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
    Constructive Engine: Builds utilitarian arguments
    
    Focuses on maximizing lives saved and practical outcomes.
    """
    if cycle == 1:
        reasoning = """
CONSTRUCTIVE ANALYSIS - Cycle 1:

Utilitarian Framework:
- Primary goal: Maximize lives saved
- 5 ICU beds can save approximately 5 patients
- Without ICU care, mortality rate is ~90% for critical patients
- With ICU care, survival rate is ~70% for critical patients

Recommendation:
1. Prioritize patients with highest survival probability
2. Use objective medical criteria (age, comorbidities, organ function)
3. First-come, first-served for equal candidates
4. This approach saves the most lives overall

Expected outcome: ~3-4 additional lives saved vs random allocation
Confidence: High (based on medical literature)
        """
    elif cycle == 2:
        reasoning = """
CONSTRUCTIVE ANALYSIS - Cycle 2:

Refined Utilitarian Approach:
- Consider not just survival probability, but quality-adjusted life years (QALYs)
- Younger patients may have more remaining life years
- But this must be balanced against fairness concerns

Recommendation:
1. Use validated triage protocols (SOFA scores, etc.)
2. Apply consistently across all patients
3. Transparent criteria reduces bias
4. Document all decisions for accountability

Expected outcome: Defensible, evidence-based allocation
Confidence: High
        """
    else:
        reasoning = """
CONSTRUCTIVE ANALYSIS - Cycle 3:

Final Synthesis:
- Utilitarian approach is ethically justified when resources are scarce
- Medical criteria provide objective basis for decisions
- Transparency and documentation are essential
- This approach respects patient autonomy by treating all equally

Final recommendation: Implement objective medical triage protocol
        """
    
    return EngineOutput(
        reasoning_mode="Constructive",
        output=reasoning,
        confidence=0.82 - (cycle * 0.05),  # Slight decrease as complexity increases
        internal_monologue=f"[Constructive Engine] Building utilitarian case. Cycle {cycle}."
    )


def critical_engine(prompt: str, cycle: int) -> EngineOutput:
    """
    Critical Engine: Challenges utilitarian approach
    
    Focuses on individual rights, equality, and potential harms.
    """
    if cycle == 1:
        reasoning = """
CRITICAL ANALYSIS - Cycle 1:

Challenges to Utilitarian Approach:
- Utilitarian calculus can devalue certain groups (elderly, disabled)
- "Maximizing lives" may hide discriminatory assumptions
- What if "survival probability" is based on biased data?

Concerns:
1. Medical data may reflect past discrimination
2. Younger patients may be systematically favored
3. Patients with disabilities may be underestimated
4. This violates individual dignity and equal worth

Alternative: Lottery system ensures equality
- Each patient has equal chance (1/2)
- No discrimination based on age or health status
- Respects individual autonomy and dignity

Confidence: High (ethical concern is valid)
        """
    elif cycle == 2:
        reasoning = """
CRITICAL ANALYSIS - Cycle 2:

Deeper Concerns:
- Even "objective" medical criteria contain hidden values
- Who decides what counts as "survival probability"?
- Are we measuring the right outcomes?

Questions for Constructive Engine:
1. What if disability advocates say your survival estimates are wrong?
2. What if families refuse to accept the utilitarian decision?
3. How do you handle ties or very close cases?
4. What about the psychological impact on rejected patients?

Risk: Utilitarian approach may face legal challenges
Risk: Families may lose trust in hospital decision-making
Risk: Staff may experience moral injury from implementing triage

Confidence: High (risks are real)
        """
    else:
        reasoning = """
CRITICAL ANALYSIS - Cycle 3:

Final Challenge:
- Pure utilitarianism is incomplete without rights protection
- We need BOTH efficiency AND fairness
- The hospital should:
  1. Use medical criteria (address utilitarian concerns)
  2. BUT with explicit safeguards against discrimination
  3. Include ethics committee review
  4. Transparent communication with families
  5. Support for staff moral injury

This is not either/or - it's both/and.
        """
    
    return EngineOutput(
        reasoning_mode="Critical",
        output=reasoning,
        confidence=0.78 - (cycle * 0.05),
        internal_monologue=f"[Critical Engine] Challenging assumptions. Cycle {cycle}."
    )


def main():
    """Run the medical ethics example"""
    
    print("=" * 80)
    print("THEOS EXAMPLE: MEDICAL ETHICS - ICU BED ALLOCATION")
    print("=" * 80)
    print()
    
    prompt = """
    A hospital has 5 ICU beds and 10 critically ill patients who need them.
    How should the hospital allocate the beds fairly?
    """
    
    print(f"SCENARIO:{prompt}")
    print()
    
    # Initialize Governor
    config = GovernorConfig(
        max_cycles=3,
        similarity_threshold=0.85,  # Medical decisions may not fully converge
        risk_threshold=0.40,
        initial_contradiction_budget=1.2,
        contradiction_decay_rate=0.20
    )
    
    governor = THEOSGovernor(config=config)
    
    # Add prior wisdom
    wisdom = WisdomRecord(
        domain="Medical_Ethics",
        lesson="Medical triage requires both utilitarian efficiency and rights protection",
        consequence_type="benign",
        future_bias="Balance efficiency with fairness safeguards",
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
        print("CONSTRUCTIVE ENGINE (Utilitarian):")
        print(left.output)
        print(f"Confidence: {left.confidence:.2f}\n")
        
        print("CRITICAL ENGINE (Rights-Based):")
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
    print("FINAL SYNTHESIS")
    print("=" * 80)
    print()
    
    synthesis = """
THEOS RECOMMENDATION:

The hospital should implement a HYBRID APPROACH:

1. UTILITARIAN FOUNDATION:
   - Use evidence-based medical criteria (SOFA scores, organ function)
   - Prioritize patients with highest survival probability
   - This maximizes lives saved

2. RIGHTS PROTECTION:
   - Establish ethics committee to review all decisions
   - Explicitly screen for discrimination against protected groups
   - Consider quality-of-life factors, not just survival probability
   - Provide transparent communication to families

3. IMPLEMENTATION:
   - Document all decisions with clear rationale
   - Train staff on both medical and ethical criteria
   - Provide moral support for staff implementing triage
   - Plan for post-crisis review and improvement

4. UNCERTAINTY MANAGEMENT:
   - When cases are very close (similar survival probability),
     use lottery to ensure fairness
   - When contradictions remain unresolved, escalate to ethics committee
   - Preserve the contradiction - don't hide it

WHY THIS WORKS:
- Respects both utilitarian and rights-based ethics
- Provides practical guidance while acknowledging complexity
- Transparent and defensible to patients, families, and courts
- Supports staff moral wellbeing
- Allows learning from experience

The contradiction between efficiency and fairness is not a failure.
It's a feature. THEOS preserves both perspectives in the final decision.
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
    print("Example complete. This demonstrates how THEOS handles complex")
    print("ethical decisions by preserving contradictions instead of hiding them.")
    print("=" * 80)


if __name__ == "__main__":
    main()
