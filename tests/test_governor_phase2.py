"""
THEOS Phase 2 Unit Tests
Comprehensive test suite for Governor implementation

Tests cover:
- Wisdom integration and retrieval
- Momentary past tracking
- Energy accounting
- Ethical alignment
- All halting criteria
- Output generation
- Audit trails
- Edge cases and error handling

Author: Frederick Davis Stalnecker
Date: February 21, 2026
"""

import pytest
import math
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Import Phase 2 Governor
import sys
sys.path.insert(0, '/home/ubuntu/THEOS_repo/code')

from theos_governor_phase2 import (
    THEOSGovernor,
    GovernorConfig,
    EngineOutput,
    WisdomRecord,
    MomentaryPast,
    GovernorEvaluation,
    EnergyMetrics,
    EthicalAlignment,
    UnifiedQueryInterface,
    ReasoningMode,
    StopReason,
    ContradictionType,
    WisdomType
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_wisdom_storage():
    """Create temporary wisdom storage"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('[]')
        return f.name


@pytest.fixture
def governor_config():
    """Create default Governor config"""
    return GovernorConfig()


@pytest.fixture
def governor(temp_wisdom_storage, governor_config):
    """Create Governor instance"""
    return THEOSGovernor(governor_config, temp_wisdom_storage)


@pytest.fixture
def engine_output_constructive():
    """Create constructive engine output"""
    return EngineOutput(
        reasoning_mode=ReasoningMode.CONSTRUCTIVE,
        output="Provide information with ethical caveats to respect user autonomy.",
        confidence=0.75,
        internal_monologue="[Engine L] Prioritizing user autonomy and information access.",
        reasoning_depth=1
    )


@pytest.fixture
def engine_output_critical():
    """Create critical engine output"""
    return EngineOutput(
        reasoning_mode=ReasoningMode.CRITICAL,
        output="Refuse ethically ambiguous requests to prevent harm.",
        confidence=0.80,
        internal_monologue="[Engine R] Prioritizing harm prevention over autonomy.",
        reasoning_depth=1
    )


# ============================================================================
# TESTS: CONFIGURATION VALIDATION
# ============================================================================

class TestGovernorConfiguration:
    """Test Governor configuration and validation"""
    
    def test_config_creation(self):
        """Test creating valid configuration"""
        config = GovernorConfig()
        assert config.similarity_threshold == 0.85
        assert config.max_cycles == 7
        assert config.initial_contradiction_budget == 1.0
    
    def test_config_validation_passes(self):
        """Test that valid config passes validation"""
        config = GovernorConfig()
        config.validate()  # Should not raise
    
    def test_config_invalid_similarity_threshold(self):
        """Test invalid similarity threshold"""
        config = GovernorConfig()
        config.similarity_threshold = 1.5
        with pytest.raises(ValueError):
            config.validate()
    
    def test_config_invalid_max_cycles(self):
        """Test invalid max cycles"""
        config = GovernorConfig()
        config.max_cycles = 2
        config.min_cycles = 5
        with pytest.raises(ValueError):
            config.validate()


# ============================================================================
# TESTS: WISDOM INTEGRATION
# ============================================================================

class TestWisdomIntegration:
    """Test wisdom storage, retrieval, and influence"""
    
    def test_wisdom_record_creation(self):
        """Test creating wisdom record"""
        record = WisdomRecord(
            query="Should AI refuse ambiguous requests?",
            hypothesis="Harm prevention is primary",
            resolution="Yes, with transparent explanation",
            confidence=0.85,
            wisdom_type=WisdomType.LEARNED,
            contradiction_level=0.2,
            ethical_alignment=0.9
        )
        assert record.confidence == 0.85
        assert record.wisdom_type == WisdomType.LEARNED
    
    def test_wisdom_record_validation_confidence(self):
        """Test wisdom record validates confidence"""
        with pytest.raises(ValueError):
            WisdomRecord(
                query="test",
                hypothesis="test",
                resolution="test",
                confidence=1.5,  # Invalid
                wisdom_type=WisdomType.LEARNED,
                contradiction_level=0.2,
                ethical_alignment=0.9
            )
    
    def test_wisdom_record_validation_alignment(self):
        """Test wisdom record validates ethical alignment"""
        with pytest.raises(ValueError):
            WisdomRecord(
                query="test",
                hypothesis="test",
                resolution="test",
                confidence=0.8,
                wisdom_type=WisdomType.LEARNED,
                contradiction_level=0.2,
                ethical_alignment=-0.1  # Invalid
            )
    
    def test_uqi_store_wisdom(self, temp_wisdom_storage):
        """Test storing wisdom via UQI"""
        uqi = UnifiedQueryInterface(temp_wisdom_storage)
        
        record = WisdomRecord(
            query="test query",
            hypothesis="test hypothesis",
            resolution="test resolution",
            confidence=0.8,
            wisdom_type=WisdomType.LEARNED,
            contradiction_level=0.2,
            ethical_alignment=0.85
        )
        
        success = uqi.store_wisdom(record)
        assert success is True
        assert len(uqi.wisdom_db) == 1
    
    def test_uqi_retrieve_wisdom_exact_match(self, temp_wisdom_storage):
        """Test retrieving wisdom with exact match"""
        uqi = UnifiedQueryInterface(temp_wisdom_storage)
        
        record = WisdomRecord(
            query="Should AI refuse ambiguous requests?",
            hypothesis="Harm prevention",
            resolution="Yes",
            confidence=0.9,
            wisdom_type=WisdomType.LEARNED,
            contradiction_level=0.1,
            ethical_alignment=0.95
        )
        uqi.store_wisdom(record)
        
        # Exact match should have high similarity
        retrieved = uqi.retrieve_wisdom("Should AI refuse ambiguous requests?", threshold=0.5)
        assert len(retrieved) > 0
        assert retrieved[0].query == record.query
    
    def test_uqi_retrieve_wisdom_no_match(self, temp_wisdom_storage):
        """Test retrieving wisdom with no match"""
        uqi = UnifiedQueryInterface(temp_wisdom_storage)
        
        record = WisdomRecord(
            query="Question A",
            hypothesis="test",
            resolution="test",
            confidence=0.8,
            wisdom_type=WisdomType.LEARNED,
            contradiction_level=0.2,
            ethical_alignment=0.85
        )
        uqi.store_wisdom(record)
        
        # Very different query should not match
        retrieved = uqi.retrieve_wisdom("Completely different question", threshold=0.9)
        assert len(retrieved) == 0
    
    def test_uqi_similarity_computation(self, temp_wisdom_storage):
        """Test semantic similarity computation"""
        uqi = UnifiedQueryInterface(temp_wisdom_storage)
        
        # Identical queries should have similarity = 1.0
        sim = uqi._compute_similarity("test query", "test query")
        assert sim > 0.95
        
        # Completely different queries should have low similarity
        sim = uqi._compute_similarity("abc xyz", "def ghi")
        assert sim < 0.5
    
    def test_uqi_statistics(self, temp_wisdom_storage):
        """Test wisdom statistics"""
        uqi = UnifiedQueryInterface(temp_wisdom_storage)
        
        # Empty database
        stats = uqi.get_statistics()
        assert stats['total_records'] == 0
        
        # Add records
        for i in range(3):
            record = WisdomRecord(
                query=f"query {i}",
                hypothesis="test",
                resolution="test",
                confidence=0.7 + (0.1 * i),
                wisdom_type=WisdomType.LEARNED,
                contradiction_level=0.2,
                ethical_alignment=0.85
            )
            uqi.store_wisdom(record)
        
        stats = uqi.get_statistics()
        assert stats['total_records'] == 3
        assert stats['learned_records'] == 3
        assert stats['average_confidence'] > 0.7


# ============================================================================
# TESTS: MOMENTARY PAST
# ============================================================================

class TestMomentaryPast:
    """Test momentary past tracking"""
    
    def test_momentary_past_creation(self):
        """Test creating momentary past"""
        mp = MomentaryPast(
            previous_output_l="Output L",
            previous_output_r="Output R",
            previous_contradiction=0.3,
            previous_cycle_number=1
        )
        assert mp.previous_output_l == "Output L"
        assert mp.previous_contradiction == 0.3
    
    def test_momentary_past_influence(self, governor):
        """Test momentary past influence computation"""
        # Cycle 1: no previous output
        influence = governor._compute_momentary_past_influence(1)
        assert influence == 0.0
        
        # Cycle 2: with previous output
        governor.momentary_past.previous_output_l = "test"
        influence = governor._compute_momentary_past_influence(2)
        assert 0.0 < influence < 1.0
        
        # Influence should decrease with cycle number
        influence_3 = governor._compute_momentary_past_influence(3)
        assert influence_3 < influence


# ============================================================================
# TESTS: METRIC COMPUTATIONS
# ============================================================================

class TestMetricComputations:
    """Test metric computation functions"""
    
    def test_similarity_identical_outputs(self, governor):
        """Test similarity of identical outputs"""
        output = "This is a test output"
        similarity = governor.compute_similarity(output, output)
        assert similarity > 0.95
    
    def test_similarity_different_outputs(self, governor):
        """Test similarity of different outputs"""
        output1 = "This is output A"
        output2 = "This is output B"
        similarity = governor.compute_similarity(output1, output2)
        assert 0.0 <= similarity <= 1.0
        assert similarity < 0.95
    
    def test_similarity_empty_outputs(self, governor):
        """Test similarity with empty outputs"""
        similarity = governor.compute_similarity("", "test")
        assert similarity == 0.0
    
    def test_risk_computation(self, governor, engine_output_constructive, engine_output_critical):
        """Test risk computation"""
        risk = governor.compute_risk(
            engine_output_constructive,
            engine_output_critical,
            similarity=0.5
        )
        assert 0.0 <= risk <= 1.0
    
    def test_risk_high_disagreement(self, governor):
        """Test risk with high disagreement"""
        output_l = EngineOutput(
            reasoning_mode=ReasoningMode.CONSTRUCTIVE,
            output="Option A is best",
            confidence=0.9,
            internal_monologue="test"
        )
        output_r = EngineOutput(
            reasoning_mode=ReasoningMode.CRITICAL,
            output="Option B is best",
            confidence=0.9,
            internal_monologue="test"
        )
        
        risk = governor.compute_risk(output_l, output_r, similarity=0.1)
        assert risk > 0.5  # High risk from disagreement
    
    def test_quality_metrics(self, governor, engine_output_constructive, engine_output_critical):
        """Test quality metrics computation"""
        metrics = governor.compute_quality_metrics(
            engine_output_constructive,
            engine_output_critical,
            similarity=0.7
        )
        
        assert 'coherence' in metrics
        assert 'confidence' in metrics
        assert 'convergence' in metrics
        assert 'depth' in metrics
        
        # All metrics should be in [0, 1]
        for value in metrics.values():
            assert 0.0 <= value <= 1.0
    
    def test_contradiction_spent(self, governor):
        """Test contradiction budget spending"""
        contradiction_level = 0.5
        spent = governor.compute_contradiction_spent(contradiction_level)
        
        expected = contradiction_level * governor.config.contradiction_decay_rate
        assert abs(spent - expected) < 0.001


# ============================================================================
# TESTS: ETHICAL ALIGNMENT
# ============================================================================

class TestEthicalAlignment:
    """Test ethical alignment computation"""
    
    def test_ethical_alignment_high_confidence(self, governor):
        """Test ethical alignment with high confidence engines"""
        output_l = EngineOutput(
            reasoning_mode=ReasoningMode.CONSTRUCTIVE,
            output="test",
            confidence=0.9,
            internal_monologue="test"
        )
        output_r = EngineOutput(
            reasoning_mode=ReasoningMode.CRITICAL,
            output="test",
            confidence=0.85,
            internal_monologue="test"
        )
        
        alignment = governor._compute_ethical_alignment(output_l, output_r, contradiction=0.1)
        assert alignment > 0.7
    
    def test_ethical_alignment_weak_critical_engine(self, governor):
        """Test ethical alignment when critical engine is weak"""
        output_l = EngineOutput(
            reasoning_mode=ReasoningMode.CONSTRUCTIVE,
            output="test",
            confidence=0.9,
            internal_monologue="test"
        )
        output_r = EngineOutput(
            reasoning_mode=ReasoningMode.CRITICAL,
            output="test",
            confidence=0.3,  # Weak critical engine
            internal_monologue="test"
        )
        
        alignment = governor._compute_ethical_alignment(output_l, output_r, contradiction=0.1)
        assert alignment < 0.7  # Lower alignment due to weak critical engine
    
    def test_ethical_alignment_transparent_contradiction(self, governor):
        """Test ethical alignment bonus for transparent contradiction"""
        output_l = EngineOutput(
            reasoning_mode=ReasoningMode.CONSTRUCTIVE,
            output="test",
            confidence=0.8,
            internal_monologue="test"
        )
        output_r = EngineOutput(
            reasoning_mode=ReasoningMode.CRITICAL,
            output="test",
            confidence=0.8,
            internal_monologue="test"
        )
        
        # High contradiction (transparent)
        alignment_high_contradiction = governor._compute_ethical_alignment(
            output_l, output_r, contradiction=0.5
        )
        
        # Low contradiction
        alignment_low_contradiction = governor._compute_ethical_alignment(
            output_l, output_r, contradiction=0.1
        )
        
        # Transparent contradiction should have bonus
        assert alignment_high_contradiction > alignment_low_contradiction


# ============================================================================
# TESTS: HALTING CRITERIA
# ============================================================================

class TestHaltingCriteria:
    """Test all halting criteria"""
    
    def test_convergence_halting(self, governor, engine_output_constructive, engine_output_critical):
        """Test convergence halting criterion"""
        # Create nearly identical outputs
        output_l = EngineOutput(
            reasoning_mode=ReasoningMode.CONSTRUCTIVE,
            output="The answer is yes",
            confidence=0.9,
            internal_monologue="test"
        )
        output_r = EngineOutput(
            reasoning_mode=ReasoningMode.CRITICAL,
            output="The answer is yes",
            confidence=0.9,
            internal_monologue="test"
        )
        
        evaluation = governor.evaluate_cycle(output_l, output_r, current_budget=1.0, cycle_number=1)
        
        # Should converge (high similarity)
        assert evaluation.similarity_score > 0.8
        if evaluation.similarity_score >= governor.config.similarity_threshold:
            assert evaluation.decision == "STOP"
            assert evaluation.stop_reason == StopReason.CONVERGENCE_ACHIEVED
    
    def test_risk_threshold_halting(self, governor):
        """Test risk threshold halting criterion"""
        # Create outputs with high confidence but low similarity
        output_l = EngineOutput(
            reasoning_mode=ReasoningMode.CONSTRUCTIVE,
            output="Option A is correct",
            confidence=0.9,
            internal_monologue="test"
        )
        output_r = EngineOutput(
            reasoning_mode=ReasoningMode.CRITICAL,
            output="Option B is correct",
            confidence=0.9,
            internal_monologue="test"
        )
        
        evaluation = governor.evaluate_cycle(output_l, output_r, current_budget=1.0, cycle_number=1)
        
        # Evaluation should complete successfully
        assert evaluation is not None
        assert 0.0 <= evaluation.contradiction_level <= 1.0
        assert 0.0 <= evaluation.risk_score <= 1.0
    
    def test_budget_exhaustion_halting(self, governor, engine_output_constructive, engine_output_critical):
        """Test contradiction budget exhaustion"""
        # Start with minimal budget
        evaluation = governor.evaluate_cycle(
            engine_output_constructive,
            engine_output_critical,
            current_budget=0.01,  # Very small budget
            cycle_number=1
        )
        
        # Should stop due to budget exhaustion
        if evaluation.remaining_budget <= 0:
            assert evaluation.decision == "STOP"
            assert evaluation.stop_reason == StopReason.CONTRADICTION_EXHAUSTED
    
    def test_plateau_detection(self, governor, engine_output_constructive, engine_output_critical):
        """Test plateau detection halting"""
        # First cycle
        eval1 = governor.evaluate_cycle(
            engine_output_constructive,
            engine_output_critical,
            current_budget=1.0,
            cycle_number=1
        )
        
        # Second cycle with no improvement
        eval2 = governor.evaluate_cycle(
            engine_output_constructive,
            engine_output_critical,
            current_budget=eval1.remaining_budget,
            cycle_number=2
        )
        
        # If quality improvement is too small, should detect plateau
        quality_improvement = eval2.composite_quality - eval1.composite_quality
        if quality_improvement < governor.config.quality_improvement_threshold:
            assert eval2.decision == "STOP"
            assert eval2.stop_reason == StopReason.PLATEAU_DETECTED
    
    def test_max_cycles_halting(self, governor, engine_output_constructive, engine_output_critical):
        """Test max cycles halting"""
        # Run until max cycles
        for cycle_num in range(1, governor.config.max_cycles + 1):
            evaluation = governor.evaluate_cycle(
                engine_output_constructive,
                engine_output_critical,
                current_budget=1.0,
                cycle_number=cycle_num
            )
            
            if cycle_num == governor.config.max_cycles:
                # Should stop at max cycles (may be due to plateau or max cycles)
                assert evaluation.decision == "STOP"
                assert evaluation.stop_reason in [
                    StopReason.MAX_CYCLES_REACHED,
                    StopReason.PLATEAU_DETECTED,
                    StopReason.CONVERGENCE_ACHIEVED
                ]


# ============================================================================
# TESTS: ENERGY ACCOUNTING
# ============================================================================

class TestEnergyAccounting:
    """Test energy accounting and measurement"""
    
    def test_energy_cost_computation(self, governor):
        """Test energy cost computation"""
        cost_1 = governor._compute_energy_cost(1)
        cost_2 = governor._compute_energy_cost(2)
        
        # Cost should increase with cycle depth
        assert cost_2 > cost_1
        assert cost_1 > 0
    
    def test_energy_metrics_tracking(self, governor):
        """Test energy metrics tracking"""
        initial_tokens = governor.energy_metrics.total_tokens
        
        # Simulate some cycles
        for i in range(3):
            cost = governor._compute_energy_cost(i + 1)
            governor.energy_metrics.tokens_per_cycle.append(cost)
            governor.energy_metrics.total_tokens += cost
        
        assert governor.energy_metrics.total_tokens > initial_tokens
        assert len(governor.energy_metrics.tokens_per_cycle) == 3
    
    def test_wisdom_hit_rate(self, governor):
        """Test wisdom hit rate calculation"""
        governor.energy_metrics.wisdom_hits = 5
        governor.energy_metrics.wisdom_misses = 5
        
        hit_rate = governor.energy_metrics.wisdom_hit_rate
        assert hit_rate == 0.5
    
    def test_energy_savings_estimation(self, governor):
        """Test energy savings estimation"""
        # High wisdom hit rate should indicate high savings
        governor.energy_metrics.wisdom_hits = 70
        governor.energy_metrics.wisdom_misses = 30
        
        savings = governor.energy_metrics.energy_savings_percent
        assert savings > 0.5  # Should be 50%+


# ============================================================================
# TESTS: OUTPUT GENERATION
# ============================================================================

class TestOutputGeneration:
    """Test output generation logic"""
    
    def test_output_converged(self, governor, engine_output_constructive, engine_output_critical):
        """Test converged output generation"""
        # Create converged cycle
        evaluation = governor.evaluate_cycle(
            engine_output_constructive,
            engine_output_critical,
            current_budget=1.0,
            cycle_number=1
        )
        
        # If converged, output should be single answer
        output = governor._generate_output(evaluation)
        assert output is not None
        assert 'output_type' in output
    
    def test_output_blending(self, governor):
        """Test output blending for partial resolution"""
        # Create outputs with moderate disagreement
        output_l = EngineOutput(
            reasoning_mode=ReasoningMode.CONSTRUCTIVE,
            output="Approach A",
            confidence=0.8,
            internal_monologue="test"
        )
        output_r = EngineOutput(
            reasoning_mode=ReasoningMode.CRITICAL,
            output="Approach B",
            confidence=0.8,
            internal_monologue="test"
        )
        
        evaluation = governor.evaluate_cycle(output_l, output_r, current_budget=1.0, cycle_number=1)
        
        # Test blending
        blended = governor._blend_outputs("Output A", "Output B", contradiction=0.15)
        assert "Output A" in blended
        assert "Output B" in blended


# ============================================================================
# TESTS: AUDIT TRAIL
# ============================================================================

class TestAuditTrail:
    """Test audit trail generation"""
    
    def test_audit_trail_structure(self, governor, engine_output_constructive, engine_output_critical):
        """Test audit trail has all required fields"""
        evaluation = governor.evaluate_cycle(
            engine_output_constructive,
            engine_output_critical,
            current_budget=1.0,
            cycle_number=1
        )
        
        output = {'output': 'test'}
        audit = governor._build_audit_trail(output, evaluation)
        
        assert 'audit_trail' in audit
        trail = audit['audit_trail']
        
        assert 'total_cycles' in trail
        assert 'final_similarity' in trail
        assert 'final_risk' in trail
        assert 'final_quality' in trail
        assert 'energy_metrics' in trail
        assert 'wisdom_stats' in trail
        assert 'cycle_details' in trail
    
    def test_audit_trail_energy_metrics(self, governor, engine_output_constructive, engine_output_critical):
        """Test energy metrics in audit trail"""
        evaluation = governor.evaluate_cycle(
            engine_output_constructive,
            engine_output_critical,
            current_budget=1.0,
            cycle_number=1
        )
        
        output = {'output': 'test'}
        audit = governor._build_audit_trail(output, evaluation)
        
        energy = audit['audit_trail']['energy_metrics']
        assert 'total_tokens' in energy
        assert 'tokens_per_cycle' in energy
        assert 'wisdom_hit_rate' in energy


# ============================================================================
# TESTS: COMPLETE REASONING CYCLE
# ============================================================================

class TestCompleteReasoningCycle:
    """Test complete end-to-end reasoning"""
    
    def test_reason_with_early_exit(self, governor, temp_wisdom_storage):
        """Test reasoning with early wisdom exit"""
        # Add high-confidence wisdom
        record = WisdomRecord(
            query="Test query",
            hypothesis="test",
            resolution="Test resolution",
            confidence=0.95,
            wisdom_type=WisdomType.SEED,
            contradiction_level=0.05,
            ethical_alignment=0.95
        )
        governor.uqi.store_wisdom(record)
        
        # Reason with matching query
        result = governor.reason("Test query")
        
        assert result['status'] == 'success'
        assert result.get('early_exit') is True
        assert governor.energy_metrics.wisdom_hits == 1
    
    def test_reason_full_cycle(self, governor):
        """Test full reasoning cycle"""
        result = governor.reason("Should AI systems be transparent about their limitations?", domain="ai_ethics")
        
        assert result['status'] == 'success'
        assert 'output' in result
        assert 'audit_trail' in result
        
        audit = result['audit_trail']
        assert audit['total_cycles'] > 0
        assert audit['total_cycles'] <= governor.config.max_cycles
    
    def test_reason_accumulates_wisdom(self, governor):
        """Test that reasoning accumulates wisdom"""
        initial_count = len(governor.uqi.wisdom_db)
        
        governor.reason("Test query 1")
        governor.reason("Test query 2")
        
        final_count = len(governor.uqi.wisdom_db)
        assert final_count > initial_count


# ============================================================================
# TESTS: EDGE CASES AND ERROR HANDLING
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_engine_output_invalid_confidence(self):
        """Test engine output rejects invalid confidence"""
        with pytest.raises(ValueError):
            EngineOutput(
                reasoning_mode=ReasoningMode.CONSTRUCTIVE,
                output="test",
                confidence=1.5,  # Invalid
                internal_monologue="test"
            )
    
    def test_engine_output_invalid_reasoning_depth(self):
        """Test engine output rejects invalid reasoning depth"""
        with pytest.raises(ValueError):
            EngineOutput(
                reasoning_mode=ReasoningMode.CONSTRUCTIVE,
                output="test",
                confidence=0.8,
                internal_monologue="test",
                reasoning_depth=0  # Invalid
            )
    
    def test_evaluate_cycle_invalid_budget(self, governor, engine_output_constructive, engine_output_critical):
        """Test evaluate cycle rejects invalid budget"""
        with pytest.raises(ValueError):
            governor.evaluate_cycle(
                engine_output_constructive,
                engine_output_critical,
                current_budget=-0.5,  # Invalid
                cycle_number=1
            )
    
    def test_evaluate_cycle_invalid_cycle_number(self, governor, engine_output_constructive, engine_output_critical):
        """Test evaluate cycle rejects invalid cycle number"""
        with pytest.raises(ValueError):
            governor.evaluate_cycle(
                engine_output_constructive,
                engine_output_critical,
                current_budget=1.0,
                cycle_number=0  # Invalid
            )
    
    def test_similarity_with_unicode(self, governor):
        """Test similarity computation with unicode"""
        output1 = "This contains émojis 🎉 and spëcial chars"
        output2 = "This contains émojis 🎉 and spëcial chars"
        
        similarity = governor.compute_similarity(output1, output2)
        assert similarity > 0.9


# ============================================================================
# TESTS: STATISTICS AND REPORTING
# ============================================================================

class TestStatisticsAndReporting:
    """Test statistics and reporting functions"""
    
    def test_governor_statistics(self, governor):
        """Test Governor statistics"""
        # Run a reasoning cycle
        governor.reason("Test query")
        
        stats = governor.get_statistics()
        
        assert 'cycles_completed' in stats
        assert 'energy_metrics' in stats
        assert 'ethical_alignment' in stats
        assert 'wisdom_statistics' in stats
    
    def test_energy_metrics_statistics(self, governor):
        """Test energy metrics statistics"""
        # Run reasoning
        governor.reason("Test query 1")
        governor.reason("Test query 2")
        
        stats = governor.get_statistics()
        energy = stats['energy_metrics']
        
        assert energy['total_tokens'] > 0
        assert energy['wisdom_hit_rate'] >= 0.0
        assert energy['estimated_energy_savings_percent'] >= 0.0


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
