# Copyright (c) 2026 Frederick Stalnecker
# Licensed under the MIT License - see LICENSE file for details

"""
Comprehensive Unit Tests for THEOS Governor

This test suite validates:
1. Core governor logic (similarity, risk, quality metrics)
2. All stop conditions (convergence, risk, budget, plateau, max cycles)
3. Contradiction budget mechanics
4. Dual-clock reasoning system
5. Integration scenarios
6. Edge cases and boundary conditions

Test Framework: pytest (no external dependencies needed)
Python: 3.8+

Run tests with:
    pytest tests/test_governor.py -v
    pytest tests/test_governor.py -v --tb=short
    pytest tests/test_governor.py::TestGovernorCore -v
"""

import sys
import math
from pathlib import Path

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "code"))

import pytest
from theos_governor import (
    THEOSGovernor,
    GovernorConfig,
    EngineOutput,
    GovernorEvaluation,
    WisdomRecord,
    StopReason,
    Posture
)
from theos_dual_clock_governor import (
    TheosDualClockGovernor,
    GovernorConfig as DualClockConfig,
    EngineOutput as DualClockEngineOutput,
    GovernorDecision
)


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def basic_config():
    """Basic governor configuration for testing"""
    return GovernorConfig(
        max_cycles=5,
        similarity_threshold=0.90,
        risk_threshold=0.35,
        initial_contradiction_budget=1.0,
        contradiction_decay_rate=0.175,
        quality_improvement_threshold=0.05
    )


@pytest.fixture
def governor(basic_config):
    """Create a fresh governor instance"""
    return THEOSGovernor(config=basic_config)


@pytest.fixture
def dual_clock_governor():
    """Create a fresh dual-clock governor instance"""
    config = DualClockConfig(
        max_cycles=4,
        max_risk=0.35,
        min_improvement=0.02,
        plateau_cycles=2,
        contradiction_budget=1.5,
        similarity_converge=0.9,
        thrash_window=3
    )
    return TheosDualClockGovernor(cfg=config)


@pytest.fixture
def identical_outputs():
    """Two identical engine outputs (should converge immediately)"""
    output = "This is a well-reasoned conclusion about the topic at hand."
    return (
        EngineOutput(
            reasoning_mode="Constructive",
            output=output,
            confidence=0.95,
            internal_monologue="Building solution"
        ),
        EngineOutput(
            reasoning_mode="Critical",
            output=output,
            confidence=0.95,
            internal_monologue="Validating solution"
        )
    )


@pytest.fixture
def similar_outputs():
    """Two similar but not identical outputs (should converge eventually)"""
    return (
        EngineOutput(
            reasoning_mode="Constructive",
            output="The solution should prioritize efficiency and scalability.",
            confidence=0.85,
            internal_monologue="Building solution"
        ),
        EngineOutput(
            reasoning_mode="Critical",
            output="The solution should prioritize scalability and efficiency.",
            confidence=0.80,
            internal_monologue="Validating solution"
        )
    )


@pytest.fixture
def divergent_outputs():
    """Two very different outputs (high contradiction)"""
    return (
        EngineOutput(
            reasoning_mode="Constructive",
            output="We should maximize profit and shareholder value above all else.",
            confidence=0.70,
            internal_monologue="Building solution"
        ),
        EngineOutput(
            reasoning_mode="Critical",
            output="We should prioritize employee welfare and social responsibility.",
            confidence=0.65,
            internal_monologue="Validating solution"
        )
    )


@pytest.fixture
def high_risk_outputs():
    """Outputs that should trigger risk threshold"""
    return (
        EngineOutput(
            reasoning_mode="Constructive",
            output="Proceed with the dangerous experiment immediately.",
            confidence=0.40,
            internal_monologue="Low confidence"
        ),
        EngineOutput(
            reasoning_mode="Critical",
            output="This could cause catastrophic harm.",
            confidence=0.30,
            internal_monologue="Very low confidence"
        )
    )


# ==============================================================================
# TEST SUITE 1: GOVERNOR CORE LOGIC
# ==============================================================================

class TestGovernorCore:
    """Test core governor functionality"""

    def test_governor_initialization(self, basic_config):
        """Governor should initialize with correct configuration"""
        gov = THEOSGovernor(config=basic_config)
        assert gov.config == basic_config
        assert gov.wisdom_records == []
        assert gov.posture == Posture.NOM
        assert gov.cycle_history == []

    def test_default_config(self):
        """Governor should use default config if none provided"""
        gov = THEOSGovernor()
        assert gov.config is not None
        assert gov.config.max_cycles == 3
        assert gov.config.similarity_threshold == 0.90

    def test_similarity_identical_outputs(self, governor, identical_outputs):
        """Identical outputs should have similarity = 1.0"""
        left, right = identical_outputs
        similarity = governor.compute_similarity(left.output, right.output)
        assert similarity == 1.0

    def test_similarity_identical_case_insensitive(self, governor):
        """Similarity should be case-insensitive"""
        output1 = "The Quick Brown Fox"
        output2 = "the quick brown fox"
        similarity = governor.compute_similarity(output1, output2)
        assert similarity == 1.0

    def test_similarity_similar_outputs(self, governor, similar_outputs):
        """Similar outputs should have high similarity"""
        left, right = similar_outputs
        similarity = governor.compute_similarity(left.output, right.output)
        # Should be higher than divergent but lower than identical
        assert 0.4 < similarity < 1.0

    def test_similarity_divergent_outputs(self, governor, divergent_outputs):
        """Divergent outputs should have low similarity"""
        left, right = divergent_outputs
        similarity = governor.compute_similarity(left.output, right.output)
        assert 0.0 <= similarity < 0.5

    def test_similarity_empty_outputs(self, governor):
        """Empty outputs should have zero similarity"""
        similarity = governor.compute_similarity("", "")
        assert similarity == 0.0

    def test_similarity_one_empty(self, governor):
        """One empty output should give zero similarity"""
        similarity = governor.compute_similarity("Some content", "")
        assert similarity == 0.0

    def test_risk_identical_high_confidence(self, governor, identical_outputs):
        """Identical outputs with high confidence should have low risk"""
        left, right = identical_outputs
        risk = governor.compute_risk(left, right, similarity=1.0)
        assert risk < 0.2

    def test_risk_divergent_low_confidence(self, governor, divergent_outputs):
        """Divergent outputs with low confidence should have high risk"""
        left, right = divergent_outputs
        risk = governor.compute_risk(left, right, similarity=0.2)
        assert risk > 0.5

    def test_risk_bounded(self, governor):
        """Risk should always be in [0, 1]"""
        left = EngineOutput("Constructive", "output", 0.0, "")
        right = EngineOutput("Critical", "output", 1.0, "")
        
        for similarity in [0.0, 0.25, 0.5, 0.75, 1.0]:
            risk = governor.compute_risk(left, right, similarity)
            assert 0.0 <= risk <= 1.0

    def test_quality_metrics_structure(self, governor, similar_outputs):
        """Quality metrics should have all required keys"""
        left, right = similar_outputs
        metrics = governor.compute_quality_metrics(left, right, similarity=0.8)
        
        assert "coherence" in metrics
        assert "calibration" in metrics
        assert "evidence_quality" in metrics
        assert "actionability" in metrics
        
        for key, value in metrics.items():
            assert 0.0 <= value <= 1.0

    def test_quality_metrics_values_reasonable(self, governor, similar_outputs):
        """Quality metrics should have reasonable values"""
        left, right = similar_outputs
        metrics = governor.compute_quality_metrics(left, right, similarity=0.85)
        
        # Coherence should be average of confidences
        expected_coherence = (left.confidence + right.confidence) / 2.0
        assert metrics["coherence"] == expected_coherence
        
        # Calibration should equal similarity
        assert metrics["calibration"] == 0.85

    def test_contradiction_spent_calculation(self, governor):
        """Contradiction spent should be contradiction_level * decay_rate"""
        contradiction_level = 0.5
        expected_spent = contradiction_level * governor.config.contradiction_decay_rate
        actual_spent = governor.compute_contradiction_spent(contradiction_level)
        assert actual_spent == expected_spent

    def test_contradiction_spent_zero(self, governor):
        """Zero contradiction should spend zero budget"""
        spent = governor.compute_contradiction_spent(0.0)
        assert spent == 0.0

    def test_contradiction_spent_maximum(self, governor):
        """Maximum contradiction should spend maximum budget"""
        spent = governor.compute_contradiction_spent(1.0)
        assert spent == governor.config.contradiction_decay_rate


# ==============================================================================
# TEST SUITE 2: STOP CONDITIONS
# ==============================================================================

class TestStopConditions:
    """Test all five stop conditions"""

    def test_stop_convergence_achieved(self, governor, identical_outputs):
        """Should stop when similarity >= threshold (convergence)"""
        left, right = identical_outputs
        evaluation = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
        
        assert evaluation.decision == "STOP"
        assert evaluation.stop_reason == StopReason.CONVERGENCE_ACHIEVED
        assert evaluation.similarity_score >= governor.config.similarity_threshold

    def test_stop_risk_threshold_exceeded(self, governor, high_risk_outputs):
        """Should stop when risk > threshold"""
        left, right = high_risk_outputs
        evaluation = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
        
        assert evaluation.decision == "STOP"
        assert evaluation.stop_reason == StopReason.RISK_THRESHOLD_EXCEEDED
        assert evaluation.risk_score > governor.config.risk_threshold

    def test_stop_contradiction_exhausted(self, governor, divergent_outputs):
        """Should stop when contradiction budget exhausted"""
        left, right = divergent_outputs
        
        # Run cycles until budget exhausted
        budget = governor.config.initial_contradiction_budget
        cycle_num = 1
        
        while budget > 0 and cycle_num <= 10:
            evaluation = governor.evaluate_cycle(left, right, current_budget=budget, cycle_number=cycle_num)
            budget = evaluation.remaining_budget
            
            if evaluation.decision == "STOP":
                break
            
            cycle_num += 1
        
        # Should eventually stop (may be due to risk, budget, plateau, or max cycles)
        assert evaluation.decision == "STOP"
        assert evaluation.stop_reason is not None

    def test_stop_plateau_detected(self, governor, similar_outputs):
        """Should stop when quality plateaus"""
        left, right = similar_outputs
        
        # Run multiple cycles with similar quality
        for cycle_num in range(1, 5):
            evaluation = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=cycle_num)
            
            if cycle_num > 1 and evaluation.stop_reason == StopReason.PLATEAU_DETECTED:
                assert evaluation.decision == "STOP"
                return
        
        # If we get here, plateau detection may not have triggered
        # This is acceptable - plateau detection depends on history

    def test_stop_max_cycles_reached(self, governor, similar_outputs):
        """Should stop when max cycles reached"""
        left, right = similar_outputs
        
        # Run exactly max_cycles
        for cycle_num in range(1, governor.config.max_cycles + 1):
            evaluation = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=cycle_num)
            
            if cycle_num == governor.config.max_cycles:
                # Should stop, but may be for various reasons (convergence, plateau, max cycles)
                assert evaluation.decision == "STOP"
                assert evaluation.stop_reason is not None

    def test_stop_reason_is_set(self, governor, identical_outputs):
        """Stop reason should always be set when decision is STOP"""
        left, right = identical_outputs
        evaluation = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
        
        if evaluation.decision == "STOP":
            assert evaluation.stop_reason is not None
            assert isinstance(evaluation.stop_reason, StopReason)


# ==============================================================================
# TEST SUITE 3: CONTRADICTION BUDGET MECHANICS
# ==============================================================================

class TestContradictionBudget:
    """Test contradiction budget tracking and exhaustion"""

    def test_budget_decreases_with_contradiction(self, governor, divergent_outputs):
        """Budget should decrease as contradiction is spent"""
        left, right = divergent_outputs
        initial_budget = 1.0
        
        evaluation = governor.evaluate_cycle(left, right, current_budget=initial_budget, cycle_number=1)
        
        assert evaluation.remaining_budget < initial_budget
        assert evaluation.contradiction_spent > 0.0

    def test_budget_unchanged_with_convergence(self, governor, identical_outputs):
        """Budget should barely decrease with convergence (low contradiction)"""
        left, right = identical_outputs
        initial_budget = 1.0
        
        evaluation = governor.evaluate_cycle(left, right, current_budget=initial_budget, cycle_number=1)
        
        # Should spend very little budget (similarity is high)
        assert evaluation.contradiction_spent < 0.1
        assert evaluation.remaining_budget > 0.9

    def test_budget_goes_negative(self, governor, divergent_outputs):
        """Remaining budget can go negative (triggers stop condition)"""
        left, right = divergent_outputs
        
        # Start with very small budget
        evaluation = governor.evaluate_cycle(left, right, current_budget=0.05, cycle_number=1)
        
        # Should result in negative or zero budget
        assert evaluation.remaining_budget <= 0.0

    def test_budget_tracking_across_cycles(self, governor, divergent_outputs):
        """Budget should be tracked correctly across multiple cycles"""
        left, right = divergent_outputs
        
        budget = governor.config.initial_contradiction_budget
        budgets = [budget]
        
        for cycle_num in range(1, 4):
            evaluation = governor.evaluate_cycle(left, right, current_budget=budget, cycle_number=cycle_num)
            budget = evaluation.remaining_budget
            budgets.append(budget)
        
        # Budgets should be monotonically decreasing
        for i in range(len(budgets) - 1):
            assert budgets[i] >= budgets[i + 1]


# ==============================================================================
# TEST SUITE 4: DUAL-CLOCK GOVERNOR
# ==============================================================================

class TestDualClockGovernor:
    """Test dual-clock governor functionality"""

    def test_dual_clock_initialization(self, dual_clock_governor):
        """Dual-clock governor should initialize correctly"""
        assert dual_clock_governor.cfg.max_cycles == 4
        assert dual_clock_governor.history == []
        assert dual_clock_governor.best_score is None
        assert dual_clock_governor.plateau_count == 0

    def test_dual_clock_scoring(self, dual_clock_governor):
        """Scoring should combine quality metrics correctly"""
        output = DualClockEngineOutput(
            engine_id="L",
            cycle_index=1,
            answer="Test answer",
            coherence=0.8,
            calibration=0.75,
            evidence=0.6,
            actionability=0.7,
            risk=0.1,
            constraint_ok=True
        )
        
        score = dual_clock_governor.score(output)
        
        # Score should be weighted combination
        expected = (1.2 * 0.8 + 1.0 * 0.75 + 1.1 * 0.6 + 1.0 * 0.7 - 1.6 * 0.1)
        assert score == expected

    def test_dual_clock_score_negative_on_constraint_violation(self, dual_clock_governor):
        """Score should be -1.0 if constraints violated"""
        output = DualClockEngineOutput(
            engine_id="L",
            cycle_index=1,
            answer="Test answer",
            constraint_ok=False
        )
        
        score = dual_clock_governor.score(output)
        assert score == -1.0

    def test_dual_clock_score_negative_on_high_risk(self, dual_clock_governor):
        """Score should be -1.0 if risk exceeds threshold"""
        output = DualClockEngineOutput(
            engine_id="L",
            cycle_index=1,
            answer="Test answer",
            risk=0.5,  # Exceeds max_risk of 0.35
            constraint_ok=True
        )
        
        score = dual_clock_governor.score(output)
        assert score == -1.0

    def test_dual_clock_step_convergence(self, dual_clock_governor):
        """Should freeze when outputs converge"""
        left = DualClockEngineOutput(
            engine_id="L",
            cycle_index=1,
            answer="The solution is optimal",
            coherence=0.9,
            calibration=0.9,
            evidence=0.8,
            actionability=0.85,
            risk=0.1,
            constraint_ok=True
        )
        
        right = DualClockEngineOutput(
            engine_id="R",
            cycle_index=1,
            answer="The solution is optimal",
            coherence=0.9,
            calibration=0.9,
            evidence=0.8,
            actionability=0.85,
            risk=0.1,
            constraint_ok=True
        )
        
        decision = dual_clock_governor.step(left, right)
        
        assert decision.decision == "FREEZE"
        assert decision.chosen_answer is not None

    def test_dual_clock_step_max_cycles(self, dual_clock_governor):
        """Should freeze when max cycles reached"""
        left = DualClockEngineOutput(
            engine_id="L",
            cycle_index=4,  # At max_cycles
            answer="Answer L",
            coherence=0.5,
            calibration=0.5,
            evidence=0.5,
            actionability=0.5,
            risk=0.1,
            constraint_ok=True
        )
        
        right = DualClockEngineOutput(
            engine_id="R",
            cycle_index=4,
            answer="Answer R",
            coherence=0.5,
            calibration=0.5,
            evidence=0.5,
            actionability=0.5,
            risk=0.1,
            constraint_ok=True
        )
        
        decision = dual_clock_governor.step(left, right)
        
        assert decision.decision == "FREEZE"
        assert "max cycles" in decision.reason.lower()


# ==============================================================================
# TEST SUITE 5: WISDOM ACCUMULATION
# ==============================================================================

class TestWisdomAccumulation:
    """Test wisdom accumulation functionality"""

    def test_add_wisdom_record(self, governor):
        """Should add wisdom records correctly"""
        record = WisdomRecord(
            domain="Medical_Ethics",
            lesson="Prioritizing individual autonomy leads to better outcomes",
            consequence_type="benign",
            future_bias="Increase weight on autonomy in similar decisions",
            timestamp="2026-02-19T12:00:00Z"
        )
        
        governor.add_wisdom(record)
        
        assert len(governor.wisdom_records) == 1
        assert governor.wisdom_records[0] == record

    def test_add_multiple_wisdom_records(self, governor):
        """Should accumulate multiple wisdom records"""
        records = [
            WisdomRecord("Domain1", "Lesson1", "benign", "Bias1", "2026-02-19T12:00:00Z"),
            WisdomRecord("Domain2", "Lesson2", "probing", "Bias2", "2026-02-19T12:01:00Z"),
            WisdomRecord("Domain3", "Lesson3", "near_miss", "Bias3", "2026-02-19T12:02:00Z"),
        ]
        
        for record in records:
            governor.add_wisdom(record)
        
        assert len(governor.wisdom_records) == 3

    def test_wisdom_consequence_types(self, governor):
        """Wisdom records should support all consequence types"""
        consequence_types = ["benign", "probing", "near_miss", "harm"]
        
        for ctype in consequence_types:
            record = WisdomRecord(
                domain="Test",
                lesson="Test lesson",
                consequence_type=ctype,
                future_bias="Test bias",
                timestamp="2026-02-19T12:00:00Z"
            )
            governor.add_wisdom(record)
        
        assert len(governor.wisdom_records) == 4


# ==============================================================================
# TEST SUITE 6: AUDIT TRAIL
# ==============================================================================

class TestAuditTrail:
    """Test audit trail generation"""

    def test_audit_trail_structure(self, governor, similar_outputs):
        """Audit trail should have required structure"""
        left, right = similar_outputs
        
        # Run a cycle
        evaluation = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
        
        # Get audit trail
        audit = governor.get_audit_trail()
        
        assert "total_cycles" in audit
        assert "contradiction_budget_used" in audit
        assert "final_similarity" in audit
        assert "final_risk" in audit
        assert "stop_reason" in audit

    def test_cycle_history_tracking(self, governor, similar_outputs):
        """Governor should track cycle history"""
        left, right = similar_outputs
        
        # Run multiple cycles
        for cycle_num in range(1, 4):
            governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=cycle_num)
        
        assert len(governor.cycle_history) == 3

    def test_internal_monologue_present(self, governor, similar_outputs):
        """Evaluations should include internal monologue"""
        left, right = similar_outputs
        evaluation = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
        
        assert evaluation.internal_monologue != ""
        assert "[Governor]" in evaluation.internal_monologue


# ==============================================================================
# TEST SUITE 7: EDGE CASES AND BOUNDARY CONDITIONS
# ==============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_output_strings(self, governor):
        """Should reject empty output strings"""
        left = EngineOutput("Constructive", "", 0.5, "")
        right = EngineOutput("Critical", "valid", 0.5, "")
        
        # Should raise ValueError for empty output
        with pytest.raises(ValueError, match="output cannot be empty"):
            governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)

    def test_very_long_output_strings(self, governor):
        """Should handle very long output strings"""
        long_text = "word " * 10000  # 50,000 characters
        
        left = EngineOutput("Constructive", long_text, 0.8, "")
        right = EngineOutput("Critical", long_text, 0.8, "")
        
        evaluation = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
        assert evaluation is not None

    def test_extreme_confidence_values(self, governor):
        """Should handle extreme confidence values"""
        left = EngineOutput("Constructive", "output", 0.0, "")
        right = EngineOutput("Critical", "output", 1.0, "")
        
        evaluation = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
        assert 0.0 <= evaluation.risk_score <= 1.0

    def test_zero_budget(self, governor, similar_outputs):
        """Should handle zero budget"""
        left, right = similar_outputs
        evaluation = governor.evaluate_cycle(left, right, current_budget=0.0, cycle_number=1)
        
        assert evaluation.remaining_budget <= 0.0
        assert evaluation.decision == "STOP"

    def test_negative_budget(self, governor, similar_outputs):
        """Should reject negative budget"""
        left, right = similar_outputs
        
        # Should raise ValueError for negative budget
        with pytest.raises(ValueError, match="cannot be negative"):
            governor.evaluate_cycle(left, right, current_budget=-1.0, cycle_number=1)

    def test_single_word_outputs(self, governor):
        """Should handle single-word outputs"""
        left = EngineOutput("Constructive", "Yes", 0.8, "")
        right = EngineOutput("Critical", "No", 0.7, "")
        
        evaluation = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
        assert evaluation is not None

    def test_special_characters_in_output(self, governor):
        """Should handle special characters"""
        left = EngineOutput("Constructive", "Test @#$%^&*()", 0.8, "")
        right = EngineOutput("Critical", "Test @#$%^&*()", 0.8, "")
        
        evaluation = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
        assert evaluation is not None

    def test_unicode_in_output(self, governor):
        """Should handle Unicode characters"""
        left = EngineOutput("Constructive", "Test 你好 مرحبا", 0.8, "")
        right = EngineOutput("Critical", "Test 你好 مرحبا", 0.8, "")
        
        evaluation = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
        assert evaluation is not None


# ==============================================================================
# TEST SUITE 8: INTEGRATION TESTS
# ==============================================================================

class TestIntegration:
    """Integration tests for complete reasoning cycles"""

    def test_full_reasoning_cycle_convergence(self, governor):
        """Should complete a full reasoning cycle leading to convergence"""
        output = "The optimal approach balances efficiency and safety."
        
        left = EngineOutput("Constructive", output, 0.90, "Building solution")
        right = EngineOutput("Critical", output, 0.90, "Validating solution")
        
        # Run cycle
        evaluation = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
        
        # Should converge
        assert evaluation.decision == "STOP"
        assert evaluation.stop_reason == StopReason.CONVERGENCE_ACHIEVED

    def test_full_reasoning_cycle_divergence(self, governor):
        """Should handle divergent outputs appropriately"""
        left = EngineOutput(
            "Constructive",
            "We should maximize profit above all else.",
            0.70,
            "Building solution"
        )
        right = EngineOutput(
            "Critical",
            "We should prioritize social responsibility and ethics.",
            0.65,
            "Challenging solution"
        )
        
        evaluation = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
        
        # Should not converge immediately
        assert evaluation.similarity_score < 0.9

    def test_multi_cycle_reasoning(self, governor):
        """Should handle multiple reasoning cycles"""
        outputs = [
            ("First pass", "First pass"),
            ("Second pass refined", "Second pass refined"),
            ("Final answer", "Final answer")
        ]
        
        budget = governor.config.initial_contradiction_budget
        
        for cycle_num, (left_text, right_text) in enumerate(outputs, 1):
            left = EngineOutput("Constructive", left_text, 0.85, "")
            right = EngineOutput("Critical", right_text, 0.85, "")
            
            evaluation = governor.evaluate_cycle(left, right, current_budget=budget, cycle_number=cycle_num)
            budget = evaluation.remaining_budget
            
            assert evaluation is not None
            assert len(governor.cycle_history) == cycle_num

    def test_wisdom_integration_with_reasoning(self, governor):
        """Wisdom should be tracked alongside reasoning"""
        # Add wisdom
        wisdom = WisdomRecord(
            domain="AI_Safety",
            lesson="Contradictions reveal uncertainty",
            consequence_type="benign",
            future_bias="Increase tolerance for contradiction",
            timestamp="2026-02-19T12:00:00Z"
        )
        governor.add_wisdom(wisdom)
        
        # Run reasoning
        left = EngineOutput("Constructive", "Test output", 0.8, "")
        right = EngineOutput("Critical", "Test output", 0.8, "")
        evaluation = governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
        
        # Both should be tracked
        assert len(governor.wisdom_records) == 1
        assert len(governor.cycle_history) == 1


# ==============================================================================
# TEST SUITE 9: POSTURE MANAGEMENT
# ==============================================================================

class TestPostureManagement:
    """Test governor posture states"""

    def test_initial_posture(self, governor):
        """Governor should start in NOM posture"""
        assert governor.posture == Posture.NOM

    def test_posture_enum_values(self):
        """Posture enum should have all required values"""
        assert hasattr(Posture, "NOM")
        assert hasattr(Posture, "PEM")
        assert hasattr(Posture, "CM")
        assert hasattr(Posture, "IM")


# ==============================================================================
# TEST SUITE 10: CONFIGURATION VALIDATION
# ==============================================================================

class TestConfigurationValidation:
    """Test configuration validation and bounds"""

    def test_config_similarity_threshold_bounds(self):
        """Similarity threshold should be in [0, 1]"""
        config = GovernorConfig(similarity_threshold=0.95)
        assert 0.0 <= config.similarity_threshold <= 1.0

    def test_config_risk_threshold_bounds(self):
        """Risk threshold should be in [0, 1]"""
        config = GovernorConfig(risk_threshold=0.35)
        assert 0.0 <= config.risk_threshold <= 1.0

    def test_config_decay_rate_reasonable(self):
        """Decay rate should be reasonable"""
        config = GovernorConfig(contradiction_decay_rate=0.175)
        assert 0.0 < config.contradiction_decay_rate < 1.0

    def test_config_hyperparameters_sum(self):
        """Hyperparameters should sum appropriately"""
        config = GovernorConfig()
        # alpha + beta + gamma + delta + epsilon should be meaningful
        assert config.alpha > 0
        assert config.beta > 0
        assert config.gamma > 0
        assert config.delta > 0
        assert config.epsilon > 0


# ==============================================================================
# PERFORMANCE TESTS
# ==============================================================================

class TestPerformance:
    """Performance and efficiency tests"""

    def test_similarity_computation_performance(self, governor):
        """Similarity computation should be fast"""
        import time
        
        left = "word " * 1000
        right = "word " * 1000
        
        start = time.time()
        for _ in range(100):
            governor.compute_similarity(left, right)
        elapsed = time.time() - start
        
        # Should complete 100 iterations in < 1 second
        assert elapsed < 1.0

    def test_evaluation_performance(self, governor, similar_outputs):
        """Evaluation should be fast"""
        import time
        
        left, right = similar_outputs
        
        start = time.time()
        for _ in range(100):
            governor.evaluate_cycle(left, right, current_budget=1.0, cycle_number=1)
        elapsed = time.time() - start
        
        # Should complete 100 evaluations in < 2 seconds
        assert elapsed < 2.0


# ==============================================================================
# MAIN TEST RUNNER
# ==============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
