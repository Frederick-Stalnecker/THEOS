#!/usr/bin/env python3
"""
THEOS Implementation Test Suite
================================

Comprehensive tests for THEOS core, system integration, and examples.

Tests verify:
- Core reasoning engine functionality
- Governor control mechanisms
- Wisdom accumulation and retrieval
- System metrics tracking
- Example domains (medical, financial, AI safety)

Author: Frederick Davis Stalnecker
"""

import unittest  # sys.path injected by root conftest.py

from theos_ai_safety import AISafetyEvaluator
from theos_core import HaltReason, TheosConfig, TheosCore
from theos_financial_analysis import FinancialAnalysisEngine
from theos_medical_diagnosis import MedicalDiagnosisEngine
from theos_system import TheosSystem, create_numeric_system


class TestTheosCore(unittest.TestCase):
    """Test THEOS core reasoning engine."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = TheosConfig(max_cycles=5, eps_converge=0.1, verbose=False)

    def test_core_initialization(self):
        """Test that TheosCore initializes correctly."""
        system = create_numeric_system(self.config)
        self.assertIsNotNone(system.core)
        self.assertEqual(system.core.config.max_cycles, 5)

    def test_single_query(self):
        """Test single query reasoning."""
        system = create_numeric_system(self.config)
        result = system.reason("Test query")

        self.assertIsNotNone(result)
        self.assertGreater(result.confidence, 0.0)
        self.assertLess(result.confidence, 1.0)
        self.assertGreater(result.cycles_used, 0)
        self.assertLessEqual(result.cycles_used, self.config.max_cycles)

    def test_multiple_queries(self):
        """Test multiple queries with wisdom accumulation."""
        system = create_numeric_system(self.config)

        # First query
        result1 = system.reason("Query A")
        wisdom_after_1 = len(system.core.wisdom)

        # Second query (same)
        result2 = system.reason("Query A")
        wisdom_after_2 = len(system.core.wisdom)

        # Third query (different)
        system.reason("Query B")
        wisdom_after_3 = len(system.core.wisdom)

        # Verify wisdom accumulation
        self.assertEqual(wisdom_after_1, 1)
        self.assertEqual(wisdom_after_2, 2)  # Wisdom reuse
        self.assertEqual(wisdom_after_3, 3)

        # Verify confidence improvement on repeat query
        self.assertGreater(result2.confidence, result1.confidence)

    def test_halt_reasons(self):
        """Test that halt reasons are properly tracked."""
        system = create_numeric_system(self.config)
        result = system.reason("Test query")

        self.assertIsNotNone(result.halt_reason)
        self.assertIn(
            result.halt_reason,
            [HaltReason.CONVERGENCE, HaltReason.DIMINISHING_RETURNS, HaltReason.MAX_CYCLES],
        )

    def test_metrics_tracking(self):
        """Test that metrics are properly tracked."""
        system = create_numeric_system(self.config)

        # Run queries
        for i in range(3):
            system.reason(f"Query {i}")

        metrics = system.get_metrics()
        self.assertEqual(metrics.total_queries, 3)
        self.assertGreater(metrics.total_cycles, 0)
        self.assertGreater(metrics.avg_cycles_per_query, 0)
        self.assertGreater(metrics.avg_confidence, 0)


class TestTheosSystem(unittest.TestCase):
    """Test THEOS unified system."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = TheosConfig(max_cycles=5, eps_converge=0.1, verbose=False)
        self.system = create_numeric_system(self.config)

    def test_system_initialization(self):
        """Test system initialization."""
        self.assertIsNotNone(self.system)
        self.assertIsNotNone(self.system.core)
        self.assertIsNotNone(self.system.metrics)

    def test_query_history(self):
        """Test query history tracking."""
        self.system.reason("Query 1")
        self.system.reason("Query 2")

        history = self.system.get_query_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["query"], "Query 1")
        self.assertEqual(history[1]["query"], "Query 2")

    def test_wisdom_export(self):
        """Test wisdom export functionality."""
        self.system.reason("Test query")

        wisdom = self.system.get_wisdom()
        self.assertIsNotNone(wisdom)
        self.assertGreater(len(wisdom), 0)

    def test_metrics_export(self):
        """Test metrics export to JSON."""
        self.system.reason("Query 1")
        self.system.reason("Query 2")

        metrics_json = self.system.export_metrics()
        self.assertIsNotNone(metrics_json)
        self.assertIn("total_queries", metrics_json)
        self.assertIn("2", metrics_json)  # Should show 2 queries

    def test_history_export(self):
        """Test history export to JSON."""
        self.system.reason("Query 1")

        history_json = self.system.export_history()
        self.assertIsNotNone(history_json)
        self.assertIn("Query 1", history_json)


class TestMedicalDiagnosis(unittest.TestCase):
    """Test medical diagnosis example."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = MedicalDiagnosisEngine()

    def test_engine_initialization(self):
        """Test engine initialization."""
        self.assertIsNotNone(self.engine)
        self.assertIsNotNone(self.engine.theos)

    def test_diagnosis_analysis(self):
        """Test diagnosis analysis."""
        result = self.engine.diagnose(
            symptoms=["chest_pain", "shortness_of_breath"],
            risk_factors=["age_over_60"],
            test_results={"EKG": "normal"},
        )

        self.assertIsNotNone(result)
        self.assertIn("differential_diagnosis", result)
        self.assertIn("primary_diagnosis", result)
        self.assertIn("theos_confidence", result)
        self.assertGreater(len(result["differential_diagnosis"]), 0)

    def test_recommendation_generation(self):
        """Test recommendation generation."""
        result = self.engine.diagnose(
            symptoms=["fever"],
            risk_factors=[],
            test_results={"WBC": "elevated"},
        )

        self.assertIn("recommendation", result)
        self.assertIsNotNone(result["recommendation"])
        self.assertGreater(len(result["recommendation"]), 0)


class TestFinancialAnalysis(unittest.TestCase):
    """Test financial analysis example."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = FinancialAnalysisEngine()

    def test_engine_initialization(self):
        """Test engine initialization."""
        self.assertIsNotNone(self.engine)
        self.assertIsNotNone(self.engine.theos)

    def test_investment_analysis(self):
        """Test investment analysis."""
        result = self.engine.analyze_investment(
            asset="TEST-STOCK",
            bullish_factors=["earnings_growth"],
            bearish_factors=["high_valuation"],
            risk_factors=["execution_risk"],
        )

        self.assertIsNotNone(result)
        self.assertIn("asset", result)
        self.assertIn("adjusted_confidence", result)
        self.assertIn("recommendation", result)

    def test_recommendation_types(self):
        """Test that recommendations are one of expected types."""
        result = self.engine.analyze_investment(
            asset="TEST",
            bullish_factors=["earnings_growth"],
            bearish_factors=[],
            risk_factors=[],
        )

        recommendation = result["recommendation"]
        valid_recommendations = [
            "STRONG BUY",
            "BUY",
            "HOLD",
            "SELL",
            "WAIT",
        ]
        self.assertTrue(any(r in recommendation for r in valid_recommendations))


class TestAISafety(unittest.TestCase):
    """Test AI safety evaluation example."""

    def setUp(self):
        """Set up test fixtures."""
        self.evaluator = AISafetyEvaluator()

    def test_evaluator_initialization(self):
        """Test evaluator initialization."""
        self.assertIsNotNone(self.evaluator)
        self.assertIsNotNone(self.evaluator.theos)

    def test_system_evaluation(self):
        """Test system evaluation."""
        result = self.evaluator.evaluate_system(
            system_name="TEST-SYSTEM",
            capabilities=["reasoning", "planning"],
            alignment_measures=["constitutional_ai"],
            risk_factors=["goal_misalignment"],
        )

        self.assertIsNotNone(result)
        self.assertIn("system", result)
        self.assertIn("safety_confidence", result)
        self.assertIn("recommendation", result)

    def test_recommendation_types(self):
        """Test that recommendations are one of expected types."""
        result = self.evaluator.evaluate_system(
            system_name="TEST",
            capabilities=["reasoning"],
            alignment_measures=["constitutional_ai"],
            risk_factors=[],
        )

        recommendation = result["recommendation"]
        valid_recommendations = [
            "APPROVED",
            "CONDITIONAL",
            "REVIEW",
            "RESTRICTED",
            "BLOCKED",
        ]
        self.assertTrue(any(r in recommendation for r in valid_recommendations))


class TestIntegration(unittest.TestCase):
    """Integration tests across all components."""

    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # Create system
        config = TheosConfig(max_cycles=5, eps_converge=0.1, verbose=False)
        system = create_numeric_system(config)

        # Run multiple queries
        queries = ["Query A", "Query A", "Query B", "Query C"]
        for q in queries:
            system.reason(q)

        # Verify results
        metrics = system.get_metrics()
        self.assertEqual(metrics.total_queries, 4)

        history = system.get_query_history()
        self.assertEqual(len(history), 4)

        wisdom = system.get_wisdom()
        self.assertGreater(len(wisdom), 0)

    def test_domain_examples_work(self):
        """Test that all domain examples work without errors."""
        # Medical
        med_engine = MedicalDiagnosisEngine()
        med_result = med_engine.diagnose(
            symptoms=["fever"],
            risk_factors=[],
            test_results={},
        )
        self.assertIsNotNone(med_result)

        # Financial
        fin_engine = FinancialAnalysisEngine()
        fin_result = fin_engine.analyze_investment(
            asset="TEST",
            bullish_factors=["earnings_growth"],
            bearish_factors=[],
            risk_factors=[],
        )
        self.assertIsNotNone(fin_result)

        # AI Safety
        safety_eval = AISafetyEvaluator()
        safety_result = safety_eval.evaluate_system(
            system_name="TEST",
            capabilities=["reasoning"],
            alignment_measures=["constitutional_ai"],
            risk_factors=[],
        )
        self.assertIsNotNone(safety_result)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTheosCore))
    suite.addTests(loader.loadTestsFromTestCase(TestTheosSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestMedicalDiagnosis))
    suite.addTests(loader.loadTestsFromTestCase(TestFinancialAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestAISafety))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_tests()

    # Print summary
    print("\n" + "=" * 70)
    print("THEOS Implementation Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)
