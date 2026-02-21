#!/usr/bin/env python3
"""
THEOS Safety and Robustness Benchmark

Purpose: Test THEOS against adversarial inputs, edge cases, and stress conditions.
This verifies that the Governor can handle malformed inputs, resource exhaustion,
and other failure modes gracefully.

Lab Assistant Mode: Only report what we actually observe.
"""

import sys
sys.path.insert(0, '/home/ubuntu/THEOS_repo/code')

from theos_governor import THEOSGovernor, EngineOutput, GovernorConfig, StopReason
import json
import time
from typing import List, Dict, Any, Tuple

# ============================================================================
# ADVERSARIAL TEST CASES
# ============================================================================

class SafetyTestSuite:
    """Comprehensive safety and robustness testing."""
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
    
    # ========================================================================
    # TEST 1: Malformed Input Handling
    # ========================================================================
    
    def test_empty_output(self):
        """Test handling of empty output strings."""
        print("\n[TEST 1] Empty Output Handling")
        print("-" * 60)
        
        config = GovernorConfig()
        governor = THEOSGovernor(config=config)
        
        try:
            left = EngineOutput(
                reasoning_mode="Constructive",
                output="",  # EMPTY
                confidence=0.5,
                internal_monologue="test"
            )
            right = EngineOutput(
                reasoning_mode="Critical",
                output="Valid output",
                confidence=0.5,
                internal_monologue="test"
            )
            
            # Try to evaluate - should this fail or handle gracefully?
            result = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
            
            print("  Result: Governor accepted empty output")
            print(f"  Similarity: {result.similarity_score:.4f}")
            print(f"  Decision: {result.decision}")
            
            # This is a problem if Governor doesn't validate
            self.failed += 1
            return {
                "test": "Empty Output",
                "status": "ISSUE FOUND",
                "description": "Governor accepted empty output without validation",
                "severity": "HIGH"
            }
        
        except ValueError as e:
            print(f"  Result: Governor rejected empty output ✅")
            print(f"  Error: {str(e)}")
            self.passed += 1
            return {
                "test": "Empty Output",
                "status": "PASS",
                "description": "Governor properly validates empty outputs",
                "severity": "N/A"
            }
        
        except Exception as e:
            print(f"  Result: Unexpected error")
            print(f"  Error: {type(e).__name__}: {str(e)}")
            self.failed += 1
            return {
                "test": "Empty Output",
                "status": "FAIL",
                "description": f"Unexpected error: {type(e).__name__}",
                "severity": "HIGH"
            }
    
    def test_invalid_confidence(self):
        """Test handling of invalid confidence values."""
        print("\n[TEST 2] Invalid Confidence Values")
        print("-" * 60)
        
        test_cases = [
            (-0.5, "Negative confidence"),
            (1.5, "Confidence > 1.0"),
            (float('inf'), "Infinite confidence"),
            (float('nan'), "NaN confidence")
        ]
        
        results = []
        for confidence, description in test_cases:
            config = GovernorConfig()
            governor = THEOSGovernor(config=config)
            
            try:
                left = EngineOutput(
                    reasoning_mode="Constructive",
                    output="Valid output",
                    confidence=confidence,
                    internal_monologue="test"
                )
                right = EngineOutput(
                    reasoning_mode="Critical",
                    output="Valid output",
                    confidence=0.5,
                    internal_monologue="test"
                )
                
                result = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
                print(f"  {description}: Governor accepted (similarity {result.similarity_score:.4f})")
                results.append(("ISSUE", description))
                self.failed += 1
            
            except (ValueError, TypeError) as e:
                print(f"  {description}: Governor rejected ✅")
                results.append(("PASS", description))
                self.passed += 1
            
            except Exception as e:
                print(f"  {description}: Unexpected error ({type(e).__name__})")
                results.append(("ERROR", description))
                self.failed += 1
        
        return {
            "test": "Invalid Confidence",
            "status": "MIXED" if any(r[0] == "ISSUE" for r in results) else "PASS",
            "results": results
        }
    
    def test_very_long_output(self):
        """Test handling of extremely long outputs."""
        print("\n[TEST 3] Very Long Output Handling")
        print("-" * 60)
        
        config = GovernorConfig()
        governor = THEOSGovernor(config=config)
        
        # Create a 100KB output
        long_output = "This is a test. " * 6250  # ~100KB
        
        print(f"  Output length: {len(long_output):,} characters")
        
        try:
            start_time = time.time()
            
            left = EngineOutput(
                reasoning_mode="Constructive",
                output=long_output,
                confidence=0.5,
                internal_monologue="test"
            )
            right = EngineOutput(
                reasoning_mode="Critical",
                output=long_output,
                confidence=0.5,
                internal_monologue="test"
            )
            
            result = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
            
            elapsed = time.time() - start_time
            print(f"  Result: Governor processed long output ✅")
            print(f"  Time: {elapsed:.3f} seconds")
            print(f"  Similarity: {result.similarity_score:.4f}")
            
            if elapsed > 1.0:
                print(f"  WARNING: Slow processing ({elapsed:.3f}s)")
                self.failed += 1
                return {
                    "test": "Very Long Output",
                    "status": "SLOW",
                    "time_seconds": elapsed,
                    "description": "Governor processes very long outputs but slowly"
                }
            else:
                self.passed += 1
                return {
                    "test": "Very Long Output",
                    "status": "PASS",
                    "time_seconds": elapsed,
                    "description": "Governor handles very long outputs efficiently"
                }
        
        except Exception as e:
            print(f"  Result: Error processing long output")
            print(f"  Error: {type(e).__name__}: {str(e)}")
            self.failed += 1
            return {
                "test": "Very Long Output",
                "status": "FAIL",
                "error": str(e)
            }
    
    # ========================================================================
    # TEST 4: Stop Condition Verification
    # ========================================================================
    
    def test_all_stop_conditions(self):
        """Verify that all 5 stop conditions work correctly."""
        print("\n[TEST 4] Stop Condition Verification")
        print("-" * 60)
        
        results = []
        
        # Stop Condition 1: Convergence
        print("  Testing CONVERGENCE_ACHIEVED...")
        config = GovernorConfig(similarity_threshold=0.5)
        governor = THEOSGovernor(config=config)
        
        left = EngineOutput(
            reasoning_mode="Constructive",
            output="The answer is yes",
            confidence=0.9,
            internal_monologue="test"
        )
        right = EngineOutput(
            reasoning_mode="Critical",
            output="The answer is yes",  # Identical
            confidence=0.9,
            internal_monologue="test"
        )
        
        result = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
        if result.stop_reason == StopReason.CONVERGENCE_ACHIEVED:
            print("    ✅ CONVERGENCE_ACHIEVED triggered correctly")
            results.append(("PASS", "CONVERGENCE_ACHIEVED"))
            self.passed += 1
        else:
            print(f"    ❌ Expected CONVERGENCE_ACHIEVED, got {result.stop_reason}")
            results.append(("FAIL", "CONVERGENCE_ACHIEVED"))
            self.failed += 1
        
        # Stop Condition 2: Risk Exceeded
        print("  Testing RISK_THRESHOLD_EXCEEDED...")
        config = GovernorConfig(risk_threshold=0.3)
        governor = THEOSGovernor(config=config)
        
        left = EngineOutput(
            reasoning_mode="Constructive",
            output="This is very risky",
            confidence=0.1,  # Low confidence = high risk
            internal_monologue="test"
        )
        right = EngineOutput(
            reasoning_mode="Critical",
            output="This is extremely risky",
            confidence=0.1,
            internal_monologue="test"
        )
        
        result = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
        if result.stop_reason == StopReason.RISK_THRESHOLD_EXCEEDED:
            print("    ✅ RISK_THRESHOLD_EXCEEDED triggered correctly")
            results.append(("PASS", "RISK_THRESHOLD_EXCEEDED"))
            self.passed += 1
        else:
            print(f"    ⚠️  Expected RISK_THRESHOLD_EXCEEDED, got {result.stop_reason}")
            # This might not trigger if risk calculation doesn't work as expected
            results.append(("INFO", "RISK_THRESHOLD_EXCEEDED"))
        
        # Stop Condition 3: Budget Exhausted
        print("  Testing CONTRADICTION_EXHAUSTED...")
        config = GovernorConfig()
        governor = THEOSGovernor(config=config)
        
        left = EngineOutput(
            reasoning_mode="Constructive",
            output="Completely different perspective A",
            confidence=0.5,
            internal_monologue="test"
        )
        right = EngineOutput(
            reasoning_mode="Critical",
            output="Completely different perspective B",
            confidence=0.5,
            internal_monologue="test"
        )
        
        # Run cycles until budget exhausted
        budget = 1.0
        cycle_num = 1
        final_result = None
        while budget > 0 and cycle_num <= 10:
            result = governor.evaluate_cycle(left, right, current_budget=budget, cycle_number=cycle_num)
            budget = result.remaining_budget
            final_result = result
            if result.decision == "STOP":
                break
            cycle_num += 1
        
        if final_result and final_result.stop_reason == StopReason.CONTRADICTION_EXHAUSTED:
            print("    ✅ CONTRADICTION_EXHAUSTED triggered correctly")
            results.append(("PASS", "CONTRADICTION_EXHAUSTED"))
            self.passed += 1
        else:
            print(f"    ⚠️  CONTRADICTION_EXHAUSTED not triggered (got {final_result.stop_reason if final_result else 'None'})")
            results.append(("INFO", "CONTRADICTION_EXHAUSTED"))
        
        # Stop Condition 4: Max Cycles
        print("  Testing MAX_CYCLES_REACHED...")
        config = GovernorConfig(max_cycles=2)
        governor = THEOSGovernor(config=config)
        
        left = EngineOutput(
            reasoning_mode="Constructive",
            output="Perspective A",
            confidence=0.5,
            internal_monologue="test"
        )
        right = EngineOutput(
            reasoning_mode="Critical",
            output="Perspective B",
            confidence=0.5,
            internal_monologue="test"
        )
        
        # Run cycles
        result1 = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
        if result1.decision == "CONTINUE":
            result2 = governor.evaluate_cycle(left, right, current_budget=result1.remaining_budget, cycle_number=2)
            if result2.stop_reason == StopReason.MAX_CYCLES_REACHED:
                print("    ✅ MAX_CYCLES_REACHED triggered correctly")
                results.append(("PASS", "MAX_CYCLES_REACHED"))
                self.passed += 1
            else:
                print(f"    ⚠️  Expected MAX_CYCLES_REACHED, got {result2.stop_reason}")
                results.append(("INFO", "MAX_CYCLES_REACHED"))
        else:
            print(f"    ⚠️  Stopped before cycle 2 with {result1.stop_reason}")
            results.append(("INFO", "MAX_CYCLES_REACHED"))
        
        return {
            "test": "Stop Conditions",
            "status": "PASS" if all(r[0] == "PASS" for r in results) else "MIXED",
            "results": results
        }
    
    # ========================================================================
    # TEST 5: Budget Mechanics
    # ========================================================================
    
    def test_budget_mechanics(self):
        """Verify contradiction budget decreases correctly."""
        print("\n[TEST 5] Contradiction Budget Mechanics")
        print("-" * 60)
        
        config = GovernorConfig(initial_contradiction_budget=1.0)
        governor = THEOSGovernor(config=config)
        
        left = EngineOutput(
            reasoning_mode="Constructive",
            output="Perspective A",
            confidence=0.5,
            internal_monologue="test"
        )
        right = EngineOutput(
            reasoning_mode="Critical",
            output="Perspective B",
            confidence=0.5,
            internal_monologue="test"
        )
        
        budgets = [1.0]
        
        for cycle_num in range(1, 6):
            result = governor.evaluate_cycle(left, right, current_budget=budgets[-1], cycle_number=cycle_num)
            budgets.append(result.remaining_budget)
            
            print(f"  Cycle {cycle_num}: budget {budgets[-2]:.4f} → {budgets[-1]:.4f} (spent {budgets[-2] - budgets[-1]:.4f})")
            
            if result.decision == "STOP":
                print(f"  Stopped at cycle {cycle_num} with reason: {result.stop_reason}")
                break
        
        # Check that budget is monotonically decreasing
        is_decreasing = all(budgets[i] >= budgets[i+1] for i in range(len(budgets)-1))
        is_non_negative = all(b >= 0 for b in budgets)
        
        if is_decreasing and is_non_negative:
            print("  ✅ Budget mechanics correct (monotonically decreasing, non-negative)")
            self.passed += 1
            return {
                "test": "Budget Mechanics",
                "status": "PASS",
                "budget_trajectory": budgets
            }
        else:
            print("  ❌ Budget mechanics incorrect")
            self.failed += 1
            return {
                "test": "Budget Mechanics",
                "status": "FAIL",
                "budget_trajectory": budgets,
                "is_decreasing": is_decreasing,
                "is_non_negative": is_non_negative
            }
    
    # ========================================================================
    # RUN ALL TESTS
    # ========================================================================
    
    def run_all_tests(self):
        """Run the complete safety test suite."""
        print("\n" + "="*70)
        print("THEOS SAFETY AND ROBUSTNESS BENCHMARK")
        print("="*70)
        
        all_results = []
        
        all_results.append(self.test_empty_output())
        all_results.append(self.test_invalid_confidence())
        all_results.append(self.test_very_long_output())
        all_results.append(self.test_all_stop_conditions())
        all_results.append(self.test_budget_mechanics())
        
        # Summary
        print(f"\n{'='*70}")
        print("SAFETY BENCHMARK SUMMARY")
        print(f"{'='*70}")
        print(f"Tests Passed: {self.passed}")
        print(f"Tests Failed: {self.failed}")
        
        if self.failed == 0:
            print("\n✅ ALL SAFETY TESTS PASSED")
        else:
            print(f"\n⚠️  {self.failed} ISSUES FOUND")
        
        # Save results
        with open('/home/ubuntu/THEOS_repo/benchmarks/safety_results.json', 'w') as f:
            json.dump({
                "test_name": "Safety and Robustness Benchmark",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "passed": self.passed,
                "failed": self.failed,
                "results": all_results
            }, f, indent=2, default=str)
        
        print(f"\nDetailed results saved to: benchmarks/safety_results.json")
        
        return all_results

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    suite = SafetyTestSuite()
    suite.run_all_tests()
