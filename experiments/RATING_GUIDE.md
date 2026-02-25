# Human Rating Guide — THEOS Validation Experiment

## Purpose

This guide allows a human rater to evaluate the quality of answers produced by
three reasoning conditions. The rater does **not** know which condition produced
which answer. This blind rating is essential for unbiased results.

## The Three Conditions (Revealed After Rating)

| Label | Condition |
|-------|-----------|
| X | Condition A: Single-pass (direct answer) |
| Y | Condition B: Chain-of-thought ("think step by step") |
| Z | Condition C: THEOS two-pass I→A→D→I |

**Do not read the label reveal until you have finished rating all answers.**

---

## Scoring Rubric

Rate each answer on five dimensions. Each dimension is scored 0–3.

### 1. Accuracy (0–3)

Does the answer make logically sound, defensible claims?

| Score | Description |
|-------|-------------|
| 0 | Contains logical errors or significant inaccuracies |
| 1 | Mostly correct but has minor errors or overstatements |
| 2 | Correct with no notable errors |
| 3 | Correct and explicitly handles edge cases or exceptions |

### 2. Depth (0–3)

Does the answer go beyond surface-level description?

| Score | Description |
|-------|-------------|
| 0 | Surface-level only (restates the question or gives a one-liner) |
| 1 | Adds some explanation but stays at a single layer of analysis |
| 2 | Reveals an underlying mechanism or structure |
| 3 | Reveals an insight that meaningfully changes how you understand the topic |

**What counts as depth?** In the egotism/arrogance example:
- Score 0–1: "Egotism is internal, arrogance is external"
- Score 2–3: "They are orthogonal failures on different dimensions — you can have one without the other"

### 3. Utility (0–3)

Is the answer practically useful? Could someone act differently because of it?

| Score | Description |
|-------|-------------|
| 0 | Provides no practical guidance |
| 1 | Vaguely applicable |
| 2 | Clearly applicable to real situations |
| 3 | Provides a framework or tool the reader can immediately apply |

### 4. Coherence (0–3)

Is the answer well-organized and internally consistent?

| Score | Description |
|-------|-------------|
| 0 | Contradicts itself or is disorganized |
| 1 | Mostly coherent with minor inconsistencies |
| 2 | Clear and well-organized |
| 3 | Exceptionally clear with logical flow from premise to conclusion |

### 5. Coverage (0–3)

Does the answer address multiple dimensions of the question?

| Score | Description |
|-------|-------------|
| 0 | Addresses only one dimension |
| 1 | Addresses two dimensions |
| 2 | Addresses three or more dimensions |
| 3 | Addresses all major dimensions and notes their interactions |

---

## Scoring Sheet Template

For each question, fill in the scores for each labeled answer:

```
Question [ID]: [Question text]

         | Acc | Dep | Uti | Coh | Cov | TOTAL
Answer X |     |     |     |     |     |
Answer Y |     |     |     |     |     |
Answer Z |     |     |     |     |     |
```

**Maximum score per answer: 15**

---

## Important Instructions

1. **Rate each answer independently.** Do not compare them to each other — rate
   against the rubric, not against each other.

2. **Use the full scale.** If you never give a 3 or a 0, your ratings are
   probably compressed. Both endpoints are valid.

3. **If two answers seem equal, give them equal scores.** Do not artificially
   differentiate.

4. **Reveal the labels only after you have finished all ratings.**

5. **If you change a score after the reveal, document why.** This is important
   for scientific integrity.

---

## What Counts as a Fair Test

The hypothesis being tested is: does the THEOS two-pass process produce
better answers? A fair test requires:

- The rater genuinely does not know which is which during rating
- The question is open-ended and conceptual (not a factual lookup)
- The underlying LLM is capable enough to execute the reasoning steps
  (distilgpt2 is NOT capable; Claude or GPT-4 is)

If THEOS does not outperform the baselines, that is a valid finding.
Report it honestly. Do not adjust scores to support the hypothesis.

---

## After Rating: Enter Scores

Edit the results JSON file and add scores to each ConditionResult:

```json
{
  "condition": "C_theos_two_pass",
  "question_id": 1,
  "answer": "...",
  "score_accuracy": 3,
  "score_depth": 3,
  "score_utility": 2,
  "score_coherence": 2,
  "score_coverage": 2
}
```

Then run analysis:
```bash
python experiments/score_results.py experiments/results/run_YYYYMMDD_HHMMSS.json
```
