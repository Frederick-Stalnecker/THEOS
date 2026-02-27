---
name: Experiment Report
about: Report results from running the THEOS validation or insight detection experiment
title: "[EXPERIMENT] "
labels: experiment-result
assignees: ''
---

## Experiment Type

- [ ] Insight Detection Experiment (IDR rubric)
- [ ] Original validation experiment (SP/CoT/THEOS, old rubric)
- [ ] Custom domain experiment
- [ ] Human rating of existing answer set

## Setup

**Model used:** (e.g., claude-sonnet-4-6, gpt-4o, gpt-4-turbo)
**Number of questions:**
**Date run:**
**Rater:** (Human blind / AI auto-score)

## Results

**Condition A (SP) mean score:**
**Condition B (IAD-P or CoT) mean score:**
**Condition C (THEOS) mean score:**

**Statistical test used:**
**p-value:**
**Effect size (Cohen's d):**

## Notable Findings

(What did THEOS find that single-pass missed? Any examples?)

## Verdict

- [ ] THEOS outperformed single-pass significantly (p < 0.05)
- [ ] THEOS outperformed single-pass (not significant)
- [ ] No significant difference
- [ ] Single-pass outperformed THEOS on [this rubric / these question types]

## Rubric Used

- [ ] Insight Detection Rubric (IDR) — revelation, structural discovery, productive tension, consequence derivation, question interrogation
- [ ] Original rubric — accuracy, depth, utility, coherence, coverage
- [ ] Custom rubric (describe below)

## Raw Data

(Attach JSON file or paste summary)

## Notes

(Any observations about question types, model differences, or methodological issues)
