# Copyright (c) 2026 Frederick Davis Stalnecker
# Licensed under the MIT License

"""
Score Results — THEOS Validation Experiment
=============================================

After a human has rated the answers using RATING_GUIDE.md, this script:
1. Loads the experiment JSON
2. Accepts scores via interactive input OR reads scores already entered in the JSON
3. Computes summary statistics and the statistical test
4. Prints an honest verdict

Usage:
    # Interactive scoring (enter scores one by one):
    python experiments/score_results.py experiments/results/run_YYYYMMDD_HHMMSS.json --interactive

    # Analyze already-scored JSON:
    python experiments/score_results.py experiments/results/run_YYYYMMDD_HHMMSS.json

    # Export analysis to file:
    python experiments/score_results.py experiments/results/run_YYYYMMDD_HHMMSS.json --output analysis.json
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from typing import Dict, List, Optional, Tuple


# ─── Load and save ────────────────────────────────────────────────────────────

def load_run(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def save_run(run: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(run, f, indent=2)
    print(f"Saved: {path}")


# ─── Interactive scoring ──────────────────────────────────────────────────────

DIMENSIONS = ["accuracy", "depth", "utility", "coherence", "coverage"]


def interactive_score(run: dict) -> dict:
    """
    Walk through each question result and prompt the user for scores.
    Displays the answer text and asks for 5 dimension scores (0-3 each).
    """
    import random

    print("\n" + "="*70)
    print("THEOS VALIDATION EXPERIMENT — BLIND SCORING")
    print("="*70)
    print("Rate each answer on 5 dimensions (0-3 each).")
    print("See experiments/RATING_GUIDE.md for the full rubric.\n")
    print("Labels are ANONYMIZED during scoring. Reveal printed at end.\n")

    label_map = {
        "A_single_pass": "X",
        "B_chain_of_thought": "Y",
        "C_theos_two_pass": "Z",
    }

    for q_result in run["results"]:
        print(f"\n{'='*70}")
        print(f"QUESTION {q_result['question_id']}: {q_result['question_text']}")
        print("="*70)

        # Collect all conditions present
        conditions = []
        for attr, cond_key in [("condition_a", "A_single_pass"),
                                ("condition_b", "B_chain_of_thought"),
                                ("condition_c", "C_theos_two_pass")]:
            cr = q_result.get(attr)
            if cr:
                conditions.append((attr, cond_key, cr))

        # Shuffle to prevent order bias
        random.shuffle(conditions)

        for attr, cond_key, cr in conditions:
            blind_label = label_map[cond_key]
            print(f"\n--- Answer {blind_label} ---")
            answer = cr.get("answer", "")
            print(answer[:1200])
            if len(answer) > 1200:
                print("[... truncated for brevity ...]")
            print()

            scores = {}
            for dim in DIMENSIONS:
                while True:
                    try:
                        val = int(input(f"  {dim.capitalize()} (0-3): ").strip())
                        if 0 <= val <= 3:
                            scores[dim] = val
                            break
                        print("  Enter 0, 1, 2, or 3.")
                    except (ValueError, EOFError):
                        print("  Enter 0, 1, 2, or 3.")

            cr["score_accuracy"] = scores["accuracy"]
            cr["score_depth"] = scores["depth"]
            cr["score_utility"] = scores["utility"]
            cr["score_coherence"] = scores["coherence"]
            cr["score_coverage"] = scores["coverage"]

    print("\n" + "="*70)
    print("LABEL REVEAL (conditions are now unmasked):")
    print("  X = Condition A: Single-pass (direct answer)")
    print("  Y = Condition B: Chain-of-thought ('think step by step')")
    print("  Z = Condition C: THEOS two-pass I→A→D→I")
    print("="*70)

    return run


# ─── Score extraction ─────────────────────────────────────────────────────────

def extract_scores(run: dict) -> Tuple[List[int], List[int], List[int]]:
    """
    Extract total scores per condition.
    Returns (a_scores, b_scores, c_scores) — only questions with all 5 dims rated.
    """
    a_scores, b_scores, c_scores = [], [], []

    for qr in run.get("results", []):
        def total(cr) -> Optional[int]:
            if cr is None:
                return None
            dims = [cr.get(f"score_{d}") for d in DIMENSIONS]
            if any(d is None for d in dims):
                return None
            return sum(dims)  # type: ignore

        ta = total(qr.get("condition_a"))
        tb = total(qr.get("condition_b"))
        tc = total(qr.get("condition_c"))

        if ta is not None:
            a_scores.append(ta)
        if tb is not None:
            b_scores.append(tb)
        if tc is not None:
            c_scores.append(tc)

    return a_scores, b_scores, c_scores


# ─── Statistics ───────────────────────────────────────────────────────────────

def mean(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def std(xs: List[float], m: float) -> float:
    if len(xs) < 2:
        return 0.0
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def paired_t_test(a: List[int], b: List[int]) -> Tuple[Optional[float], str]:
    """Paired t-test: H0: mean(b - a) = 0. Returns (t_stat, interpretation)."""
    if len(a) != len(b) or len(a) < 3:
        return None, f"insufficient paired data (n={len(a)})"
    diffs = [bi - ai for ai, bi in zip(a, b)]
    dm = mean(diffs)
    ds = std(diffs, dm)
    if ds == 0:
        return None, "zero variance in differences"
    n = len(diffs)
    t = dm / (ds / math.sqrt(n))
    abs_t = abs(t)
    # Critical values (two-tailed) for common df
    crit = {
        4: 2.776, 5: 2.571, 9: 2.262, 14: 2.145, 19: 2.093,
        24: 2.064, 29: 2.045, 49: 2.010, 99: 1.984,
    }
    df = n - 1
    # Find nearest critical value
    nearest_df = min(crit.keys(), key=lambda k: abs(k - df))
    cv = crit[nearest_df]
    sig = "p<0.05 ✓" if abs_t > cv else "p≥0.05 ✗"
    direction = "C>A" if dm > 0 else ("C<A" if dm < 0 else "no difference")
    return t, f"t={t:.3f}, df={df}, {sig}, {direction}"


def cohens_d(a: List[int], b: List[int]) -> float:
    """Cohen's d effect size: (mean_b - mean_a) / pooled_std."""
    if not a or not b:
        return 0.0
    ma, mb = mean(a), mean(b)
    sa = std(a, ma)
    sb = std(b, mb)
    pooled = math.sqrt((sa**2 + sb**2) / 2)
    return (mb - ma) / pooled if pooled > 0 else 0.0


def effect_label(d: float) -> str:
    ad = abs(d)
    if ad < 0.2:
        return "negligible"
    elif ad < 0.5:
        return "small"
    elif ad < 0.8:
        return "medium"
    else:
        return "large"


# ─── Analysis ─────────────────────────────────────────────────────────────────

def analyze(run: dict) -> dict:
    a_scores, b_scores, c_scores = extract_scores(run)

    ma = mean(a_scores)
    mb = mean(b_scores)
    mc = mean(c_scores)

    # Paired tests (C vs A, C vs B, B vs A)
    # For C vs A/B, we need matched pairs — use questions where both conditions rated
    # Build matched pairs
    ca_pairs: List[Tuple[int, int]] = []
    cb_pairs: List[Tuple[int, int]] = []
    ba_pairs: List[Tuple[int, int]] = []

    for qr in run.get("results", []):
        def tot(cr):
            if cr is None:
                return None
            dims = [cr.get(f"score_{d}") for d in DIMENSIONS]
            if any(d is None for d in dims):
                return None
            return sum(dims)

        ta = tot(qr.get("condition_a"))
        tb = tot(qr.get("condition_b"))
        tc = tot(qr.get("condition_c"))

        if ta is not None and tc is not None:
            ca_pairs.append((ta, tc))
        if tb is not None and tc is not None:
            cb_pairs.append((tb, tc))
        if ta is not None and tb is not None:
            ba_pairs.append((ta, tb))

    ca_a = [p[0] for p in ca_pairs]
    ca_c = [p[1] for p in ca_pairs]
    cb_b = [p[0] for p in cb_pairs]
    cb_c = [p[1] for p in cb_pairs]
    ba_a = [p[0] for p in ba_pairs]
    ba_b = [p[1] for p in ba_pairs]

    t_ca, p_ca = paired_t_test(ca_a, ca_c)
    t_cb, p_cb = paired_t_test(cb_b, cb_c)
    t_ba, p_ba = paired_t_test(ba_a, ba_b)

    d_ca = cohens_d(ca_a, ca_c)
    d_cb = cohens_d(cb_b, cb_c)

    # Verdict
    verdict = _verdict(p_ca, d_ca, p_cb, d_cb, len(ca_pairs))

    return {
        "n_rated_A": len(a_scores),
        "n_rated_B": len(b_scores),
        "n_rated_C": len(c_scores),
        "n_matched_CA": len(ca_pairs),
        "n_matched_CB": len(cb_pairs),
        "mean_score_A": round(ma, 3),
        "mean_score_B": round(mb, 3),
        "mean_score_C": round(mc, 3),
        "max_possible": 15,
        "C_vs_A": {
            "t_test": p_ca,
            "cohens_d": round(d_ca, 3),
            "effect": effect_label(d_ca),
            "mean_diff": round(mc - ma, 3),
        },
        "C_vs_B": {
            "t_test": p_cb,
            "cohens_d": round(d_cb, 3),
            "effect": effect_label(d_cb),
            "mean_diff": round(mc - mb, 3),
        },
        "B_vs_A": {
            "t_test": p_ba,
            "mean_diff": round(mb - ma, 3),
        },
        "verdict": verdict,
    }


def _verdict(p_ca: str, d_ca: float, p_cb: str, d_cb: float, n: int) -> str:
    if n < 10:
        return (
            f"INSUFFICIENT DATA ({n} matched pairs). "
            "Need at least 10 to draw conclusions. Run more questions."
        )
    sig_ca = "p<0.05" in str(p_ca)
    sig_cb = "p<0.05" in str(p_cb)
    pos_ca = d_ca > 0
    pos_cb = d_cb > 0

    if sig_ca and sig_cb and pos_ca and pos_cb:
        if d_ca > 0.5 and d_cb > 0.5:
            return (
                "STRONGLY SUPPORTED — THEOS significantly outperforms both baselines "
                f"with medium-large effect sizes (vs A: d={d_ca:.2f}, vs B: d={d_cb:.2f}). "
                "The core hypothesis is supported."
            )
        elif d_ca > 0.2 and d_cb > 0.2:
            return (
                "SUPPORTED — THEOS significantly outperforms both baselines "
                f"(vs A: d={d_ca:.2f}, vs B: d={d_cb:.2f}). "
                "Core hypothesis is supported with small-medium effect."
            )
    if sig_ca and not sig_cb:
        return (
            "PARTIAL — THEOS beats single-pass (p<0.05) but NOT chain-of-thought. "
            "The improvement may be attributable to prompting structure rather than "
            "the THEOS-specific architecture."
        )
    if not sig_ca and not sig_cb:
        return (
            "NOT SUPPORTED — THEOS did not significantly outperform either baseline. "
            "Report this result honestly. Do not adjust the data."
        )
    if sig_ca and sig_cb and (not pos_ca or not pos_cb):
        return (
            "REVERSED — THEOS scored LOWER than baselines. "
            "This is an important negative result. Investigate why."
        )
    return f"MIXED — Review raw data. (C vs A: {p_ca}) (C vs B: {p_cb})"


# ─── Print report ─────────────────────────────────────────────────────────────

def print_report(analysis: dict, run_meta: dict) -> None:
    print("\n" + "="*70)
    print("THEOS VALIDATION EXPERIMENT — RESULTS REPORT")
    print("="*70)
    print(f"Run ID:     {run_meta.get('experiment_id', '?')}")
    print(f"Model:      {run_meta.get('model', '?')}")
    print(f"Timestamp:  {run_meta.get('timestamp', '?')}")
    print()
    print(f"Questions rated:  A={analysis['n_rated_A']}  B={analysis['n_rated_B']}  C={analysis['n_rated_C']}")
    print(f"Matched pairs: CA={analysis['n_matched_CA']}  CB={analysis['n_matched_CB']}")
    print()
    print("MEAN SCORES (out of 15):")
    print(f"  A — Single-pass:      {analysis['mean_score_A']:.2f}")
    print(f"  B — Chain-of-thought: {analysis['mean_score_B']:.2f}")
    print(f"  C — THEOS two-pass:   {analysis['mean_score_C']:.2f}")
    print()
    print("STATISTICAL TESTS:")
    cva = analysis["C_vs_A"]
    cvb = analysis["C_vs_B"]
    bva = analysis["B_vs_A"]
    print(f"  C vs A: {cva['t_test']} | Cohen's d={cva['cohens_d']} ({cva['effect']}) | mean diff={cva['mean_diff']:+.2f}")
    print(f"  C vs B: {cvb['t_test']} | Cohen's d={cvb['cohens_d']} ({cvb['effect']}) | mean diff={cvb['mean_diff']:+.2f}")
    print(f"  B vs A: {bva['t_test']} | mean diff={bva['mean_diff']:+.2f}")
    print()
    print("VERDICT:")
    print(f"  {analysis['verdict']}")
    print("="*70)
    print()
    print("For rigorous p-values, install scipy and run:")
    print("  from scipy.stats import ttest_rel")
    print("  t, p = ttest_rel(a_scores, c_scores)")


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Score and analyze THEOS validation experiment results"
    )
    parser.add_argument("run_file", help="Path to experiment run JSON file")
    parser.add_argument("--interactive", action="store_true",
                        help="Enter scores interactively")
    parser.add_argument("--output", default=None,
                        help="Save analysis to this JSON file")
    args = parser.parse_args()

    if not os.path.exists(args.run_file):
        print(f"Error: {args.run_file} not found")
        sys.exit(1)

    run = load_run(args.run_file)

    if args.interactive:
        run = interactive_score(run)
        # Save scored run back to file
        save_run(run, args.run_file)

    analysis = analyze(run)
    print_report(analysis, run)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(analysis, f, indent=2)
        print(f"Analysis saved to {args.output}")


if __name__ == "__main__":
    main()
