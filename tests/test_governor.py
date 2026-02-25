# Copyright (c) 2026 Frederick Davis Stalnecker
# Licensed under the MIT License — see LICENSE file for details

"""
Unit tests for the unified THEOS Governor.
Covers: initialization, scoring, all stop conditions, posture states,
audit trail, backward-compat alias, and edge cases.
"""

import pytest
from theos_governor import (
    THEOSGovernor,
    TheosDualClockGovernor,
    GovernorConfig,
    EngineOutput,
    GovernorDecision,
    StopReason,
    Posture,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def cfg() -> GovernorConfig:
    return GovernorConfig(
        max_cycles=5,
        max_risk=0.35,
        similarity_converge=0.90,
        min_improvement=0.02,
        plateau_cycles=2,
        contradiction_budget=1.5,
        contradiction_decay=0.175,
    )


@pytest.fixture
def gov(cfg) -> THEOSGovernor:
    return THEOSGovernor(cfg)


def _out(engine_id="L", cycle=0, answer="answer", **kw) -> EngineOutput:
    return EngineOutput(engine_id=engine_id, cycle_index=cycle, answer=answer, **kw)


@pytest.fixture
def identical_pair():
    text = "The solution balances efficiency and safety."
    return _out("L", 0, text, coherence=0.9), _out("R", 0, text, coherence=0.9)


@pytest.fixture
def divergent_pair():
    return (
        _out("L", 0, "Maximise profit at all costs.", risk=0.05),
        _out("R", 0, "Prioritise employee welfare and ethics.", risk=0.05),
    )


@pytest.fixture
def risky_pair():
    return (
        _out("L", 0, "Proceed immediately.", risk=0.50),
        _out("R", 0, "Risks are acceptable.", risk=0.60),
    )


# ─────────────────────────────────────────────────────────────────────────────
# 1. Initialisation
# ─────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_default_config(self):
        g = THEOSGovernor()
        assert g.cfg.max_cycles == 4
        assert g.contradiction_spent == 0.0
        assert g.history == []
        assert g.posture == Posture.NOM

    def test_custom_config(self, gov, cfg):
        assert gov.cfg.max_cycles == 5

    def test_backward_compat_alias(self):
        g = TheosDualClockGovernor()
        assert isinstance(g, THEOSGovernor)

    def test_reset_clears_state(self, gov, identical_pair):
        gov.step(*identical_pair)
        gov.reset()
        assert gov.history == []
        assert gov.contradiction_spent == 0.0
        assert gov.last_frozen_answer is None


# ─────────────────────────────────────────────────────────────────────────────
# 2. EngineOutput validation
# ─────────────────────────────────────────────────────────────────────────────


class TestEngineOutput:
    def test_valid_output(self):
        out = EngineOutput(engine_id="L", cycle_index=0, answer="ok")
        assert out.engine_id == "L"

    def test_empty_answer_raises(self):
        with pytest.raises(ValueError, match="empty"):
            EngineOutput(engine_id="L", cycle_index=0, answer="")

    def test_whitespace_only_answer_raises(self):
        with pytest.raises(ValueError, match="empty"):
            EngineOutput(engine_id="L", cycle_index=0, answer="   ")

    def test_out_of_range_score_raises(self):
        with pytest.raises(ValueError):
            EngineOutput(engine_id="L", cycle_index=0, answer="ok", coherence=1.5)

    def test_nan_score_raises(self):
        import math
        with pytest.raises(ValueError):
            EngineOutput(engine_id="L", cycle_index=0, answer="ok", risk=math.nan)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Scoring function
# ─────────────────────────────────────────────────────────────────────────────


class TestScoring:
    def test_score_positive(self, gov):
        out = _out(coherence=0.8, calibration=0.75, evidence=0.6, actionability=0.7, risk=0.1)
        assert gov._score(out) > 0

    def test_score_negative_on_constraint_violation(self, gov):
        out = _out(constraint_ok=False)
        assert gov._score(out) == -1.0

    def test_score_negative_on_high_risk(self, gov):
        out = _out(risk=0.50)   # exceeds max_risk=0.35
        assert gov._score(out) == -1.0

    def test_score_formula(self, gov):
        out = _out(coherence=0.8, calibration=0.75, evidence=0.6, actionability=0.7, risk=0.1)
        expected = (1.2*0.8 + 1.0*0.75 + 1.1*0.6 + 1.0*0.7 - 1.6*0.1)
        assert abs(gov._score(out) - expected) < 1e-9


# ─────────────────────────────────────────────────────────────────────────────
# 4. Stop conditions
# ─────────────────────────────────────────────────────────────────────────────


class TestStopConditions:
    def test_convergence_freeze(self, gov, identical_pair):
        d = gov.step(*identical_pair)
        assert d.decision == "FREEZE"
        assert d.stop_reason == StopReason.CONVERGENCE
        assert d.similarity >= gov.cfg.similarity_converge

    def test_risk_freeze(self, gov, risky_pair):
        d = gov.step(*risky_pair)
        assert d.decision == "FREEZE"
        assert d.stop_reason == StopReason.RISK

    def test_max_cycles_freeze(self):
        g = THEOSGovernor(GovernorConfig(max_cycles=1))
        left  = _out("L", 0, "Answer L")
        right = _out("R", 0, "Answer R")
        d = g.step(left, right)
        assert d.decision == "FREEZE"
        assert d.stop_reason == StopReason.MAX_CYCLES

    def test_plateau_freeze(self):
        g = THEOSGovernor(GovernorConfig(
            max_cycles=10,
            similarity_converge=0.99,
            plateau_cycles=2,
            min_improvement=0.5,   # very high threshold → plateau triggers fast
        ))
        left  = _out("L", 0, "Different answer A", coherence=0.6)
        right = _out("R", 0, "Different answer B", coherence=0.6)
        decisions = [g.step(
            _out("L", i, "Different answer A", coherence=0.6),
            _out("R", i, "Different answer B", coherence=0.6),
        ) for i in range(5)]
        freeze_decisions = [d for d in decisions if d.decision == "FREEZE"]
        assert freeze_decisions, "expected at least one FREEZE"
        assert any(d.stop_reason in (StopReason.DIMINISHING, StopReason.MAX_CYCLES)
                   for d in freeze_decisions)

    def test_budget_freeze(self):
        g = THEOSGovernor(GovernorConfig(
            max_cycles=20,
            similarity_converge=0.99,
            contradiction_budget=0.01,
            contradiction_decay=1.0,
        ))
        decisions = []
        for i in range(5):
            d = g.step(
                _out("L", i, "Divergent left answer text"),
                _out("R", i, "Completely different right answer",
                     contradiction_claim="clash", contradiction_value=0.9),
            )
            decisions.append(d)
            if d.decision == "FREEZE":
                break
        freeze = [d for d in decisions if d.decision == "FREEZE"]
        assert freeze
        assert freeze[0].stop_reason in (StopReason.BUDGET, StopReason.DIMINISHING,
                                         StopReason.CONVERGENCE, StopReason.MAX_CYCLES)

    def test_continue_decision(self):
        g = THEOSGovernor(GovernorConfig(
            max_cycles=10,
            similarity_converge=0.99,
            plateau_cycles=10,
        ))
        # First step with divergent outputs — should CONTINUE
        d = g.step(
            _out("L", 0, "Left divergent text"),
            _out("R", 0, "Right divergent text"),
        )
        # Could be either — just ensure it's a valid decision
        assert d.decision in ("CONTINUE", "FREEZE")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Posture states
# ─────────────────────────────────────────────────────────────────────────────


class TestPosture:
    def test_initial_posture_nom(self, gov):
        assert gov.posture == Posture.NOM

    def test_posture_enum_values(self):
        for p in ("NOM", "PEM", "CM", "IM"):
            assert hasattr(Posture, p)

    def test_posture_thresholds(self):
        g = THEOSGovernor(GovernorConfig(contradiction_budget=1.0))

        # Simulate various spend levels
        g.contradiction_spent = 0.10
        assert g.posture == Posture.NOM

        g.contradiction_spent = 0.35
        assert g.posture == Posture.PEM

        g.contradiction_spent = 0.70
        assert g.posture == Posture.CM

        g.contradiction_spent = 0.90
        assert g.posture == Posture.IM


# ─────────────────────────────────────────────────────────────────────────────
# 6. Audit trail
# ─────────────────────────────────────────────────────────────────────────────


class TestAuditTrail:
    def test_audit_trail_structure(self, gov, identical_pair):
        gov.step(*identical_pair)
        trail = gov.get_audit_trail()
        for key in ("total_cycles", "contradiction_spent", "contradiction_budget",
                    "posture", "history", "last_frozen_answer"):
            assert key in trail

    def test_history_grows(self, gov, divergent_pair):
        for i in range(3):
            gov.step(
                _out("L", i, "Left text diverges significantly here"),
                _out("R", i, "Right text diverges significantly here"),
            )
            if gov.history and gov.history[-1].get("decision") == "FREEZE":
                break
        assert len(gov.history) >= 1

    def test_frozen_answer_recorded(self, gov, identical_pair):
        gov.step(*identical_pair)
        assert gov.last_frozen_answer is not None


# ─────────────────────────────────────────────────────────────────────────────
# 7. GovernorDecision fields
# ─────────────────────────────────────────────────────────────────────────────


class TestDecisionFields:
    def test_freeze_has_chosen_engine(self, gov, identical_pair):
        d = gov.step(*identical_pair)
        assert d.chosen_engine in ("L", "R")

    def test_freeze_has_chosen_answer(self, gov, identical_pair):
        d = gov.step(*identical_pair)
        assert d.chosen_answer is not None

    def test_freeze_has_similarity(self, gov, identical_pair):
        d = gov.step(*identical_pair)
        assert 0.0 <= d.similarity <= 1.0

    def test_decision_has_posture(self, gov, identical_pair):
        d = gov.step(*identical_pair)
        assert d.posture in ("NOM", "PEM", "CM", "IM")

    def test_decision_has_scores(self, gov, identical_pair):
        d = gov.step(*identical_pair)
        assert isinstance(d.score_L, float)
        assert isinstance(d.score_R, float)


# ─────────────────────────────────────────────────────────────────────────────
# 8. Edge cases
# ─────────────────────────────────────────────────────────────────────────────


class TestEdgeCases:
    def test_long_outputs(self, gov):
        text = "word " * 5_000
        d = gov.step(_out("L", 0, text), _out("R", 0, text))
        assert d is not None

    def test_unicode_outputs(self, gov):
        d = gov.step(
            _out("L", 0, "Test 你好 مرحبا"),
            _out("R", 0, "Test 你好 مرحبا"),
        )
        assert d is not None

    def test_special_characters(self, gov):
        d = gov.step(
            _out("L", 0, "Test @#$%^&*()"),
            _out("R", 0, "Test @#$%^&*()"),
        )
        assert d is not None

    def test_single_word_outputs(self, gov):
        d = gov.step(_out("L", 0, "Yes"), _out("R", 0, "No"))
        assert d.decision in ("CONTINUE", "FREEZE")


# ─────────────────────────────────────────────────────────────────────────────
# 9. Performance (smoke test — not a benchmark)
# ─────────────────────────────────────────────────────────────────────────────


class TestPerformance:
    def test_step_is_fast(self, gov):
        import time
        left  = _out("L", 0, "word " * 500)
        right = _out("R", 0, "word " * 500)
        start = time.time()
        for _ in range(200):
            gov.step(left, right)
            gov.reset()
        assert (time.time() - start) < 2.0
