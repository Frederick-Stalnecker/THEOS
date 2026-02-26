#!/usr/bin/env python3
"""
Run 5 comparison questions through THEOS and save outputs for side-by-side analysis.
"""
import os, sys, json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))
sys.path.insert(0, os.path.dirname(__file__))

from theos_core import TheosCore, TheosConfig
from llm_interface import get_llm

QUESTIONS = [
    "What is the difference between courage and recklessness?",
    "What is the difference between being alone and being lonely?",
    "What makes an apology genuine rather than strategic?",
    "What is the difference between intelligence and wisdom?",
    "Is justice and mercy compatible, or do they ultimately contradict each other?",
]

def build_core(llm):
    config = TheosConfig(max_wringer_passes=2, engine_reflection_depth=2,
                         eps_converge=0.15, eps_partial=0.6, rho_min=0.3, verbose=False)
    token_log = {"total": 0}

    def abduce_left(pattern_I, wisdom_slice):
        wisdom_ctx = ""
        if wisdom_slice:
            wisdom_ctx = "\n\nPrior wisdom:\n" + "\n".join(
                f"- {w.get('summary','')}" for w in wisdom_slice[-2:] if w.get('summary'))
        resp = llm.complete(
            f"You are a constructive analytical engine. Build the strongest, most coherent "
            f"positive case for understanding this question:\n\n{pattern_I}{wisdom_ctx}\n\n"
            f"Provide a clear, well-reasoned hypothesis.", max_tokens=400)
        token_log["total"] += resp.prompt_tokens + resp.completion_tokens
        return resp.text

    def abduce_right(pattern_I, wisdom_slice):
        resp = llm.complete(
            f"You are a critical analytical engine. Identify the deepest flaws, overlooked "
            f"dimensions, and strongest counterarguments:\n\n{pattern_I}\n\n"
            f"Provide the most challenging critical perspective.", max_tokens=400)
        token_log["total"] += resp.prompt_tokens + resp.completion_tokens
        return resp.text

    def deduce(hypothesis):
        resp = llm.complete(
            f"Derive the necessary logical conclusions from this hypothesis. "
            f"What follows with certainty?\n\n{hypothesis}\n\nState conclusions clearly.",
            max_tokens=350)
        token_log["total"] += resp.prompt_tokens + resp.completion_tokens
        return resp.text

    def measure_contradiction(D_L, D_R):
        words_L = set(D_L.lower().split())
        words_R = set(D_R.lower().split())
        common = words_L & words_R
        union = words_L | words_R
        return 1.0 - len(common) / max(len(union), 1)

    import math
    def estimate_entropy(pair):
        A_L, A_R = pair
        wL = set(str(A_L).lower().split()); wR = set(str(A_R).lower().split())
        overlap = len(wL & wR) / max(len(wL | wR), 1)
        return 1.0 - math.exp(-2 * (1 - overlap))

    def estimate_info_gain(phi_new, phi_prev):
        if phi_prev == 0: return 1.0
        return min(2.0, abs(phi_prev - phi_new) / max(phi_prev, 1e-6))

    def retrieve_wisdom(query, W, threshold):
        if not W: return []
        qw = set(query.lower().split())
        return [e for e in W if qw & set(str(e.get('query','')).lower().split())][-3:]

    def update_wisdom(W, query, output, confidence):
        return W + [{"query": query, "summary": str(output)[:150], "confidence": confidence}]

    core = TheosCore(
        config=config,
        encode_observation=lambda q, ctx: q,
        induce_patterns=lambda obs, phi, prior=None: (
            f"{obs}\n[Reflecting: {str(prior)[:150]}]" if prior and phi > 0.1 else obs),
        abduce_left=abduce_left, abduce_right=abduce_right, deduce=deduce,
        measure_contradiction=measure_contradiction,
        retrieve_wisdom=retrieve_wisdom, update_wisdom=update_wisdom,
        estimate_entropy=estimate_entropy, estimate_info_gain=estimate_info_gain,
    )
    return core, token_log


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    llm = get_llm("anthropic", api_key=api_key)
    core, token_log = build_core(llm)

    results = []
    for i, q in enumerate(QUESTIONS, 1):
        print(f"\n[{i}/5] {q}")
        token_log["total"] = 0
        result = core.run_query(q)

        # Extract the two engine outputs from the last wringer pass
        D_L = D_R = ""
        if result.trace:
            last = result.trace[-1]
            if last.left_inner_passes:
                D_L = str(last.left_inner_passes[-1].deduction)
            if last.right_inner_passes:
                D_R = str(last.right_inner_passes[-1].deduction)

        entry = {
            "question": q,
            "theos_answer": str(result.output),
            "constructive_engine": D_L[:500],
            "adversarial_engine": D_R[:500],
            "contradiction": round(result.contradiction, 3),
            "confidence": round(result.confidence, 3),
            "halt_reason": result.halt_reason.value,
            "tokens": token_log["total"],
        }
        results.append(entry)
        print(f"  halt={result.halt_reason.value} | contradiction={result.contradiction:.3f} | tokens={token_log['total']}")
        print(f"  THEOS: {str(result.output)[:200]}...")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"experiments/results/comparison_{ts}.json"
    os.makedirs("experiments/results", exist_ok=True)
    with open(path, "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "results": results}, f, indent=2)
    print(f"\nSaved: {path}")
    return results, path

if __name__ == "__main__":
    results, path = main()
