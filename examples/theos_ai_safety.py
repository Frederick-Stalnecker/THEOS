#!/usr/bin/env python3
"""
THEOS AI Safety and Alignment Example
======================================

Demonstrates THEOS dual-engine reasoning for AI safety evaluation with:
- Constructive engine (L): Capability analysis and benefit identification
- Critical engine (R): Risk assessment and alignment verification
- Governor: Halting when safety confidence is sufficient

This example shows how THEOS can improve AI safety by:
1. Analyzing AI system capabilities
2. Critically evaluating alignment risks
3. Measuring productive disagreement about safety
4. Accumulating safety evaluation wisdom

Author: Frederick Davis Stalnecker
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from theos_system import create_numeric_system, TheosConfig
from typing import Dict, List, Any
import json


class AISafetyEvaluator:
    """THEOS-based AI safety evaluation system."""
    
    def __init__(self):
        """Initialize with AI safety knowledge base."""
        # Capability categories
        self.capability_categories = {
            "reasoning": ["planning", "problem_solving", "logic"],
            "language": ["comprehension", "generation", "translation"],
            "perception": ["vision", "audio", "multimodal"],
            "autonomy": ["decision_making", "goal_setting", "self_modification"],
            "learning": ["adaptation", "generalization", "transfer_learning"],
        }
        
        # Alignment risk factors
        self.alignment_risks = {
            "goal_misalignment": 0.4,
            "reward_hacking": 0.35,
            "specification_gaming": 0.3,
            "deceptive_alignment": 0.45,
            "power_seeking": 0.4,
            "value_drift": 0.35,
        }
        
        # Safety mechanisms
        self.safety_mechanisms = {
            "constitutional_ai": 0.3,
            "interpretability": 0.25,
            "oversight": 0.35,
            "red_teaming": 0.2,
            "containment": 0.4,
        }
        
        # Initialize THEOS system
        config = TheosConfig(
            max_cycles=5,
            eps_converge=0.1,
            verbose=False,
        )
        self.theos = create_numeric_system(config)
    
    def evaluate_system(
        self,
        system_name: str,
        capabilities: List[str],
        alignment_measures: List[str],
        risk_factors: List[str],
    ) -> Dict[str, Any]:
        """
        Run THEOS reasoning for AI safety evaluation.
        
        Args:
            system_name: Name of the AI system
            capabilities: List of system capabilities
            alignment_measures: List of alignment/safety measures in place
            risk_factors: List of identified risk factors
            
        Returns:
            Safety evaluation with confidence and recommendation
        """
        # Build query
        query = self._build_query(
            system_name,
            capabilities,
            alignment_measures,
            risk_factors,
        )
        
        # Run THEOS reasoning
        result = self.theos.reason(query)
        
        # Interpret result
        evaluation = self._interpret_result(
            result,
            system_name,
            capabilities,
            alignment_measures,
            risk_factors,
        )
        
        return evaluation
    
    def _build_query(
        self,
        system_name: str,
        capabilities: List[str],
        alignment_measures: List[str],
        risk_factors: List[str],
    ) -> str:
        """Build query string for THEOS."""
        query_parts = [
            f"System: {system_name}",
            f"Capabilities: {', '.join(capabilities)}",
            f"Alignment measures: {', '.join(alignment_measures)}",
            f"Risk factors: {', '.join(risk_factors)}",
        ]
        return " | ".join(query_parts)
    
    def _interpret_result(
        self,
        result,
        system_name: str,
        capabilities: List[str],
        alignment_measures: List[str],
        risk_factors: List[str],
    ) -> Dict[str, Any]:
        """Interpret THEOS result as safety evaluation."""
        # Calculate capability score
        capability_score = len(capabilities) / 5.0  # Normalize to 5 categories
        
        # Calculate alignment score (higher is better)
        alignment_score = len(alignment_measures) / 5.0  # Normalize to 5 mechanisms
        
        # Calculate risk score (higher is worse)
        risk_score = len(risk_factors) / 6.0  # Normalize to 6 possible risks
        
        # Combine with THEOS confidence
        base_confidence = result.confidence
        
        # Safety confidence = base confidence adjusted for alignment and risk
        safety_confidence = (
            0.4 * base_confidence +
            0.3 * alignment_score +
            0.3 * (1.0 - risk_score)
        )
        
        # Generate recommendation
        recommendation = self._get_recommendation(
            safety_confidence,
            capability_score,
            alignment_score,
            risk_score,
        )
        
        return {
            "system": system_name,
            "capabilities": capabilities,
            "alignment_measures": alignment_measures,
            "risk_factors": risk_factors,
            "capability_score": round(capability_score, 3),
            "alignment_score": round(alignment_score, 3),
            "risk_score": round(risk_score, 3),
            "theos_confidence": round(result.confidence, 3),
            "safety_confidence": round(safety_confidence, 3),
            "cycles_used": result.cycles_used,
            "halt_reason": result.halt_reason.value,
            "wisdom_entries": len(self.theos.core.wisdom),
            "recommendation": recommendation,
        }
    
    def _get_recommendation(
        self,
        safety_confidence: float,
        capability_score: float,
        alignment_score: float,
        risk_score: float,
    ) -> str:
        """Get safety recommendation based on evaluation."""
        if safety_confidence > 0.8 and alignment_score > 0.6 and risk_score < 0.3:
            return "APPROVED - High safety confidence with strong alignment measures"
        elif safety_confidence > 0.7 and alignment_score > 0.5 and risk_score < 0.4:
            return "CONDITIONAL - Acceptable safety with recommended monitoring"
        elif safety_confidence > 0.5 and alignment_score > 0.3:
            return "REVIEW - Additional safety measures recommended before deployment"
        elif capability_score > 0.6 and risk_score > 0.5:
            return "RESTRICTED - High capability with significant unmitigated risks"
        else:
            return "BLOCKED - Insufficient alignment measures for capability level"


def run_ai_safety_examples():
    """Run AI safety evaluation examples."""
    evaluator = AISafetyEvaluator()
    
    print("\n" + "=" * 70)
    print("THEOS AI Safety Evaluation System - Examples")
    print("=" * 70)
    
    # Example 1: Moderate Capability System
    print("\n--- Example 1: Moderate Capability System ---")
    result1 = evaluator.evaluate_system(
        system_name="TextGen-v2",
        capabilities=["language_comprehension", "language_generation"],
        alignment_measures=["constitutional_ai", "red_teaming"],
        risk_factors=["goal_misalignment"],
    )
    print(json.dumps(result1, indent=2))
    
    # Example 2: High Capability System
    print("\n--- Example 2: High Capability System ---")
    result2 = evaluator.evaluate_system(
        system_name="ReasoningEngine-v3",
        capabilities=[
            "planning",
            "problem_solving",
            "language_comprehension",
            "language_generation",
            "decision_making",
        ],
        alignment_measures=[
            "constitutional_ai",
            "interpretability",
            "oversight",
            "red_teaming",
        ],
        risk_factors=[
            "goal_misalignment",
            "deceptive_alignment",
            "power_seeking",
        ],
    )
    print(json.dumps(result2, indent=2))
    
    # Example 3: Autonomous System
    print("\n--- Example 3: Autonomous System ---")
    result3 = evaluator.evaluate_system(
        system_name="AutonomousAgent-v1",
        capabilities=[
            "planning",
            "problem_solving",
            "decision_making",
            "self_modification",
            "goal_setting",
        ],
        alignment_measures=[
            "constitutional_ai",
            "containment",
        ],
        risk_factors=[
            "goal_misalignment",
            "reward_hacking",
            "specification_gaming",
            "deceptive_alignment",
            "power_seeking",
            "value_drift",
        ],
    )
    print(json.dumps(result3, indent=2))
    
    # Show system metrics
    print("\n" + "=" * 70)
    evaluator.theos.print_metrics()


if __name__ == "__main__":
    run_ai_safety_examples()
