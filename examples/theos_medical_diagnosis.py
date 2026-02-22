#!/usr/bin/env python3
"""
THEOS Medical Diagnosis Example
================================

Demonstrates THEOS dual-engine reasoning for medical diagnosis with:
- Constructive engine (L): Hypothesis generation from positive evidence
- Critical engine (R): Risk assessment and contraindication checking
- Governor: Halting when confidence is sufficient

This example shows how THEOS can improve diagnostic accuracy by:
1. Generating multiple hypotheses
2. Critically evaluating each
3. Measuring productive disagreement
4. Accumulating diagnostic wisdom

Author: Frederick Davis Stalnecker
"""

import sys
sys.path.insert(0, '/home/ubuntu/THEOS_repo/code')

from theos_system import create_numeric_system, TheosConfig
from typing import Dict, List, Any
import json


class MedicalDiagnosisEngine:
    """THEOS-based medical diagnosis system."""
    
    def __init__(self):
        """Initialize with medical knowledge base."""
        # Symptom to condition mappings
        self.symptom_conditions = {
            "chest_pain": ["MI", "angina", "GERD", "anxiety"],
            "shortness_of_breath": ["MI", "PE", "pneumonia", "asthma"],
            "fever": ["infection", "inflammation", "malignancy"],
            "headache": ["migraine", "tension", "meningitis", "stroke"],
            "fatigue": ["anemia", "depression", "thyroid", "infection"],
        }
        
        # Risk factors
        self.risk_factors = {
            "age_over_60": 0.3,
            "smoking": 0.4,
            "diabetes": 0.35,
            "hypertension": 0.3,
            "family_history": 0.25,
        }
        
        # Contraindications (conditions that rule out diagnoses)
        self.contraindications = {
            "MI": {"EKG": "normal", "troponin": "normal"},
            "PE": {"D_dimer": "normal", "CXR": "normal"},
            "meningitis": {"CSF": "normal", "head_CT": "normal"},
        }
        
        # Initialize THEOS system
        config = TheosConfig(
            max_cycles=5,
            eps_converge=0.1,
            verbose=False,
        )
        self.theos = create_numeric_system(config)
    
    def diagnose(
        self,
        symptoms: List[str],
        risk_factors: List[str],
        test_results: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Run THEOS reasoning for medical diagnosis.
        
        Args:
            symptoms: List of reported symptoms
            risk_factors: List of patient risk factors
            test_results: Dict of test results
            
        Returns:
            Diagnosis result with confidence and reasoning
        """
        # Build query
        query = self._build_query(symptoms, risk_factors, test_results)
        
        # Run THEOS reasoning
        result = self.theos.reason(query)
        
        # Interpret result
        diagnosis = self._interpret_result(
            result,
            symptoms,
            risk_factors,
            test_results,
        )
        
        return diagnosis
    
    def _build_query(
        self,
        symptoms: List[str],
        risk_factors: List[str],
        test_results: Dict[str, str],
    ) -> str:
        """Build query string for THEOS."""
        query_parts = [
            f"Symptoms: {', '.join(symptoms)}",
            f"Risk factors: {', '.join(risk_factors)}",
            f"Test results: {', '.join(f'{k}={v}' for k, v in test_results.items())}",
        ]
        return " | ".join(query_parts)
    
    def _interpret_result(
        self,
        result,
        symptoms: List[str],
        risk_factors: List[str],
        test_results: Dict[str, str],
    ) -> Dict[str, Any]:
        """Interpret THEOS result as medical diagnosis."""
        # Generate differential diagnosis
        differential = []
        for symptom in symptoms:
            if symptom in self.symptom_conditions:
                differential.extend(self.symptom_conditions[symptom])
        
        # Remove duplicates and sort by frequency
        differential = list(set(differential))
        differential.sort(key=lambda x: differential.count(x), reverse=True)
        
        # Calculate confidence based on THEOS result
        base_confidence = result.confidence
        
        # Adjust for test results
        test_confidence = 1.0
        for condition in differential[:3]:  # Top 3 diagnoses
            if condition in self.contraindications:
                for test, contraindication in self.contraindications[condition].items():
                    if test in test_results and test_results[test] == contraindication:
                        test_confidence *= 0.5  # Reduce confidence if contraindicated
        
        final_confidence = base_confidence * test_confidence
        
        return {
            "differential_diagnosis": differential[:5],
            "primary_diagnosis": differential[0] if differential else "Unknown",
            "theos_confidence": result.confidence,
            "test_adjusted_confidence": final_confidence,
            "cycles_used": result.cycles_used,
            "halt_reason": result.halt_reason.value,
            "wisdom_entries": len(self.theos.core.wisdom),
            "recommendation": self._get_recommendation(final_confidence, differential[0] if differential else "Unknown"),
        }
    
    def _get_recommendation(self, confidence: float, diagnosis: str) -> str:
        """Get clinical recommendation based on confidence."""
        if confidence > 0.8:
            return f"High confidence in {diagnosis}. Proceed with treatment."
        elif confidence > 0.6:
            return f"Moderate confidence in {diagnosis}. Consider confirmatory tests."
        elif confidence > 0.4:
            return f"Low confidence in {diagnosis}. Recommend specialist consultation."
        else:
            return "Insufficient confidence. Recommend comprehensive evaluation."


def run_medical_examples():
    """Run medical diagnosis examples."""
    engine = MedicalDiagnosisEngine()
    
    print("\n" + "=" * 70)
    print("THEOS Medical Diagnosis System - Examples")
    print("=" * 70)
    
    # Example 1: Acute Coronary Syndrome
    print("\n--- Example 1: Acute Coronary Syndrome ---")
    result1 = engine.diagnose(
        symptoms=["chest_pain", "shortness_of_breath"],
        risk_factors=["age_over_60", "smoking", "hypertension"],
        test_results={
            "EKG": "ST_elevation",
            "troponin": "elevated",
            "CXR": "normal",
        },
    )
    print(json.dumps(result1, indent=2))
    
    # Example 2: Pulmonary Embolism
    print("\n--- Example 2: Pulmonary Embolism ---")
    result2 = engine.diagnose(
        symptoms=["shortness_of_breath", "chest_pain"],
        risk_factors=["age_over_60"],
        test_results={
            "D_dimer": "elevated",
            "CXR": "normal",
            "EKG": "normal",
        },
    )
    print(json.dumps(result2, indent=2))
    
    # Example 3: Infection/Fever
    print("\n--- Example 3: Systemic Infection ---")
    result3 = engine.diagnose(
        symptoms=["fever", "fatigue", "headache"],
        risk_factors=["diabetes"],
        test_results={
            "WBC": "elevated",
            "CRP": "elevated",
            "blood_culture": "pending",
        },
    )
    print(json.dumps(result3, indent=2))
    
    # Show system metrics
    print("\n" + "=" * 70)
    engine.theos.print_metrics()


if __name__ == "__main__":
    run_medical_examples()
