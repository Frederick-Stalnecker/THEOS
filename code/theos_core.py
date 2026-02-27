#!/usr/bin/env python3
"""
THEOS Core — Dual-Engine Contractive Reasoning with Per-Engine Self-Reflection
==============================================================================

WHAT THEOS IS
-------------
THEOS implements a governed dual-engine reasoning loop where two opposing engines
each privately reflect on their own thinking before their conclusions are pressed
together by a contradiction measurement — the "wringer." The governor decides
how many wringer passes are needed for the best answer.

THE ARCHITECTURE — visually:

  ┌──────────────────────────────────────────────────────────────────────┐
  │  LEFT ENGINE  (clockwise — constructive)                              │
  │                                                                       │
  │    Inner pass 1:  I ──────────→ A_L ──────────→ D_L                  │
  │                   ↑                                ↓                  │
  │    Inner pass 2:  I(D_L) ──────→ A_L ──────────→ D_L*  ← final      │
  │                   └──── engine reflects on its own prior D ────┘      │
  └─────────────────────────────────────────┬────────────────────────────┘
                                            │ D_L*  (self-reflected)
                              ══════════════╪══════════════  THE WRINGER
                                            │ D_R*  (self-reflected)
  ┌─────────────────────────────────────────┴────────────────────────────┐
  │  RIGHT ENGINE  (counterclockwise — adversarial)                       │
  │                                                                       │
  │    Inner pass 1:  I ──────────→ A_R ──────────→ D_R                  │
  │                   ↑                                ↓                  │
  │    Inner pass 2:  I(D_R) ──────→ A_R ──────────→ D_R*  ← final      │
  │                   └──── engine reflects on its own prior D ────┘      │
  └──────────────────────────────────────────────────────────────────────┘

  WRINGER:   Φ = Contradiction(D_L*, D_R*)
             Presses the two self-reflected conclusions together.
             Contradiction is not an error — it is information.
             Like a steel-mill wringer pressing molten rod into plate,
             it squeezes out excess and refines toward truth.

  GOVERNOR:  Checks 4 halting criteria after each wringer pass.
             Decides whether another pass adds value or the answer is ready.
             Prevents both under-reasoning and over-nuancing.

  WISDOM:    After each wringer pass, a compressed lesson is deposited into W.
             This is the accumulated meta-past: distilled experience that
             sharpens how both engines form hypotheses in future queries.
             Wisdom feeds into abduction — not just retrieval, but bias.

WHY THIS IS NOVEL
-----------------
Every existing AI system makes one forward pass and returns the result. It has
no memory of having reasoned. It produces output the way a calculator produces
a sum — without reflection.

THEOS does something architecturally different:

1. PER-ENGINE SELF-REFLECTION
   Each engine completes a first I→A→D pass (its "first thought"), then feeds
   its own deduction D back into its private induction I for a second pass —
   producing a conclusion that reasons about its own prior conclusion.
   This is second-order cognition: thought about thought.
   Each engine has a "momentary past" — a lived record of having just thought
   something — which it examines and refines before committing to an answer.

2. GENUINELY OPPOSING ENGINES
   Left engine runs clockwise: constructive, forward, building toward the best
   coherent answer. Right engine runs counterclockwise: adversarial, probing
   weaknesses, generating systematic opposition. These are not two prompts to
   the same model — they are two genuinely different epistemic stances.

3. THE WRINGER
   Both engines self-reflect independently. Only then are their conclusions
   pressed together. The wringer measures the productive contradiction between
   two self-aware conclusions, not between two raw first-pass outputs.

4. GOVERNED CONVERGENCE
   The governor measures whether another wringer pass adds information (via the
   information gain ratio) or whether contradiction has reached an irreducible
   minimum. This is not a fixed-cycle system — it halts when the answer is ready.

5. WISDOM AS ACCUMULATED META-PAST
   Each wringer pass's compressed lesson becomes a prior for future abduction.
   The wisdom register W is not a log — it is distilled understanding.
   Across billions of cycles, W becomes a self-improving model of how to reason.

FORMAL SPECIFICATION
--------------------
State space:  S = I × A × D × Φ × W   (complete metric space, product metric)
Fixed point:  S*(q) — unique epistemic equilibrium per query q
Convergence:  ||S_n - S*(q)|| ≤ ρⁿ · ||S₀ - S*(q)||  (geometric, Banach)

Operators (ALL injected — THEOS is domain-agnostic):
  σ_I(O, Φ_prev, D_own):  Induction
      O      = fixed observation (encoded query)
      Φ_prev = contradiction from previous wringer pass (feedback)
      D_own  = engine's own prior D (None on first inner pass, D₁ on second)
               This is the self-reflection argument — the "momentary past"

  σ_A^L(I, W):  Constructive abduction (clockwise)
  σ_A^R(I, W):  Adversarial abduction (counterclockwise)
  σ_D(A):       Deduction (shared between engines)
  Contr(D_L, D_R): Contradiction measurement — the wringer
  Upd_W(W, q, D, conf): Wisdom update — meta-past accumulation

Output rule (governor, at halting wringer pass N):
  Φ_N < ε₁:          output D_L*  (engines converged — left wins)
  ε₁ ≤ Φ_N < ε₂:    output w_L·D_L* + w_R·D_R*
                          w_L = (1 - Φ_N/ε₂) / 2   (left weight falls)
                          w_R = (1 + Φ_N/ε₂) / 2   (right weight rises)
                          Critical engine gains authority as contradiction grows.
  Φ_N ≥ ε₂:          expose (D_L*, D_R*, Φ_N) — irresolvable disagreement

HALTING CRITERIA (governor checks all four each wringer pass):
  1. Convergence:           Φ < ε_converge
  2. Diminishing returns:   IG_ratio < ρ_min
  3. Budget exhaustion:     wringer_pass ≥ max_wringer_passes
  4. Irreducible uncertainty: entropy < entropy_min AND Φ > delta_min

HOW TO USE (open-source integration)
-------------------------------------
1. Implement the 10 operator functions for your domain.
   The key function is induce_patterns(obs, prev_phi, prev_own_deduction):
     - obs:               your encoded observation (from encode_observation)
     - prev_phi:          contradiction from last wringer pass (float)
     - prev_own_deduction: this engine's own D from its last inner pass
                           (None on first pass — no prior yet)
                           Use this to make your engine reason about its
                           own prior conclusion. This is what makes THEOS
                           different from every other reasoning system.

2. Instantiate TheosConfig with your thresholds.
3. Instantiate TheosCore with your callables.
4. Call run_query(query) to run governed dual-engine reasoning.

PATENT: USPTO #63/831,738
AUTHOR: Frederick Davis Stalnecker
"""

import inspect
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

# ============================================================================
# Type Aliases — What flows through the THEOS cycle
# ============================================================================

PatternI = Any  # Inductive pattern: output of σ_I
HypothesisA = Any  # Abductive hypothesis: output of σ_A^L or σ_A^R
DeductionD = Any  # Deductive conclusion: output of σ_D
ContradictionF = float  # Wringer measurement: output of Contr(D_L, D_R)
WisdomEntry = dict[str, Any]
WisdomStore = list[WisdomEntry]


# ============================================================================
# Named Tuples — Grouping callables for clean construction
# ============================================================================


@dataclass
class AbductionEngines:
    """
    The two opposing abduction engines.

    abduce_left  — constructive (clockwise). Builds toward the best coherent answer.
    abduce_right — adversarial (counterclockwise). Systematically stresses and opposes.

    Both have signature: (pattern_I: PatternI, wisdom_slice: WisdomStore) -> HypothesisA
    """

    abduce_left: Callable[[PatternI, WisdomStore], HypothesisA]
    abduce_right: Callable[[PatternI, WisdomStore], HypothesisA]


@dataclass
class DeductionEngine:
    """
    The shared deduction operator σ_D.

    Shared between both engines — the clockwise/counterclockwise distinction
    lives entirely in abduction, not deduction.

    Signature: (hypothesis: HypothesisA) -> DeductionD
    """

    deduce: Callable[[HypothesisA], DeductionD]


# ============================================================================
# Configuration
# ============================================================================


@dataclass
class TheosConfig:
    """
    Configuration for the THEOS governor.

    max_wringer_passes:     Maximum outer cycles. The governor checks halting
                            criteria after each pass and may stop earlier.
                            This bounds the total reasoning budget.

    engine_reflection_depth: How many inner self-reflection passes each engine
                            performs before the wringer runs. Default is 2:
                              Pass 1 = first thought (I → A → D)
                              Pass 2 = reflection on that thought (I(D₁) → A → D₂)
                            Set to 1 for single-pass engines (no self-reflection).
                            Set higher for deeper per-engine introspection.

    eps_converge:   Contradiction threshold below which engines have converged.
                    Output is D_L* directly. w_L = 1, w_R = 0.

    eps_partial:    Contradiction threshold below which a blended output is used.
                    The wringer produces w_L·D_L* + w_R·D_R* with weights above.

    rho_min:        Minimum information gain ratio. If IG_n / IG_{n-1} < rho_min,
                    the wringer has hit diminishing returns — halt.

    entropy_min:    Minimum hypothesis entropy. If entropy drops below this AND
                    contradiction stays above delta_min, uncertainty is irreducible.

    delta_min:      Contradiction threshold for irreducible uncertainty check.

    similarity_threshold: Minimum similarity for wisdom retrieval.

    budget:         Optional resource budget (None = unlimited).
    """

    max_wringer_passes: int = 7
    engine_reflection_depth: int = 2
    eps_converge: float = 0.05
    eps_partial: float = 0.5
    rho_min: float = 0.4
    entropy_min: float = 0.15
    delta_min: float = 0.4
    similarity_threshold: float = 0.7
    budget: float | None = None
    verbose: bool = False

    # ── Backward-compatibility alias ─────────────────────────────────────────
    @property
    def max_cycles(self) -> int:
        """Alias for max_wringer_passes (legacy name)."""
        return self.max_wringer_passes

    @max_cycles.setter
    def max_cycles(self, value: int):
        self.max_wringer_passes = value


# ── Legacy construction support: TheosConfig(max_cycles=N) ──────────────────
_original_theos_config_init = TheosConfig.__init__


def _theos_config_init_with_alias(
    self,
    max_wringer_passes=7,
    engine_reflection_depth=2,
    eps_converge=0.05,
    eps_partial=0.5,
    rho_min=0.4,
    entropy_min=0.15,
    delta_min=0.4,
    similarity_threshold=0.7,
    budget=None,
    verbose=False,
    max_cycles=None,
):
    self.max_wringer_passes = max_cycles if max_cycles is not None else max_wringer_passes
    self.engine_reflection_depth = engine_reflection_depth
    self.eps_converge = eps_converge
    self.eps_partial = eps_partial
    self.rho_min = rho_min
    self.entropy_min = entropy_min
    self.delta_min = delta_min
    self.similarity_threshold = similarity_threshold
    self.budget = budget
    self.verbose = verbose


TheosConfig.__init__ = _theos_config_init_with_alias  # type: ignore[method-assign]


# ============================================================================
# Trace Data Structures
# ============================================================================


@dataclass
class InnerPassTrace:
    """
    Record of one inner self-reflection pass within a single engine.

    pass_num = 0  → first thought  (I → A → D, no prior)
    pass_num = 1  → self-reflection (I(D₀) → A → D₁, using own prior D)
    pass_num > 1  → deeper introspection (uncommon, engine_reflection_depth > 2)
    """

    pass_num: int
    pattern_I: Any  # Inductive pattern this pass used
    hypothesis: Any  # Abductive hypothesis generated
    deduction: Any  # Deductive conclusion reached
    used_own_prior: bool  # True if this pass used the engine's own prior D


@dataclass
class WringerPassTrace:
    """
    Record of one complete wringer pass.

    Contains:
    - Each engine's full inner self-reflection trace
    - The final self-reflected outputs D_L* and D_R*
    - The wringer's contradiction measurement Φ
    - The governor's halt decision (if any)
    """

    wringer_pass: int
    left_inner_passes: list[InnerPassTrace]  # Left engine's self-reflection trace
    right_inner_passes: list[InnerPassTrace]  # Right engine's self-reflection trace
    deduction_L: Any  # D_L*: left engine's final self-reflected output
    deduction_R: Any  # D_R*: right engine's final self-reflected output
    contradiction: float  # Φ = Contr(D_L*, D_R*)
    entropy: float  # Entropy of hypothesis space (A_L, A_R)
    info_gain_ratio: float
    halt_reason: Optional["HaltReason"] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# Backward-compatibility alias
CycleTrace = WringerPassTrace


# ============================================================================
# Halt Reasons
# ============================================================================


class HaltReason(Enum):
    """Why the governor stopped the wringer."""

    CONVERGENCE = "convergence"  # Φ < ε_converge
    DIMINISHING_RETURNS = "diminishing_returns"  # IG ratio < ρ_min
    BUDGET_EXHAUSTION = "budget_exhaustion"  # pass ≥ max or budget
    IRREDUCIBLE_UNCERTAINTY = "irreducible_uncertainty"  # entropy low, Φ high
    MAX_CYCLES = "max_cycles"  # hit max_wringer_passes
    UNKNOWN = "unknown"


# ============================================================================
# Output
# ============================================================================


@dataclass
class TheosOutput:
    """
    Final output from a THEOS reasoning run.

    output:       The answer. Type depends on output_type:
                    "convergence"  → D_L* directly (engines agreed)
                    "blend"        → w_L·D_L* + w_R·D_R* or structured blend dict
                    "disagreement" → {"type": "disagreement", "left": ..., "right": ...}

    output_type:  "convergence" | "blend" | "disagreement"

    confidence:   [0, 1] scalar. Higher = more certain.
                    convergence:   1 - Φ/ε_converge  (1.0 at perfect agreement)
                    blend:         1 - (Φ/ε_partial) * 0.5
                    disagreement:  0.5

    contradiction: Φ at the halting wringer pass.

    wringer_passes_used: How many outer cycles the governor ran.

    trace:        Full record of every wringer pass and inner self-reflection pass.
    """

    output: Any
    output_type: str
    confidence: float
    contradiction: float
    wringer_passes_used: int
    halt_reason: HaltReason
    trace: list[WringerPassTrace]
    wisdom_updated: bool

    @property
    def cycles_used(self) -> int:
        """Backward-compatible alias for wringer_passes_used."""
        return self.wringer_passes_used


# ============================================================================
# THEOS Core
# ============================================================================


class TheosCore:
    """
    The THEOS reasoning engine.

    Implements the governed dual-engine I→A→D→I cycle with per-engine
    self-reflection (the "wringer" architecture).

    All domain logic is injected as callables. TheosCore is domain-agnostic —
    it provides the governance structure; you provide the reasoning content.

    Constructor accepts either separate callables or the AbductionEngines /
    DeductionEngine named tuples (both styles work):

        # Style 1 — named tuples (matches formal spec toy demo):
        TheosCore(
            config=cfg,
            encode_observation=my_encode,
            induce_patterns=my_induce,
            abduction_engines=AbductionEngines(abduce_left=..., abduce_right=...),
            deduction_engine=DeductionEngine(deduce=...),
            measure_contradiction=my_contradiction,
            retrieve_wisdom=my_retrieve,
            update_wisdom=my_update,
            estimate_entropy=my_entropy,
            estimate_info_gain=my_ig,
        )

        # Style 2 — flat callables (original API):
        TheosCore(
            config=cfg,
            encode_observation=my_encode,
            induce_patterns=my_induce,
            abduce_left=..., abduce_right=..., deduce=...,
            measure_contradiction=my_contradiction,
            ...
        )

    THE KEY CALLABLE: induce_patterns
    ---------------------------------
    Signature:  (obs, prev_phi, prev_own_deduction) -> PatternI

        obs:                 the encoded observation (fixed for the query)
        prev_phi:            contradiction Φ from the previous wringer pass
        prev_own_deduction:  THIS engine's own D from its previous inner pass.
                             On the first inner pass this is None.
                             On the second inner pass this is D from pass 1.
                             THIS IS THE SELF-REFLECTION ARGUMENT.
                             Use it to make the engine reason about its own
                             prior conclusion — the "momentary past."

    If your induce_patterns only accepts 2 arguments (obs, prev_phi), it still
    works — THEOS detects this and calls it without the third argument. You
    lose the per-engine self-reflection but everything else functions normally.
    """

    def __init__(
        self,
        config: TheosConfig,
        encode_observation: Callable[[str, Any], Any],
        induce_patterns: Callable,
        measure_contradiction: Callable[[DeductionD, DeductionD], float],
        retrieve_wisdom: Callable[[str, WisdomStore, float], WisdomStore],
        update_wisdom: Callable[[WisdomStore, str, Any, float], WisdomStore],
        estimate_entropy: Callable[[tuple[HypothesisA, HypothesisA]], float],
        estimate_info_gain: Callable[[float, float], float],
        # Named-tuple style
        abduction_engines: AbductionEngines | None = None,
        deduction_engine: DeductionEngine | None = None,
        # Flat-callable style
        abduce_left: Callable | None = None,
        abduce_right: Callable | None = None,
        deduce: Callable | None = None,
    ):
        self.config = config

        # Resolve abduction engines (accept either style)
        if abduction_engines is not None:
            self.abduce_left = abduction_engines.abduce_left
            self.abduce_right = abduction_engines.abduce_right
        elif abduce_left is not None and abduce_right is not None:
            self.abduce_left = abduce_left
            self.abduce_right = abduce_right
        else:
            raise ValueError(
                "Provide either abduction_engines=AbductionEngines(...) "
                "or abduce_left=... and abduce_right=... separately."
            )

        # Resolve deduction engine (accept either style)
        if deduction_engine is not None:
            self.deduce = deduction_engine.deduce
        elif deduce is not None:
            self.deduce = deduce
        else:
            raise ValueError("Provide either deduction_engine=DeductionEngine(...) or deduce=...")

        self.encode_observation = encode_observation
        self.induce_patterns = induce_patterns
        self.measure_contradiction = measure_contradiction
        self.retrieve_wisdom = retrieve_wisdom
        self.update_wisdom = update_wisdom
        self.estimate_entropy = estimate_entropy
        self.estimate_info_gain = estimate_info_gain

        # Detect whether induce_patterns accepts the self-reflection argument.
        # Legacy implementations take (obs, prev_phi) — 2 params.
        # New implementations take (obs, prev_phi, prev_own_deduction) — 3 params.
        try:
            sig = inspect.signature(induce_patterns)
            len([p for p in sig.parameters.values() if p.default is inspect.Parameter.empty])
            total_params = len(sig.parameters)
            self._induce_accepts_own_prior = total_params >= 3
        except (ValueError, TypeError):
            self._induce_accepts_own_prior = False

        self.wisdom: WisdomStore = []
        self.cycle_count = 0

    # ── Private: call induction with or without self-reflection arg ──────────

    def _induce(
        self,
        observation: Any,
        prev_contradiction: float,
        prev_own_deduction: Any | None,
    ) -> PatternI:
        """
        Call σ_I with optional self-reflection argument.

        If induce_patterns accepts 3 args: pass prev_own_deduction (may be None).
        If induce_patterns accepts 2 args: call without it (legacy compatibility).
        """
        if self._induce_accepts_own_prior:
            return self.induce_patterns(observation, prev_contradiction, prev_own_deduction)
        else:
            return self.induce_patterns(observation, prev_contradiction)

    # ── Main reasoning loop ──────────────────────────────────────────────────

    def run_query(
        self,
        query: str,
        context: Any | None = None,
    ) -> TheosOutput:
        """
        Run the governed dual-engine wringer for a query.

        Each outer iteration is one "wringer pass":
          1. Left engine runs engine_reflection_depth inner passes (self-reflection).
          2. Right engine runs engine_reflection_depth inner passes (self-reflection).
          3. Wringer measures contradiction between the two self-reflected outputs.
          4. Governor checks halting criteria.
          5. If continuing: update prev_contradiction and repeat.
          6. At halt: generate output, update wisdom, return.

        Returns TheosOutput with the final answer, confidence, contradiction,
        halt reason, and full trace of every wringer pass and inner pass.
        """
        observation = self.encode_observation(query, context)
        trace: list[WringerPassTrace] = []
        prev_contradiction = 0.0

        # These hold the last cycle's final deductions — used only if the loop
        # exits via max_wringer_passes without an explicit halt signal.
        deduction_L: Any = None
        deduction_R: Any = None
        hypothesis_L: Any = None
        hypothesis_R: Any = None
        contradiction = 0.0
        entropy = 0.0

        for wringer_pass in range(self.config.max_wringer_passes):

            wisdom_slice = self.retrieve_wisdom(
                query, self.wisdom, self.config.similarity_threshold
            )

            # ─────────────────────────────────────────────────────────────────
            # LEFT ENGINE — Clockwise self-reflection
            #
            # Inner pass 0: first thought — no prior of own D
            # Inner pass 1: reflection   — own D from pass 0 feeds back into I
            # Inner pass n: deeper       — own D from pass n-1 feeds back into I
            #
            # The engine's prior D is PRIVATE: it does not influence the right
            # engine's induction. Each engine has its own "momentary past."
            # ─────────────────────────────────────────────────────────────────
            own_D_L: Any | None = None
            left_inner_traces: list[InnerPassTrace] = []

            for inner in range(self.config.engine_reflection_depth):
                I_L = self._induce(observation, prev_contradiction, own_D_L)
                A_L = self.abduce_left(I_L, wisdom_slice)
                D_L = self.deduce(A_L)

                left_inner_traces.append(
                    InnerPassTrace(
                        pass_num=inner,
                        pattern_I=I_L,
                        hypothesis=A_L,
                        deduction=D_L,
                        used_own_prior=(own_D_L is not None),
                    )
                )

                own_D_L = D_L  # ← this engine's D feeds back into its own next I

            deduction_L = own_D_L  # D_L* — final self-reflected left conclusion
            hypothesis_L = A_L  # final A_L for entropy

            # ─────────────────────────────────────────────────────────────────
            # RIGHT ENGINE — Counterclockwise self-reflection
            #
            # Identical structure to the left engine, but adversarial abduction.
            # The right engine's prior D is also private — it does not influence
            # the left engine's induction. Both engines self-reflect independently.
            # ─────────────────────────────────────────────────────────────────
            own_D_R: Any | None = None
            right_inner_traces: list[InnerPassTrace] = []

            for inner in range(self.config.engine_reflection_depth):
                I_R = self._induce(observation, prev_contradiction, own_D_R)
                A_R = self.abduce_right(I_R, wisdom_slice)
                D_R = self.deduce(A_R)

                right_inner_traces.append(
                    InnerPassTrace(
                        pass_num=inner,
                        pattern_I=I_R,
                        hypothesis=A_R,
                        deduction=D_R,
                        used_own_prior=(own_D_R is not None),
                    )
                )

                own_D_R = D_R  # ← this engine's D feeds back into its own next I

            deduction_R = own_D_R  # D_R* — final self-reflected right conclusion
            hypothesis_R = A_R  # final A_R for entropy

            # ─────────────────────────────────────────────────────────────────
            # THE WRINGER
            #
            # Both engines have self-reflected. Now press their conclusions
            # together. Φ = Contradiction(D_L*, D_R*).
            #
            # Φ is not a failure signal — it is the productive disagreement
            # between two self-aware minds. The governor decides what to do with it.
            # ─────────────────────────────────────────────────────────────────
            contradiction = self.measure_contradiction(deduction_L, deduction_R)
            entropy = self.estimate_entropy((hypothesis_L, hypothesis_R))
            info_gain_ratio = self.estimate_info_gain(contradiction, prev_contradiction)

            # Record this full wringer pass
            wringer_trace = WringerPassTrace(
                wringer_pass=wringer_pass,
                left_inner_passes=left_inner_traces,
                right_inner_passes=right_inner_traces,
                deduction_L=deduction_L,
                deduction_R=deduction_R,
                contradiction=contradiction,
                entropy=entropy,
                info_gain_ratio=info_gain_ratio,
            )
            trace.append(wringer_trace)

            if self.config.verbose:
                print(
                    f"[THEOS] Wringer pass {wringer_pass}: "
                    f"Φ={contradiction:.4f}  H={entropy:.4f}  IG={info_gain_ratio:.4f}"
                )

            # ─────────────────────────────────────────────────────────────────
            # GOVERNOR — Check all four halting criteria
            # ─────────────────────────────────────────────────────────────────
            halt_reason = self._check_halt_criteria(
                wringer_pass, contradiction, info_gain_ratio, entropy
            )

            if halt_reason is not None:
                wringer_trace.halt_reason = halt_reason
                return self._finalize(
                    query,
                    deduction_L,
                    deduction_R,
                    contradiction,
                    entropy,
                    wringer_pass + 1,
                    halt_reason,
                    trace,
                )

            # Wringer Φ feeds into both engines' induction next pass
            prev_contradiction = contradiction

        # Max wringer passes reached — governor's final budget exhausted
        return self._finalize(
            query,
            deduction_L,
            deduction_R,
            contradiction,
            entropy,
            self.config.max_wringer_passes,
            HaltReason.MAX_CYCLES,
            trace,
        )

    # ── Governor: halting criteria ───────────────────────────────────────────

    def _check_halt_criteria(
        self,
        wringer_pass: int,
        contradiction: float,
        info_gain_ratio: float,
        entropy: float,
    ) -> HaltReason | None:
        """
        Check all four governor halting criteria.

        Criterion 1 — Convergence:
            Φ < ε_converge → engines agree, D_L* is the answer.

        Criterion 2 — Diminishing returns:
            IG_ratio < ρ_min → each wringer pass is producing less new information.
            Another pass would be waste.

        Criterion 3 — Budget exhaustion:
            wringer_pass ≥ budget → computational resource limit reached.

        Criterion 4 — Irreducible uncertainty:
            entropy < entropy_min AND Φ > delta_min → the hypothesis space has
            narrowed, but the engines still disagree. More passes will not help.
            The contradiction is structural, not resolvable by further reasoning.
        """
        # 1. Convergence
        if contradiction < self.config.eps_converge:
            return HaltReason.CONVERGENCE

        # 2. Diminishing returns (only after first pass — need a prior to compare)
        if wringer_pass > 0 and info_gain_ratio < self.config.rho_min:
            return HaltReason.DIMINISHING_RETURNS

        # 3. Budget exhaustion
        if self.config.budget is not None and wringer_pass >= self.config.budget:
            return HaltReason.BUDGET_EXHAUSTION

        # 4. Irreducible uncertainty
        if entropy < self.config.entropy_min and contradiction > self.config.delta_min:
            return HaltReason.IRREDUCIBLE_UNCERTAINTY

        return None

    # ── Governor: output rule ────────────────────────────────────────────────

    def _generate_output(
        self,
        deduction_L: DeductionD,
        deduction_R: DeductionD,
        contradiction: float,
        entropy: float,
    ) -> tuple[Any, str, float]:
        """
        Governor output rule (formal spec Section 6).

        Case 1 — Convergence (Φ < ε_converge):
            Engines agree. Output D_L* directly.
            Confidence = 1 - Φ/ε_converge (1.0 at perfect agreement).

        Case 2 — Partial convergence (ε_converge ≤ Φ < ε_partial):
            Blend D_L* and D_R* with contradiction-weighted blend:
                w_L = (1 - Φ/ε_partial) / 2   ← falls as contradiction rises
                w_R = (1 + Φ/ε_partial) / 2   ← rises as contradiction rises
            The adversarial engine gains authority as disagreement grows.
            This is the formal blend rule from the specification.

        Case 3 — Full disagreement (Φ ≥ ε_partial):
            Expose both conclusions and the contradiction.
            Caller must handle this case explicitly.
        """
        # Case 1: Convergence
        if contradiction < self.config.eps_converge:
            confidence = 1.0 - (contradiction / self.config.eps_converge)
            return deduction_L, "convergence", max(0.0, min(1.0, confidence))

        # Case 2: Partial convergence — blend with formal weights
        if contradiction < self.config.eps_partial:
            ratio = contradiction / self.config.eps_partial
            w_L = (1.0 - ratio) / 2.0  # left weight falls as Φ rises
            w_R = (1.0 + ratio) / 2.0  # right weight rises as Φ rises

            try:
                if isinstance(deduction_L, (int, float)) and isinstance(deduction_R, (int, float)):
                    blended = w_L * deduction_L + w_R * deduction_R
                    confidence = 1.0 - ratio * 0.5
                    return blended, "blend", max(0.0, min(1.0, confidence))
            except Exception:
                pass

            output = {
                "type": "blend",
                "left": deduction_L,
                "right": deduction_R,
                "weights": {"left": round(w_L, 4), "right": round(w_R, 4)},
                "contradiction": contradiction,
            }
            confidence = 1.0 - ratio * 0.5
            return output, "blend", max(0.0, min(1.0, confidence))

        # Case 3: Full disagreement — expose both
        output = {
            "type": "disagreement",
            "left": deduction_L,
            "right": deduction_R,
            "contradiction": contradiction,
            "entropy": entropy,
        }
        return output, "disagreement", 0.5

    # ── Finalize: generate output and update wisdom ──────────────────────────

    def _finalize(
        self,
        query: str,
        deduction_L: Any,
        deduction_R: Any,
        contradiction: float,
        entropy: float,
        wringer_passes_used: int,
        halt_reason: HaltReason,
        trace: list[WringerPassTrace],
    ) -> TheosOutput:
        """Generate final output, update wisdom, return TheosOutput."""
        output, output_type, confidence = self._generate_output(
            deduction_L, deduction_R, contradiction, entropy
        )

        # Deposit this query's lesson into the wisdom register (the meta-past)
        self.wisdom = self.update_wisdom(self.wisdom, query, output, confidence)

        return TheosOutput(
            output=output,
            output_type=output_type,
            confidence=confidence,
            contradiction=contradiction,
            wringer_passes_used=wringer_passes_used,
            halt_reason=halt_reason,
            trace=trace,
            wisdom_updated=True,
        )

    # ── Wisdom management ────────────────────────────────────────────────────

    def get_wisdom_summary(self) -> dict[str, Any]:
        """Return the accumulated wisdom register."""
        return {
            "total_entries": len(self.wisdom),
            "entries": self.wisdom,
        }

    def clear_wisdom(self):
        """Clear all accumulated wisdom (the full meta-past)."""
        self.wisdom = []

    # ── Trace export ─────────────────────────────────────────────────────────

    def export_trace(self, trace: list[WringerPassTrace]) -> str:
        """Export a full wringer trace as JSON (for audit and debugging)."""
        trace_data = []
        for wp in trace:
            pass_data = {
                "wringer_pass": wp.wringer_pass,
                "contradiction": wp.contradiction,
                "entropy": wp.entropy,
                "info_gain_ratio": wp.info_gain_ratio,
                "halt_reason": wp.halt_reason.value if wp.halt_reason else None,
                "deduction_L": str(wp.deduction_L),
                "deduction_R": str(wp.deduction_R),
                "left_inner_passes": [
                    {
                        "pass_num": ip.pass_num,
                        "used_own_prior": ip.used_own_prior,
                        "pattern_I": str(ip.pattern_I),
                        "hypothesis": str(ip.hypothesis),
                        "deduction": str(ip.deduction),
                    }
                    for ip in wp.left_inner_passes
                ],
                "right_inner_passes": [
                    {
                        "pass_num": ip.pass_num,
                        "used_own_prior": ip.used_own_prior,
                        "pattern_I": str(ip.pattern_I),
                        "hypothesis": str(ip.hypothesis),
                        "deduction": str(ip.deduction),
                    }
                    for ip in wp.right_inner_passes
                ],
            }
            trace_data.append(pass_data)
        return json.dumps(trace_data, indent=2)
