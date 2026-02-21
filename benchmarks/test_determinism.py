#!/usr/bin/env python3
"""
THEOS Determinism Verification Benchmark

Purpose: Verify that THEOS is truly deterministic by running the same inputs
100 times and checking that outputs are identical.

This is the foundation benchmark. If THEOS isn't deterministic, nothing else matters.

Lab Assistant Mode: Only report what we actually observe.
"""

import sys
sys.path.insert(0, '/home/ubuntu/THEOS_repo/code')

from theos_governor import THEOSGovernor, EngineOutput, GovernorConfig
import json
import hashlib
from typing import List, Dict, Any
import time

# ============================================================================
# TEST DATA - Real, meaningful scenarios
# ============================================================================

TEST_SCENARIOS = [
    {
        "name": "Medical Diagnosis - Simple Case",
        "constructive": EngineOutput(
            reasoning_mode="Constructive",
            output="Patient presents with fever and cough. Likely diagnosis: common cold or mild respiratory infection. Recommend rest, fluids, and monitoring.",
            confidence=0.75,
            internal_monologue="Considering most common causes of fever and cough in otherwise healthy patient"
        ),
        "critical": EngineOutput(
            reasoning_mode="Critical",
            output="Fever and cough could indicate serious conditions: pneumonia, COVID-19, influenza, or other respiratory infections. Requires testing to rule out serious causes.",
            confidence=0.80,
            internal_monologue="Focusing on worst-case scenarios and serious differential diagnoses"
        )
    },
    {
        "name": "Financial Decision - Investment",
        "constructive": EngineOutput(
            reasoning_mode="Constructive",
            output="Emerging market opportunity with 25% projected annual return. Strong growth trajectory, favorable demographics, improving infrastructure.",
            confidence=0.70,
            internal_monologue="Emphasizing upside potential and market growth factors"
        ),
        "critical": EngineOutput(
            reasoning_mode="Critical",
            output="Emerging market carries significant risks: political instability, currency volatility, regulatory uncertainty. Historical volatility 40%+ annually.",
            confidence=0.75,
            internal_monologue="Identifying risks and downside scenarios"
        )
    },
    {
        "name": "AI Safety - Jailbreak Attempt",
        "constructive": EngineOutput(
            reasoning_mode="Constructive",
            output="User is asking for educational information about social engineering. This is legitimate educational content that helps people understand security risks.",
            confidence=0.65,
            internal_monologue="Considering educational value and user autonomy"
        ),
        "critical": EngineOutput(
            reasoning_mode="Critical",
            output="Social engineering techniques could be used to manipulate vulnerable people. Providing detailed techniques could enable harm. Refusal is appropriate.",
            confidence=0.85,
            internal_monologue="Prioritizing safety and protection of vulnerable populations"
        )
    },
    {
        "name": "Legal Analysis - Contract Ambiguity",
        "constructive": EngineOutput(
            reasoning_mode="Constructive",
            output="The ambiguous clause could be interpreted favorably. Standard commercial practice suggests this interpretation. Proceed with contract.",
            confidence=0.68,
            internal_monologue="Focusing on favorable interpretation and business efficiency"
        ),
        "critical": EngineOutput(
            reasoning_mode="Critical",
            output="Ambiguous clause creates legal risk. Adverse interpretation could result in significant financial exposure. Requires legal review and clarification.",
            confidence=0.80,
            internal_monologue="Identifying legal risks and worst-case interpretations"
        )
    },
    {
        "name": "Edge Case - Very Similar Outputs",
        "constructive": EngineOutput(
            reasoning_mode="Constructive",
            output="The analysis suggests proceeding with the proposed action. The evidence is reasonably strong.",
            confidence=0.72,
            internal_monologue="Supporting the proposal"
        ),
        "critical": EngineOutput(
            reasoning_mode="Critical",
            output="The analysis suggests proceeding with the proposed action. The evidence is reasonably strong.",
            confidence=0.72,
            internal_monologue="Supporting the proposal"
        )
    }
]

# ============================================================================
# DETERMINISM VERIFICATION FUNCTIONS
# ============================================================================

def hash_output(output: Dict[str, Any]) -> str:
    """Create hash of output for comparison."""
    # Convert to JSON string with sorted keys for consistent hashing
    json_str = json.dumps(output, sort_keys=True, default=str)
    return hashlib.sha256(json_str.encode()).hexdigest()

def run_single_test(governor: THEOSGovernor, scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Run a single test and return the result."""
    left = scenario["constructive"]
    right = scenario["critical"]
    
    # Evaluate cycle 1
    eval1 = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
    
    # Evaluate cycle 2
    eval2 = governor.evaluate_cycle(left, right, current_budget=eval1.remaining_budget, cycle_number=2)
    
    # Evaluate cycle 3
    eval3 = governor.evaluate_cycle(left, right, current_budget=eval2.remaining_budget, cycle_number=3)
    
    # Get audit trail
    audit = governor.get_audit_trail()
    
    return {
        "cycle_1": {
            "similarity": eval1.similarity_score,
            "risk": eval1.risk_score,
            "quality": eval1.composite_quality,
            "decision": eval1.decision,
            "stop_reason": str(eval1.stop_reason) if eval1.stop_reason else None,
            "budget_remaining": eval1.remaining_budget
        },
        "cycle_2": {
            "similarity": eval2.similarity_score,
            "risk": eval2.risk_score,
            "quality": eval2.composite_quality,
            "decision": eval2.decision,
            "stop_reason": str(eval2.stop_reason) if eval2.stop_reason else None,
            "budget_remaining": eval2.remaining_budget
        },
        "cycle_3": {
            "similarity": eval3.similarity_score,
            "risk": eval3.risk_score,
            "quality": eval3.composite_quality,
            "decision": eval3.decision,
            "stop_reason": str(eval3.stop_reason) if eval3.stop_reason else None,
            "budget_remaining": eval3.remaining_budget
        },
        "audit_total_cycles": audit.get("total_cycles", 0) if audit else 0,
        "audit_final_similarity": audit.get("final_similarity", 0) if audit else 0,
        "audit_final_risk": audit.get("final_risk", 0) if audit else 0
    }

def run_determinism_test(scenario: Dict[str, Any], num_runs: int = 100) -> Dict[str, Any]:
    """Run the same scenario multiple times and verify determinism."""
    
    print(f"\n{'='*70}")
    print(f"Testing Determinism: {scenario['name']}")
    print(f"{'='*70}")
    print(f"Running {num_runs} identical iterations...")
    
    results = []
    hashes = []
    
    for i in range(num_runs):
        # Create fresh Governor for each run
        config = GovernorConfig()
        governor = THEOSGovernor(config=config)
        
        # Run test
        result = run_single_test(governor, scenario)
        results.append(result)
        
        # Hash the result
        result_hash = hash_output(result)
        hashes.append(result_hash)
        
        if (i + 1) % 25 == 0:
            print(f"  Completed {i + 1}/{num_runs} runs...")
    
    # Analyze results
    unique_hashes = set(hashes)
    hash_counts = {}
    for h in hashes:
        hash_counts[h] = hash_counts.get(h, 0) + 1
    
    is_deterministic = len(unique_hashes) == 1
    
    # Report findings
    print(f"\nResults:")
    print(f"  Total runs: {num_runs}")
    print(f"  Unique outputs: {len(unique_hashes)}")
    print(f"  Deterministic: {'✅ YES' if is_deterministic else '❌ NO'}")
    
    if not is_deterministic:
        print(f"\n  Hash distribution:")
        for h, count in sorted(hash_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"    {h[:16]}...: {count} runs ({100*count/num_runs:.1f}%)")
        
        # Show first example of each unique output
        print(f"\n  Example outputs:")
        shown_hashes = set()
        for i, result in enumerate(results):
            result_hash = hashes[i]
            if result_hash not in shown_hashes:
                print(f"\n    Hash {result_hash[:16]}... (from run {i+1}):")
                print(f"      Cycle 1 similarity: {result['cycle_1']['similarity']:.6f}")
                print(f"      Cycle 1 risk: {result['cycle_1']['risk']:.6f}")
                print(f"      Cycle 1 quality: {result['cycle_1']['quality']:.6f}")
                shown_hashes.add(result_hash)
    else:
        print(f"\n  ✅ All {num_runs} runs produced identical outputs")
        print(f"  First run cycle 1 similarity: {results[0]['cycle_1']['similarity']:.6f}")
        print(f"  First run cycle 1 risk: {results[0]['cycle_1']['risk']:.6f}")
        print(f"  First run cycle 1 quality: {results[0]['cycle_1']['quality']:.6f}")
    
    return {
        "scenario": scenario["name"],
        "num_runs": num_runs,
        "unique_outputs": len(unique_hashes),
        "is_deterministic": is_deterministic,
        "sample_output": results[0],
        "all_hashes_identical": len(unique_hashes) == 1,
        "hash_distribution": hash_counts
    }

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    """Run complete determinism verification."""
    
    print("\n" + "="*70)
    print("THEOS DETERMINISM VERIFICATION BENCHMARK")
    print("="*70)
    print("\nPurpose: Verify that THEOS produces identical outputs for identical inputs")
    print("Method: Run each scenario 100 times, compare outputs")
    print("Success Criteria: All 100 runs produce identical results")
    
    all_results = []
    all_deterministic = True
    
    # Run tests for each scenario
    for scenario in TEST_SCENARIOS:
        result = run_determinism_test(scenario, num_runs=100)
        all_results.append(result)
        
        if not result["is_deterministic"]:
            all_deterministic = False
    
    # Summary Report
    print(f"\n{'='*70}")
    print("DETERMINISM VERIFICATION SUMMARY")
    print(f"{'='*70}")
    
    for result in all_results:
        status = "✅ PASS" if result["is_deterministic"] else "❌ FAIL"
        print(f"{status} - {result['scenario']}")
        print(f"     Unique outputs: {result['unique_outputs']}/100")
    
    print(f"\n{'='*70}")
    if all_deterministic:
        print("✅ OVERALL RESULT: THEOS IS DETERMINISTIC")
        print("   All 5 scenarios passed determinism verification")
        print("   All 500 total runs (5 scenarios × 100 runs) produced identical outputs")
    else:
        print("❌ OVERALL RESULT: THEOS IS NOT FULLY DETERMINISTIC")
        print("   Some scenarios produced different outputs on different runs")
        print("   This must be investigated and fixed")
    print(f"{'='*70}\n")
    
    # Save detailed results
    with open('/home/ubuntu/THEOS_repo/benchmarks/determinism_results.json', 'w') as f:
        json.dump({
            "test_name": "Determinism Verification",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "overall_deterministic": all_deterministic,
            "scenarios_tested": len(TEST_SCENARIOS),
            "runs_per_scenario": 100,
            "total_runs": len(TEST_SCENARIOS) * 100,
            "results": all_results
        }, f, indent=2, default=str)
    
    print("Detailed results saved to: benchmarks/determinism_results.json")
    
    return 0 if all_deterministic else 1

if __name__ == "__main__":
    sys.exit(main())
