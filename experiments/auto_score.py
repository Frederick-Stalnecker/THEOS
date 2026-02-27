#!/usr/bin/env python3
"""
Auto-Score — AI-assisted preliminary scoring of THEOS experiment results.

Uses Claude to rate each answer on the 5 rubric dimensions, blind to condition label.
Answers are presented in randomized order. Condition labels revealed at analysis time.

This is NOT a substitute for blind human rating — it is a preliminary estimate
to identify whether the pattern is strong enough to justify the human rating effort.

Usage:
    ANTHROPIC_API_KEY="sk-ant-..." python3.12 experiments/auto_score.py \
        experiments/results/run_YYYYMMDD.json \
        --output experiments/results/auto_scored_run.json
"""

import os, sys, json, random, time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))
sys.path.insert(0, os.path.dirname(__file__))
from llm_interface import get_llm

DIMENSIONS = ["accuracy", "depth", "utility", "coherence", "coverage"]

RUBRIC = """
You are a blind academic reviewer rating answers to conceptual questions.
You do not know which AI system produced each answer.

Rate on each dimension from 0 to 3:

ACCURACY (0-3):
  3 = Factually correct, no false claims, all key concepts correctly defined
  2 = Mostly correct, minor inaccuracies
  1 = Partially correct but contains significant errors
  0 = Substantially incorrect

DEPTH (0-3):
  3 = Reveals non-obvious structure, finds orthogonal dimensions, deduces consequences
  2 = Goes beyond surface, adds some analysis
  1 = Surface-level description only
  0 = Superficial or circular

UTILITY (0-3):
  3 = Could immediately inform real decisions or understanding in a domain
  2 = Useful but would need further development
  1 = Marginally useful
  0 = Not useful

COHERENCE (0-3):
  3 = Perfectly structured, each point follows logically from the previous
  2 = Mostly coherent with minor logical gaps
  1 = Some incoherence or contradictions
  0 = Disorganized or self-contradictory

COVERAGE (0-3):
  3 = Covers all important aspects; nothing significant missing
  2 = Covers most aspects
  1 = Covers some but misses important dimensions
  0 = Misses most of what matters

Return ONLY a JSON object with this exact format (no other text):
{"accuracy": N, "depth": N, "utility": N, "coherence": N, "coverage": N}
where each N is 0, 1, 2, or 3.
"""


def score_answer(llm, question: str, answer: str) -> dict:
    prompt = (
        f"{RUBRIC}\n\n"
        f"QUESTION: {question}\n\n"
        f"ANSWER TO RATE:\n{answer[:1500]}\n\n"
        f"Return ONLY the JSON object with your scores."
    )
    resp = llm.complete(prompt, max_tokens=100)
    text = resp.text.strip()
    # Extract JSON from response
    start = text.find('{')
    end = text.rfind('}') + 1
    if start >= 0 and end > start:
        try:
            scores = json.loads(text[start:end])
            # Validate
            for dim in DIMENSIONS:
                if dim not in scores or not isinstance(scores[dim], int):
                    scores[dim] = 1
                scores[dim] = max(0, min(3, scores[dim]))
            return scores
        except json.JSONDecodeError:
            pass
    # Fallback: neutral scores
    return {d: 1 for d in DIMENSIONS}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("run_file")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    llm = get_llm("anthropic", api_key=api_key)

    with open(args.run_file) as f:
        run = json.load(f)

    print(f"Auto-scoring {len(run['results'])} questions × 3 conditions...")
    print("Answers presented in randomized order per question (blind to condition).\n")

    total_calls = 0
    for i, qr in enumerate(run["results"], 1):
        q = qr["question_text"]
        print(f"[{i}/{len(run['results'])}] {q[:60]}...")

        # Collect conditions and shuffle
        conditions = []
        for attr in ["condition_a", "condition_b", "condition_c"]:
            cr = qr.get(attr)
            if cr and cr.get("answer"):
                conditions.append((attr, cr))
        random.shuffle(conditions)

        for attr, cr in conditions:
            scores = score_answer(llm, q, cr["answer"])
            cr["score_accuracy"] = scores["accuracy"]
            cr["score_depth"] = scores["depth"]
            cr["score_utility"] = scores["utility"]
            cr["score_coherence"] = scores["coherence"]
            cr["score_coverage"] = scores["coverage"]
            total = sum(scores[d] for d in DIMENSIONS)
            label = {"condition_a": "A(SP)", "condition_b": "B(CoT)", "condition_c": "C(THEOS)"}[attr]
            print(f"  {label}: acc={scores['accuracy']} dep={scores['depth']} "
                  f"util={scores['utility']} coh={scores['coherence']} cov={scores['coverage']} → {total}/15")
            total_calls += 1
            time.sleep(0.5)  # avoid rate limits

    print(f"\nTotal scoring calls: {total_calls}")

    # Save scored run
    output_path = args.output or args.run_file.replace(".json", "_autoscored.json")
    with open(output_path, "w") as f:
        json.dump(run, f, indent=2)
    print(f"Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    path = main()
    print(f"\nNow run: python3.12 experiments/score_results.py {path}")
