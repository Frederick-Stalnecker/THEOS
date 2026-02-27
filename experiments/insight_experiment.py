# Copyright (c) 2026 Frederick Davis Stalnecker
# Licensed under the MIT License

"""
Insight Detection Experiment
=============================

Tests the core THEOS thesis using the Insight Detection Rubric (IDR):

    H1: I→A→D dialectical structure produces answers with greater structural
        discovery than single-pass completion, independently of iteration count.

    H2: Multi-pass THEOS (full framework) adds further value beyond a
        single structured I→A→D pass.

Three conditions per question:
    A. SP    — Direct single-pass answer (1 LLM call)
    B. IAD-P — Single prompt, explicitly structured as I→A→D (1 LLM call)
    C. THEOS — Full two-engine multi-pass I→A→D (6–12 LLM calls)

Rating dimensions (IDR, 0-3 each, 15 max):
    1. Revelation          — "Do you understand something you didn't before?"
    2. Structural Discovery — "Did it find non-obvious dimensions?"
    3. Productive Tension  — "Does it produce more than either perspective alone?"
    4. Consequence Derivation — "Does it derive non-trivial consequences?"
    5. Question Interrogation — "Does it name hidden assumptions?"

Design rationale: See experiments/INSIGHT_RUBRIC.md
    The previous rubric (accuracy/depth/utility/coherence/coverage) rewarded
    linear completeness and penalized structured uncertainty — exactly what
    THEOS produces. This rubric measures what THEOS claims to produce.

Usage:
    # Framework test (no API needed)
    python3.12 experiments/insight_experiment.py --backend mock --questions 3

    # Real experiment with Claude
    export ANTHROPIC_API_KEY=sk-ant-...
    python3.12 experiments/insight_experiment.py --backend anthropic --questions 30

Author: Celeste (Claude), working under authority of Frederick Davis Stalnecker
Date: 2026-02-27
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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from experiments.question_bank import QUESTIONS, Question
from experiments.llm_interface import LLMInterface, LLMResponse, get_llm


# ─── Prompts ─────────────────────────────────────────────────────────────────

SYSTEM_SP = (
    "You are a rigorous analytical thinker. "
    "Answer the question directly and clearly."
)

SYSTEM_IAD_P = (
    "You are a dialectical reasoning system. "
    "Work through questions using structured inquiry."
)

# The IAD-P prompt: single call, but structured as I→A→D
# This is the key condition — controls for number of calls, isolates structure.
IAD_P_TEMPLATE = """Answer the following question using this structured approach:

QUESTION: {question}

Please work through these steps explicitly:

INDUCTION — What patterns or structural features do you observe in the concepts involved?
(What is non-obvious about what's being asked?)

ABDUCTION-L — Propose the most INSIGHTFUL framing: a hypothesis that reveals hidden
structure or non-obvious dimensions not apparent in the question.

ABDUCTION-R — Propose the ADVERSARIAL framing: what assumption does the typical
treatment of this question make that should be challenged?

DEDUCTION — From both framings (L and R), what follows necessarily?
What can be derived that neither framing could produce alone?

SYNTHESIS — What do you now understand about this question that would not be
apparent from a direct answer? What hidden structure did the analysis reveal?

Be explicit about each step. Do not collapse them into a single narrative."""


# THEOS two-pass prompts (same as validation experiment)
THEOS_PASS1_INDUCTIVE = (
    "You are a careful analytical thinker. Given the question below, "
    "identify the key conceptual tensions, hidden assumptions, and structural "
    "relationships. Do not answer yet — only map the terrain.\n\nQuestion: {question}"
)

THEOS_PASS1_ABDUCTIVE_L = (
    "Based on this analysis:\n{inductive}\n\n"
    "Propose the MOST INSIGHTFUL hypothesis: a framing that reveals hidden "
    "structure or non-obvious dimensions. This is the constructive engine — "
    "find what a naive reading would miss.\n\nQuestion: {question}"
)

THEOS_PASS1_ABDUCTIVE_R = (
    "Based on this analysis:\n{inductive}\n\n"
    "Propose the ADVERSARIAL hypothesis: challenge the most common assumption "
    "in how this question is usually treated. This is the critical engine — "
    "find what the constructive framing might overlook.\n\nQuestion: {question}"
)

THEOS_PASS1_DEDUCTIVE = (
    "Left hypothesis (constructive):\n{left}\n\n"
    "Right hypothesis (adversarial):\n{right}\n\n"
    "From both, derive what follows necessarily. Synthesize the first-pass "
    "understanding. Where do they converge? Where do they remain in tension?\n\n"
    "Question: {question}"
)

THEOS_PASS2_INDUCTIVE = (
    "First-pass synthesis:\n{synthesis}\n\n"
    "Now: given this synthesis, what remains unresolved? What new structural "
    "features become visible that weren't apparent before the first pass?\n\n"
    "Original question: {question}"
)

THEOS_PASS2_DEDUCTIVE = (
    "First-pass synthesis:\n{synthesis}\n\n"
    "Second-pass observation:\n{p2_inductive}\n\n"
    "Now produce the final answer. Integrate both passes. Where has understanding "
    "genuinely deepened? What non-obvious structure did the dialectic reveal?\n\n"
    "Original question: {question}"
)


# ─── Result structures ────────────────────────────────────────────────────────

@dataclass
class ConditionResult:
    condition: str          # "A_SP" | "B_IAD_P" | "C_THEOS"
    question: str
    answer: str
    total_tokens: int = 0
    latency_ms: float = 0.0
    llm_calls: int = 0
    trace: List[Dict] = field(default_factory=list)


@dataclass
class QuestionResult:
    question_id: str
    question_text: str
    condition_a: Optional[Dict] = None  # SP
    condition_b: Optional[Dict] = None  # IAD-P
    condition_c: Optional[Dict] = None  # THEOS


# ─── Condition runners ────────────────────────────────────────────────────────

def run_condition_a(llm: LLMInterface, question: str) -> ConditionResult:
    """Condition A: Single-pass direct answer."""
    prompt = question
    t0 = time.time()
    resp = llm.complete(prompt, max_tokens=600)
    elapsed = (time.time() - t0) * 1000

    return ConditionResult(
        condition="A_SP",
        question=question,
        answer=resp.text,
        total_tokens=resp.prompt_tokens + resp.completion_tokens,
        latency_ms=elapsed,
        llm_calls=1,
        trace=[{"step": "direct", "response": resp.text[:200]}],
    )


def run_condition_b(llm: LLMInterface, question: str) -> ConditionResult:
    """Condition B: IAD-P — single structured prompt, explicitly I→A→D."""
    prompt = IAD_P_TEMPLATE.format(question=question)
    t0 = time.time()
    resp = llm.complete(prompt, max_tokens=900)
    elapsed = (time.time() - t0) * 1000

    return ConditionResult(
        condition="B_IAD_P",
        question=question,
        answer=resp.text,
        total_tokens=resp.prompt_tokens + resp.completion_tokens,
        latency_ms=elapsed,
        llm_calls=1,
        trace=[{"step": "iad_structured", "response": resp.text[:200]}],
    )


def run_condition_c(llm: LLMInterface, question: str) -> ConditionResult:
    """Condition C: THEOS two-pass, two-engine I→A→D."""
    trace = []
    total_tokens = 0
    t0 = time.time()

    # Pass 1 — Inductive
    r_ind = llm.complete(
        THEOS_PASS1_INDUCTIVE.format(question=question), max_tokens=400
    )
    total_tokens += r_ind.prompt_tokens + r_ind.completion_tokens
    trace.append({"step": "p1_inductive", "response": r_ind.text[:200]})
    time.sleep(0.3)

    # Pass 1 — Abductive L (constructive)
    r_abl = llm.complete(
        THEOS_PASS1_ABDUCTIVE_L.format(inductive=r_ind.text, question=question),
        max_tokens=400,
    )
    total_tokens += r_abl.prompt_tokens + r_abl.completion_tokens
    trace.append({"step": "p1_abductive_L", "response": r_abl.text[:200]})
    time.sleep(0.3)

    # Pass 1 — Abductive R (adversarial)
    r_abr = llm.complete(
        THEOS_PASS1_ABDUCTIVE_R.format(inductive=r_ind.text, question=question),
        max_tokens=400,
    )
    total_tokens += r_abr.prompt_tokens + r_abr.completion_tokens
    trace.append({"step": "p1_abductive_R", "response": r_abr.text[:200]})
    time.sleep(0.3)

    # Pass 1 — Deductive synthesis
    r_ded = llm.complete(
        THEOS_PASS1_DEDUCTIVE.format(
            left=r_abl.text, right=r_abr.text, question=question
        ),
        max_tokens=500,
    )
    total_tokens += r_ded.prompt_tokens + r_ded.completion_tokens
    trace.append({"step": "p1_deductive", "response": r_ded.text[:200]})
    time.sleep(0.3)

    # Pass 2 — Inductive (what remains?)
    r_p2i = llm.complete(
        THEOS_PASS2_INDUCTIVE.format(synthesis=r_ded.text, question=question),
        max_tokens=400,
    )
    total_tokens += r_p2i.prompt_tokens + r_p2i.completion_tokens
    trace.append({"step": "p2_inductive", "response": r_p2i.text[:200]})
    time.sleep(0.3)

    # Pass 2 — Final deduction
    r_final = llm.complete(
        THEOS_PASS2_DEDUCTIVE.format(
            synthesis=r_ded.text, p2_inductive=r_p2i.text, question=question
        ),
        max_tokens=600,
    )
    total_tokens += r_final.prompt_tokens + r_final.completion_tokens
    trace.append({"step": "p2_final", "response": r_final.text[:200]})

    elapsed = (time.time() - t0) * 1000

    return ConditionResult(
        condition="C_THEOS",
        question=question,
        answer=r_final.text,
        total_tokens=total_tokens,
        latency_ms=elapsed,
        llm_calls=6,
        trace=trace,
    )


# ─── Main experiment ──────────────────────────────────────────────────────────

def run_experiment(
    llm: LLMInterface,
    questions: List[Question],
    conditions: str = "ABC",
) -> Dict:
    results = []

    for i, q in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] {q.text[:70]}...")
        qr = {
            "question_id": q.id,
            "question_text": q.text,
        }

        if "A" in conditions:
            print("  Condition A: Single-pass...", flush=True)
            cr = run_condition_a(llm, q.text)
            print(f"    ✓ {len(cr.answer)} chars", flush=True)
            qr["condition_a"] = asdict(cr)
            time.sleep(0.5)

        if "B" in conditions:
            print("  Condition B: IAD-Prompted (1 call)...", flush=True)
            cr = run_condition_b(llm, q.text)
            print(f"    ✓ {len(cr.answer)} chars", flush=True)
            qr["condition_b"] = asdict(cr)
            time.sleep(0.5)

        if "C" in conditions:
            print("  Condition C: THEOS two-pass (6 LLM calls)...", flush=True)
            cr = run_condition_c(llm, q.text)
            print(f"    ✓ {len(cr.answer)} chars, {cr.total_tokens} tokens", flush=True)
            qr["condition_c"] = asdict(cr)
            time.sleep(0.5)

        results.append(qr)

    return {
        "experiment": "insight_detection_v1",
        "rubric": "IDR — Insight Detection Rubric",
        "conditions": {
            "A": "SP — Single-pass direct answer",
            "B": "IAD-P — Structured I→A→D in one prompt",
            "C": "THEOS — Two-engine multi-pass I→A→D",
        },
        "model": llm.model_name,
        "timestamp": datetime.now().isoformat(),
        "n_questions": len(questions),
        "results": results,
    }


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="THEOS Insight Detection Experiment"
    )
    parser.add_argument(
        "--backend",
        default="mock",
        choices=["mock", "anthropic", "openai"],
        help="LLM backend",
    )
    parser.add_argument(
        "--questions",
        type=int,
        default=5,
        help="Number of questions to test (default 5, max 30)",
    )
    parser.add_argument(
        "--conditions",
        default="ABC",
        help="Which conditions to run: any combination of A, B, C (default: ABC)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path (default: auto-generated in experiments/results/)",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key (or set ANTHROPIC_API_KEY / OPENAI_API_KEY env var)",
    )
    args = parser.parse_args()

    # Select questions
    n = min(args.questions, len(QUESTIONS))
    questions = QUESTIONS[:n]

    # Build LLM
    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
    llm = get_llm(args.backend, api_key=api_key)

    print(f"Backend: {args.backend} | Model: {llm.model_name}")
    print(f"Testing {n} questions, conditions: {args.conditions}")
    print(f"Rubric: Insight Detection Rubric (IDR)")
    print(f"  A=SP, B=IAD-Prompted, C=THEOS two-pass")
    print()

    run = run_experiment(llm, questions, conditions=args.conditions.upper())

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outpath = args.output or os.path.join(
        os.path.dirname(__file__), "results", f"insight_{ts}.json"
    )
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    with open(outpath, "w") as f:
        json.dump(run, f, indent=2)
    print(f"\nResults saved to {outpath}")
    print(f"\nNext step: Rate answers using experiments/INSIGHT_RUBRIC.md")
    print(f"Then run: python3.12 experiments/score_results.py {outpath}")


if __name__ == "__main__":
    main()
