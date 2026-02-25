# Copyright (c) 2026 Frederick Davis Stalnecker
# Licensed under the MIT License

"""
THEOS Validation Experiment
============================

Tests the core hypothesis:

    H1: Two-pass I→A→D→I reasoning (THEOS) produces measurably better answers
        than single-pass completion on open-ended conceptual questions.

Three conditions per question:
    A. Single-Pass (SP):      Direct answer to the question
    B. Chain-of-Thought (CoT): "Let's think step by step" before answering
    C. THEOS Two-Pass (T2P):   Full I→A→D first pass, deduction fed back into
                               induction for a second I→A→D pass

Human rating rubric (0-3 per dimension, 15 max per answer):
    1. Accuracy      — Is the answer logically/factually correct?
    2. Depth         — Does it go beyond surface-level categorization?
    3. Utility       — Is the answer actionable or meaningfully applicable?
    4. Coherence     — Is it well-organized and internally consistent?
    5. Coverage      — Does it address multiple dimensions of the question?

Statistical test:
    Paired t-test on mean scores: C vs A, C vs B, B vs A
    Effect size: Cohen's d
    Significance threshold: p < 0.05

If THEOS (C) does not significantly outperform both baselines (A, B):
    → The core hypothesis is not supported by this evidence
    → Report that result honestly

Usage:
    # Framework test with mock LLM (no API needed)
    python experiments/theos_validation_experiment.py --backend mock --questions 3

    # Real experiment with Claude
    export ANTHROPIC_API_KEY=sk-ant-...
    python experiments/theos_validation_experiment.py --backend anthropic --questions 30

    # Real experiment with GPT-4
    export OPENAI_API_KEY=sk-...
    python experiments/theos_validation_experiment.py --backend openai --questions 30

Author: Celeste (Claude), working under authority of Frederick Davis Stalnecker
Date: 2026-02-24
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional

# Allow running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from experiments.question_bank import QUESTIONS, Question
from experiments.llm_interface import LLMInterface, LLMResponse, get_llm


# ─── Result structures ────────────────────────────────────────────────────────

@dataclass
class StepTrace:
    """Records one I→A→D step."""
    step: str           # "inductive" | "abductive" | "deductive"
    prompt_summary: str # First 120 chars of prompt
    response: str
    tokens: int = 0
    latency_ms: float = 0.0


@dataclass
class ConditionResult:
    """One answer under one condition."""
    condition: str          # "A_single_pass" | "B_chain_of_thought" | "C_theos_two_pass"
    question_id: int
    answer: str             # The final answer text
    trace: List[StepTrace] = field(default_factory=list)
    total_tokens: int = 0
    total_latency_ms: float = 0.0
    # Human rating fields (filled in after experiment)
    score_accuracy: Optional[int] = None   # 0-3
    score_depth: Optional[int] = None      # 0-3
    score_utility: Optional[int] = None    # 0-3
    score_coherence: Optional[int] = None  # 0-3
    score_coverage: Optional[int] = None   # 0-3

    @property
    def total_score(self) -> Optional[int]:
        scores = [self.score_accuracy, self.score_depth, self.score_utility,
                  self.score_coherence, self.score_coverage]
        if any(s is None for s in scores):
            return None
        return sum(scores)  # type: ignore


@dataclass
class QuestionResult:
    """All three condition results for one question."""
    question_id: int
    question_text: str
    condition_a: Optional[ConditionResult] = None
    condition_b: Optional[ConditionResult] = None
    condition_c: Optional[ConditionResult] = None


@dataclass
class ExperimentRun:
    """Complete experiment run record."""
    experiment_id: str
    model: str
    backend: str
    timestamp: str
    questions_tested: int
    results: List[QuestionResult] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f"Results saved to {path}")


# ─── Prompts ─────────────────────────────────────────────────────────────────

SYSTEM_CONTEXT = (
    "You are a precise analytical thinker. Answer the question completely and "
    "honestly. Do not pad your answer. Do not use bullet points unless the "
    "question specifically calls for a list. Write in clear prose."
)


def prompt_single_pass(question: str) -> str:
    return f"{SYSTEM_CONTEXT}\n\nQuestion: {question}\n\nAnswer:"


def prompt_chain_of_thought(question: str) -> str:
    return (
        f"{SYSTEM_CONTEXT}\n\n"
        f"Question: {question}\n\n"
        f"Let me think through this carefully before answering.\n\nAnswer:"
    )


def prompt_inductive(question: str, prior_context: str = "") -> str:
    if prior_context:
        return (
            f"Question: {question}\n\n"
            f"Prior conclusion to reflect on: {prior_context}\n\n"
            f"Inductive step — from this prior conclusion as a new observation, "
            f"what patterns and generalizations can you extract? "
            f"What does it reveal about the underlying structure?"
        )
    return (
        f"Question: {question}\n\n"
        f"Inductive step — from observable facts and examples, "
        f"what patterns and generalizations can you identify relevant to this question?"
    )


def prompt_abductive(question: str, inductive_output: str) -> str:
    return (
        f"Question: {question}\n\n"
        f"Observations and patterns: {inductive_output}\n\n"
        f"Abductive step — given these observations, what is the best explanatory "
        f"hypothesis that accounts for all of them? What underlying principle or "
        f"mechanism best explains the pattern?"
    )


def prompt_deductive(question: str, abductive_output: str) -> str:
    return (
        f"Question: {question}\n\n"
        f"Hypothesis: {abductive_output}\n\n"
        f"Deductive step — given this hypothesis, what conclusions follow "
        f"necessarily? What are the logical implications for the original question? "
        f"State the conclusion clearly."
    )


# ─── Reasoning conditions ────────────────────────────────────────────────────

def run_single_pass(llm: LLMInterface, question: str) -> ConditionResult:
    """Condition A: Direct single-pass completion."""
    prompt = prompt_single_pass(question.text)
    resp = llm.complete(prompt, max_tokens=400)
    trace = [StepTrace("single_pass", prompt[:120], resp.text,
                       resp.completion_tokens, resp.latency_ms)]
    return ConditionResult(
        condition="A_single_pass",
        question_id=question.id,
        answer=resp.text.strip(),
        trace=trace,
        total_tokens=resp.prompt_tokens + resp.completion_tokens,
        total_latency_ms=resp.latency_ms,
    )


def run_chain_of_thought(llm: LLMInterface, question: str) -> ConditionResult:
    """Condition B: Chain-of-thought — standard "think step by step" prompt."""
    prompt = prompt_chain_of_thought(question.text)
    resp = llm.complete(prompt, max_tokens=500)
    trace = [StepTrace("chain_of_thought", prompt[:120], resp.text,
                       resp.completion_tokens, resp.latency_ms)]
    return ConditionResult(
        condition="B_chain_of_thought",
        question_id=question.id,
        answer=resp.text.strip(),
        trace=trace,
        total_tokens=resp.prompt_tokens + resp.completion_tokens,
        total_latency_ms=resp.latency_ms,
    )


def run_theos_two_pass(llm: LLMInterface, question: str) -> ConditionResult:
    """
    Condition C: THEOS two-pass I→A→D→I.

    First pass:
        Inductive(Q) → Abductive(Q, I1) → Deductive(Q, A1) = D1

    Second pass (D1 fed back as new observation):
        Inductive(Q, D1) → Abductive(Q, I2) → Deductive(Q, A2) = final answer

    The governor is implicit here: two passes are fixed by design.
    Future work can hook the governor to decide whether a third pass adds value.
    """
    trace: List[StepTrace] = []
    total_tokens = 0
    total_latency = 0.0

    def call(prompt: str, step_name: str, max_tokens: int = 350) -> str:
        nonlocal total_tokens, total_latency
        resp = llm.complete(prompt, max_tokens=max_tokens)
        total_tokens += resp.prompt_tokens + resp.completion_tokens
        total_latency += resp.latency_ms
        trace.append(StepTrace(step_name, prompt[:120], resp.text,
                               resp.completion_tokens, resp.latency_ms))
        return resp.text.strip()

    # ── First pass ──────────────────────────────────────────────
    i1 = call(prompt_inductive(question.text), "pass1_inductive")
    a1 = call(prompt_abductive(question.text, i1), "pass1_abductive")
    d1 = call(prompt_deductive(question.text, a1), "pass1_deductive")

    # ── Second pass (D1 feeds back into Induction) ──────────────
    i2 = call(prompt_inductive(question.text, prior_context=d1), "pass2_inductive")
    a2 = call(prompt_abductive(question.text, i2), "pass2_abductive")
    d2 = call(prompt_deductive(question.text, a2), "pass2_deductive", max_tokens=500)

    return ConditionResult(
        condition="C_theos_two_pass",
        question_id=question.id,
        answer=d2,
        trace=trace,
        total_tokens=total_tokens,
        total_latency_ms=total_latency,
    )


# ─── Main experiment runner ───────────────────────────────────────────────────

class THEOSValidationExperiment:
    """
    Runs the three-condition experiment across the question bank.

    IMPORTANT: This class generates the answers. A human must then rate them
    using the scoring rubric. The class provides a rating tool for that.
    """

    def __init__(self, llm: LLMInterface, question_ids: Optional[List[int]] = None):
        self.llm = llm
        questions = QUESTIONS
        if question_ids:
            questions = [q for q in questions if q.id in question_ids]
        self.questions = questions

    def run(
        self,
        conditions: str = "ABC",
        verbose: bool = True,
    ) -> ExperimentRun:
        """
        Run the experiment.

        Args:
            conditions: Which conditions to run. "ABC" = all, "AC" = skip CoT, etc.
            verbose: Print progress.

        Returns:
            ExperimentRun with all results.
        """
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        experiment = ExperimentRun(
            experiment_id=run_id,
            model=self.llm.model_name,
            backend=type(self.llm).__name__,
            timestamp=datetime.now().isoformat(),
            questions_tested=len(self.questions),
        )

        for i, question in enumerate(self.questions, 1):
            if verbose:
                print(f"\n[{i}/{len(self.questions)}] Q{question.id}: {question.text[:70]}...")

            q_result = QuestionResult(
                question_id=question.id,
                question_text=question.text,
            )

            if "A" in conditions:
                if verbose:
                    print("  Condition A: Single-pass...")
                q_result.condition_a = run_single_pass(self.llm, question)
                if verbose:
                    print(f"    ✓ {len(q_result.condition_a.answer)} chars")

            if "B" in conditions:
                if verbose:
                    print("  Condition B: Chain-of-thought...")
                q_result.condition_b = run_chain_of_thought(self.llm, question)
                if verbose:
                    print(f"    ✓ {len(q_result.condition_b.answer)} chars")

            if "C" in conditions:
                if verbose:
                    print("  Condition C: THEOS two-pass (6 LLM calls)...")
                q_result.condition_c = run_theos_two_pass(self.llm, question)
                if verbose:
                    print(f"    ✓ {len(q_result.condition_c.answer)} chars, "
                          f"{q_result.condition_c.total_tokens} tokens")

            experiment.results.append(q_result)

        return experiment

    def print_answers_for_rating(self, experiment: ExperimentRun) -> None:
        """
        Print answers in a blind format suitable for human rating.
        Labels are anonymized (X, Y, Z instead of A, B, C).

        IMPORTANT: The rater should not know which condition is which.
        The reveal mapping is printed at the end AFTER rating is complete.
        """
        import random
        label_map = {"A_single_pass": "X", "B_chain_of_thought": "Y",
                     "C_theos_two_pass": "Z"}
        # Shuffle so rater doesn't always see same order
        for q_result in experiment.results:
            conditions_present = []
            for attr, cond in [("condition_a", "A_single_pass"),
                               ("condition_b", "B_chain_of_thought"),
                               ("condition_c", "C_theos_two_pass")]:
                cr = getattr(q_result, attr)
                if cr is not None:
                    conditions_present.append((label_map[cond], cr.answer))
            random.shuffle(conditions_present)

            print(f"\n{'='*70}")
            print(f"QUESTION {q_result.question_id}: {q_result.question_text}")
            print('='*70)
            for label, answer in conditions_present:
                print(f"\n--- Answer {label} ---")
                print(answer[:1000])
                if len(answer) > 1000:
                    print("[... truncated ...]")
            print(f"\nRate each answer (Accuracy, Depth, Utility, Coherence, Coverage — each 0-3):")

        print("\n\nLABEL REVEAL (do not read before rating):")
        print("X = Single-pass (Condition A)")
        print("Y = Chain-of-thought (Condition B)")
        print("Z = THEOS two-pass (Condition C)")


# ─── Statistical analysis ─────────────────────────────────────────────────────

def analyze_results(experiment: ExperimentRun) -> Dict:
    """
    Compute summary statistics after human ratings have been entered.

    Performs:
    - Mean score per condition
    - Paired t-test (C vs A, C vs B, B vs A)
    - Cohen's d effect sizes
    - Verdict: does THEOS significantly outperform baselines?
    """
    import math

    def mean(xs):
        return sum(xs) / len(xs) if xs else 0.0

    def std(xs, m):
        if len(xs) < 2:
            return 0.0
        return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))

    def paired_t(a_scores, b_scores):
        """Paired t-test. Returns (t_stat, approx_p_interpretation)."""
        if len(a_scores) != len(b_scores) or len(a_scores) < 2:
            return None, "insufficient data"
        diffs = [b - a for a, b in zip(a_scores, b_scores)]
        d_mean = mean(diffs)
        d_std = std(diffs, d_mean)
        if d_std == 0:
            return None, "zero variance"
        n = len(diffs)
        t = d_mean / (d_std / math.sqrt(n))
        # Approximate p-value interpretation (two-tailed, df=n-1)
        # For rigorous analysis, use scipy.stats.ttest_rel
        abs_t = abs(t)
        if n >= 20:
            p_note = "p<0.05 (t>{:.2f})".format(2.09) if abs_t > 2.09 else "p>=0.05"
        else:
            p_note = f"t={t:.3f}, use scipy for exact p (n={n})"
        return t, p_note

    def cohens_d(a_scores, b_scores):
        """Cohen's d effect size."""
        ma, mb = mean(a_scores), mean(b_scores)
        sa, sb = std(a_scores, ma), std(b_scores, mb)
        pooled = math.sqrt((sa**2 + sb**2) / 2) if (sa + sb) > 0 else 1
        return (mb - ma) / pooled if pooled > 0 else 0.0

    a_scores, b_scores, c_scores = [], [], []
    for qr in experiment.results:
        if qr.condition_a and qr.condition_a.total_score is not None:
            a_scores.append(qr.condition_a.total_score)
        if qr.condition_b and qr.condition_b.total_score is not None:
            b_scores.append(qr.condition_b.total_score)
        if qr.condition_c and qr.condition_c.total_score is not None:
            c_scores.append(qr.condition_c.total_score)

    t_ca, p_ca = paired_t(a_scores, c_scores) if a_scores and c_scores else (None, "no data")
    t_cb, p_cb = paired_t(b_scores, c_scores) if b_scores and c_scores else (None, "no data")
    t_ba, p_ba = paired_t(a_scores, b_scores) if a_scores and b_scores else (None, "no data")

    d_ca = cohens_d(a_scores, c_scores) if a_scores and c_scores else 0.0
    d_cb = cohens_d(b_scores, c_scores) if b_scores and c_scores else 0.0

    result = {
        "n_rated": len(a_scores),
        "mean_score_A": mean(a_scores),
        "mean_score_B": mean(b_scores),
        "mean_score_C": mean(c_scores),
        "C_vs_A": {"t": t_ca, "p_note": p_ca, "cohens_d": d_ca},
        "C_vs_B": {"t": t_cb, "p_note": p_cb, "cohens_d": d_cb},
        "B_vs_A": {"t": t_ba, "p_note": p_ba},
        "verdict": _verdict(t_ca, p_ca, d_ca, t_cb, p_cb, d_cb),
    }
    return result


def _verdict(t_ca, p_ca, d_ca, t_cb, p_cb, d_cb) -> str:
    """Honest verdict based on statistical results."""
    if t_ca is None or t_cb is None:
        return "INSUFFICIENT DATA — more rated questions needed."
    if "p<0.05" in str(p_ca) and "p<0.05" in str(p_cb) and d_ca > 0.2 and d_cb > 0.2:
        return (
            "SUPPORTED — THEOS (C) significantly outperforms both baselines "
            f"(vs A: d={d_ca:.2f}, vs B: d={d_cb:.2f}). Core hypothesis is supported."
        )
    if "p<0.05" in str(p_ca) and "p<0.05" not in str(p_cb):
        return (
            "PARTIAL — THEOS beats single-pass but NOT chain-of-thought. "
            "The improvement may be attributable to prompting alone."
        )
    return (
        "NOT SUPPORTED — THEOS did not significantly outperform baselines. "
        "Report this result. Do not adjust the data."
    )


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="THEOS Validation Experiment — prove or disprove the core hypothesis"
    )
    parser.add_argument(
        "--backend", default="mock",
        choices=["mock", "anthropic", "openai"],
        help="LLM backend to use (default: mock)",
    )
    parser.add_argument(
        "--questions", type=int, default=3,
        help="Number of questions to test (default: 3 for quick test)",
    )
    parser.add_argument(
        "--question-ids", nargs="+", type=int,
        help="Specific question IDs to test (overrides --questions)",
    )
    parser.add_argument(
        "--conditions", default="ABC",
        help="Which conditions to run: A=single-pass, B=CoT, C=THEOS (default: ABC)",
    )
    parser.add_argument(
        "--output", default="experiments/results",
        help="Output directory for results (default: experiments/results)",
    )
    parser.add_argument(
        "--api-key", default=None,
        help="API key (or set ANTHROPIC_API_KEY / OPENAI_API_KEY env var)",
    )
    parser.add_argument(
        "--print-for-rating", action="store_true",
        help="Print answers in blind format for human rating",
    )
    args = parser.parse_args()

    # Build LLM
    llm = get_llm(args.backend, api_key=args.api_key)
    print(f"Backend: {args.backend} | Model: {llm.model_name}")

    # Select questions
    question_ids = args.question_ids
    if not question_ids:
        from experiments.question_bank import QUESTIONS as ALL_Q
        question_ids = [q.id for q in ALL_Q[:args.questions]]

    print(f"Testing {len(question_ids)} questions, conditions: {args.conditions}")

    # Run
    exp = THEOSValidationExperiment(llm, question_ids=question_ids)
    result = exp.run(conditions=args.conditions, verbose=True)

    # Save
    out_path = os.path.join(args.output, f"run_{result.experiment_id}.json")
    result.save(out_path)

    if args.print_for_rating:
        exp.print_answers_for_rating(result)

    print("\nNext step: Rate the answers using the scoring rubric in experiments/RATING_GUIDE.md")
    print(f"Then run: python experiments/score_results.py {out_path}")


if __name__ == "__main__":
    main()
