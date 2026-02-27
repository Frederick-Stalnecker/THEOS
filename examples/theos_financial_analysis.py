#!/usr/bin/env python3
"""
THEOS Financial Analysis Example
=================================

Demonstrates THEOS dual-engine reasoning for financial decision-making with:
- Constructive engine (L): Bullish analysis and opportunity identification
- Critical engine (R): Risk assessment and downside scenario analysis
- Governor: Halting when confidence is sufficient

This example shows how THEOS can improve investment decisions by:
1. Generating investment theses
2. Critically stress-testing assumptions
3. Measuring productive disagreement about risk
4. Accumulating investment wisdom

Author: Frederick Davis Stalnecker
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

import json
from typing import Any

from theos_system import TheosConfig, create_numeric_system


class FinancialAnalysisEngine:
    """THEOS-based financial analysis system."""

    def __init__(self):
        """Initialize with financial knowledge base."""
        # Market factors and their typical impact
        self.market_factors = {
            "interest_rates": {"bullish": -0.3, "bearish": 0.4},
            "inflation": {"bullish": -0.2, "bearish": 0.3},
            "GDP_growth": {"bullish": 0.4, "bearish": -0.3},
            "unemployment": {"bullish": -0.2, "bearish": 0.3},
            "earnings_growth": {"bullish": 0.5, "bearish": -0.4},
        }

        # Risk factors
        self.risk_factors = {
            "high_valuation": 0.4,
            "sector_concentration": 0.3,
            "geopolitical_risk": 0.35,
            "regulatory_risk": 0.25,
            "execution_risk": 0.3,
        }

        # Initialize THEOS system
        config = TheosConfig(
            max_cycles=5,
            eps_converge=0.1,
            verbose=False,
        )
        self.theos = create_numeric_system(config)

    def analyze_investment(
        self,
        asset: str,
        bullish_factors: list[str],
        bearish_factors: list[str],
        risk_factors: list[str],
    ) -> dict[str, Any]:
        """
        Run THEOS reasoning for investment analysis.

        Args:
            asset: Asset name/ticker
            bullish_factors: Factors supporting the investment
            bearish_factors: Factors against the investment
            risk_factors: Risk factors to consider

        Returns:
            Investment analysis with recommendation
        """
        # Build query
        query = self._build_query(asset, bullish_factors, bearish_factors, risk_factors)

        # Run THEOS reasoning
        result = self.theos.reason(query)

        # Interpret result
        analysis = self._interpret_result(
            result,
            asset,
            bullish_factors,
            bearish_factors,
            risk_factors,
        )

        return analysis

    def _build_query(
        self,
        asset: str,
        bullish_factors: list[str],
        bearish_factors: list[str],
        risk_factors: list[str],
    ) -> str:
        """Build query string for THEOS."""
        query_parts = [
            f"Asset: {asset}",
            f"Bullish: {', '.join(bullish_factors)}",
            f"Bearish: {', '.join(bearish_factors)}",
            f"Risks: {', '.join(risk_factors)}",
        ]
        return " | ".join(query_parts)

    def _interpret_result(
        self,
        result,
        asset: str,
        bullish_factors: list[str],
        bearish_factors: list[str],
        risk_factors: list[str],
    ) -> dict[str, Any]:
        """Interpret THEOS result as investment recommendation."""
        # Calculate bullish score
        bullish_score = len(bullish_factors) / max(len(bullish_factors) + len(bearish_factors), 1)

        # Calculate risk score
        risk_score = len(risk_factors) / 5.0  # Normalize to 5 possible risks

        # Combine with THEOS confidence
        base_confidence = result.confidence
        adjusted_confidence = 0.4 * base_confidence + 0.3 * bullish_score + 0.3 * (1.0 - risk_score)

        # Generate recommendation
        recommendation = self._get_recommendation(
            adjusted_confidence,
            bullish_score,
            risk_score,
        )

        return {
            "asset": asset,
            "bullish_factors": bullish_factors,
            "bearish_factors": bearish_factors,
            "risk_factors": risk_factors,
            "bullish_score": round(bullish_score, 3),
            "risk_score": round(risk_score, 3),
            "theos_confidence": round(result.confidence, 3),
            "adjusted_confidence": round(adjusted_confidence, 3),
            "cycles_used": result.cycles_used,
            "halt_reason": result.halt_reason.value,
            "wisdom_entries": len(self.theos.core.wisdom),
            "recommendation": recommendation,
        }

    def _get_recommendation(
        self,
        confidence: float,
        bullish_score: float,
        risk_score: float,
    ) -> str:
        """Get investment recommendation based on analysis."""
        if confidence > 0.75 and bullish_score > 0.6 and risk_score < 0.4:
            return "STRONG BUY - High conviction with manageable risks"
        elif confidence > 0.65 and bullish_score > 0.5 and risk_score < 0.5:
            return "BUY - Positive outlook with acceptable risk profile"
        elif confidence > 0.5 and bullish_score > 0.4:
            return "HOLD - Mixed signals, monitor for clarity"
        elif bullish_score < 0.4 or risk_score > 0.6:
            return "SELL - Risk-reward unfavorable"
        else:
            return "WAIT - Insufficient conviction, need more data"


def run_financial_examples():
    """Run financial analysis examples."""
    engine = FinancialAnalysisEngine()

    print("\n" + "=" * 70)
    print("THEOS Financial Analysis System - Examples")
    print("=" * 70)

    # Example 1: Growth Stock
    print("\n--- Example 1: Growth Tech Stock ---")
    result1 = engine.analyze_investment(
        asset="TECH-GROWTH-001",
        bullish_factors=[
            "earnings_growth",
            "market_expansion",
            "product_innovation",
        ],
        bearish_factors=[
            "high_valuation",
            "competition",
        ],
        risk_factors=[
            "high_valuation",
            "execution_risk",
            "regulatory_risk",
        ],
    )
    print(json.dumps(result1, indent=2))

    # Example 2: Value Stock
    print("\n--- Example 2: Value Stock ---")
    result2 = engine.analyze_investment(
        asset="VALUE-STOCK-001",
        bullish_factors=[
            "low_valuation",
            "dividend_yield",
            "stable_earnings",
        ],
        bearish_factors=[
            "sector_headwinds",
            "slow_growth",
        ],
        risk_factors=[
            "geopolitical_risk",
        ],
    )
    print(json.dumps(result2, indent=2))

    # Example 3: Emerging Market
    print("\n--- Example 3: Emerging Market Investment ---")
    result3 = engine.analyze_investment(
        asset="EMERGING-MARKET-001",
        bullish_factors=[
            "GDP_growth",
            "demographic_dividend",
            "market_expansion",
        ],
        bearish_factors=[
            "currency_risk",
            "political_instability",
        ],
        risk_factors=[
            "geopolitical_risk",
            "regulatory_risk",
            "sector_concentration",
        ],
    )
    print(json.dumps(result3, indent=2))

    # Show system metrics
    print("\n" + "=" * 70)
    engine.theos.print_metrics()


if __name__ == "__main__":
    run_financial_examples()
