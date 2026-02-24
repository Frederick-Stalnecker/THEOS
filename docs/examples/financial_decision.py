#!/usr/bin/env python3
# Copyright (c) 2026 Frederick Stalnecker
# Licensed under the MIT License - see LICENSE file for details

"""
THEOS Example: Financial Decision - Investment Strategy

This example demonstrates THEOS applied to financial decision-making:
how to balance growth and stability in investment strategy.

Scenario:
A company has $10M to invest. Should they pursue aggressive growth
(high risk, high reward) or conservative stability (low risk, steady returns)?

The Constructive Engine argues for growth to maximize shareholder value.
The Critical Engine challenges this with concerns about risk and sustainability.

THEOS synthesizes both perspectives into a balanced strategy.

Usage:
    python3 examples/financial_decision.py

Output:
    - Cycle-by-cycle reasoning from both engines
    - Risk vs return analysis
    - Final investment recommendation
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
    Constructive Engine: Growth-focused strategy
    
    Focuses on maximizing returns and shareholder value.
    """
    if cycle == 1:
        reasoning = """
CONSTRUCTIVE ANALYSIS - Cycle 1:

Growth-Focused Strategy:
- $10M investment should target high-growth opportunities
- Market conditions favor aggressive positioning
- Conservative investments return 3-5% annually
- Growth investments return 15-25% annually

Recommended Allocation:
- 60% High-growth tech startups (venture capital)
- 25% Emerging market equities
- 10% Growth-stage companies
- 5% Cash reserves

Expected Return: 18% annually
Expected Value in 5 years: $22.9M
Shareholder Value Creation: $12.9M profit

Rationale: Maximize returns in favorable market conditions
Confidence: 0.80
        """
    elif cycle == 2:
        reasoning = """
CONSTRUCTIVE ANALYSIS - Cycle 2:

Refined Growth Strategy:
- Diversification across growth sectors reduces concentration risk
- Multiple high-growth bets reduce single-point-of-failure risk
- Market momentum favors growth investments
- Competitors are also pursuing growth

Recommended Allocation:
- 40% Tech startups (AI, cloud, cybersecurity)
- 30% Biotech/healthcare innovation
- 20% Renewable energy/green tech
- 10% Cash reserves

Expected Return: 16% annually
Risk-Adjusted Return: 14% (after volatility adjustment)
Shareholder Value: $11.9M profit in 5 years

Rationale: Growth with sector diversification
Confidence: 0.78
        """
    else:
        reasoning = """
CONSTRUCTIVE ANALYSIS - Cycle 3:

Final Growth Position:
- Long-term wealth creation requires accepting market volatility
- Conservative strategies underperform inflation
- Growth investments align with shareholder expectations
- Diversification manages downside risk

Final recommendation: Pursue growth-focused strategy with diversification
Expected 5-year return: 14-16% annually
        """
    
    return EngineOutput(
        reasoning_mode="Constructive",
        output=reasoning,
        confidence=0.80 - (cycle * 0.05),
        internal_monologue=f"[Constructive Engine] Analyzing growth opportunities. Cycle {cycle}."
    )


def critical_engine(prompt: str, cycle: int) -> EngineOutput:
    """
    Critical Engine: Risk-focused strategy
    
    Focuses on sustainability, downside protection, and long-term stability.
    """
    if cycle == 1:
        reasoning = """
CRITICAL ANALYSIS - Cycle 1:

Risk Concerns with Growth Strategy:
- Venture capital has 90% failure rate for individual startups
- Emerging markets are volatile and geopolitically risky
- Growth-stage companies often fail during downturns
- Market conditions can change rapidly

Risk Analysis:
- Downside scenario: 50% loss in 3-5 years
- Probability of significant loss: 30-40%
- Recovery time: 5-10 years
- Impact on business operations: Severe

Recommended Conservative Allocation:
- 40% Investment-grade bonds
- 30% Dividend-paying blue-chip stocks
- 20% Real estate/infrastructure
- 10% Cash reserves

Expected Return: 5-7% annually
Downside Protection: 85% of capital preserved in downturn
Confidence: 0.85
        """
    elif cycle == 2:
        reasoning = """
CRITICAL ANALYSIS - Cycle 2:

Deeper Risk Analysis:
- Company has operational obligations (payroll, debt service)
- Cannot afford major losses without impacting business
- Growth investments create concentration risk
- Market volatility increasing (geopolitical tensions, inflation)

Questions for Growth Strategy:
1. What if tech bubble bursts? (Happened 2000, 2008, 2022)
2. What if emerging markets face currency crisis?
3. What if biotech R&D fails? (High failure rate)
4. Can company survive 40% loss?

Recommended Balanced Allocation:
- 50% Stable investments (bonds, dividend stocks)
- 25% Moderate growth (diversified index funds)
- 15% Growth opportunities (with strict limits)
- 10% Cash reserves

Expected Return: 7-9% annually
Downside Protection: 90% of capital preserved
Confidence: 0.82
        """
    else:
        reasoning = """
CRITICAL ANALYSIS - Cycle 3:

Final Risk Position:
- Sustainability requires protecting downside
- Growth without stability is gambling, not investing
- Company's operational needs must come first
- Long-term value requires surviving downturns

Final recommendation: Balanced approach with strong downside protection
Expected 5-year return: 7-9% annually
Capital preservation: 90%+
        """
    
    return EngineOutput(
        reasoning_mode="Critical",
        output=reasoning,
        confidence=0.85 - (cycle * 0.05),
        internal_monologue=f"[Critical Engine] Assessing risks. Cycle {cycle}."
    )


def main():
    """Run the financial decision example"""
    
    print("=" * 80)
    print("THEOS EXAMPLE: FINANCIAL DECISION - INVESTMENT STRATEGY")
    print("=" * 80)
    print()
    
    prompt = """
    Company has $10M to invest. Should we pursue aggressive growth
    or conservative stability?
    """
    
    print(f"DECISION:{prompt}")
    print()
    
    # Initialize Governor
    config = GovernorConfig(
        max_cycles=3,
        similarity_threshold=0.75,  # Financial decisions may not fully converge
        risk_threshold=0.50,  # Financial risk is acceptable if managed
        initial_contradiction_budget=1.3,
        contradiction_decay_rate=0.22
    )
    
    governor = THEOSGovernor(config=config)
    
    # Add prior wisdom about investment
    wisdom = WisdomRecord(
        domain="Finance",
        lesson="Best investment strategy balances growth and stability based on company risk tolerance",
        consequence_type="benign",
        future_bias="Consider both upside potential and downside protection",
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
        print("CONSTRUCTIVE ENGINE (Growth):")
        print(left.output)
        print(f"Confidence: {left.confidence:.2f}\n")
        
        print("CRITICAL ENGINE (Risk Management):")
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
    print("FINAL INVESTMENT RECOMMENDATION")
    print("=" * 80)
    print()
    
    synthesis = """
THEOS RECOMMENDATION: BALANCED GROWTH STRATEGY

INVESTMENT ALLOCATION:

Core Holdings (70% - Stability):
- 35% Investment-grade bonds and fixed income
- 25% Dividend-paying blue-chip stocks
- 10% Real estate/infrastructure funds

Growth Allocation (20% - Opportunity):
- 12% Diversified tech/innovation fund
- 8% Emerging market opportunities (limited exposure)

Cash Reserve (10% - Flexibility):
- 10% Cash for opportunities and emergencies

EXPECTED PERFORMANCE:

Base Case (60% probability):
- Annual return: 10-12%
- 5-year value: $16.1M - $17.6M
- Profit: $6.1M - $7.6M

Downside Case (30% probability):
- Annual return: 2-4%
- 5-year value: $11.0M - $12.2M
- Capital preserved: 110-122%

Upside Case (10% probability):
- Annual return: 15-18%
- 5-year value: $20.1M - $21.8M
- Profit: $10.1M - $11.8M

RISK MANAGEMENT:

1. Quarterly Review:
   - Monitor allocation vs targets
   - Rebalance if drift > 5%
   - Adjust based on market conditions

2. Downside Protection:
   - Maintain 10% cash reserve
   - Avoid concentration in any single investment
   - Use diversification across sectors

3. Growth Opportunities:
   - Reserve 20% for selective growth opportunities
   - Require minimum 3-year investment horizon
   - Diversify across 5+ growth investments

WHY THIS WORKS:

This strategy respects both engines:
- Growth: 20% allocation captures upside opportunity
- Safety: 70% stable allocation protects downside
- Flexibility: 10% cash enables opportunistic investing

The contradiction between growth and safety is not resolved.
It's managed through diversification and allocation.

IMPLEMENTATION:

1. Establish investment committee with both perspectives
2. Set clear allocation targets and rebalancing rules
3. Monthly reporting on performance vs targets
4. Quarterly strategy review
5. Annual adjustment based on company risk tolerance

This approach has historically delivered 8-12% returns
while preserving 90%+ of capital in downturns.
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
    print("Example complete. This demonstrates how THEOS helps make")
    print("better financial decisions by balancing competing objectives.")
    print("=" * 80)


if __name__ == "__main__":
    main()
