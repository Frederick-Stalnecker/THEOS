---
layout: default
title: The Experiment — THEOS
---

# The Experiment

## What We Are Testing

THEOS's core claim is:

> **Dialectical two-engine reasoning finds structure that a single inference step cannot find — systematically, not occasionally.**

The egotism/arrogance case demonstrates this once. The experiment is designed to test whether it holds at scale.

---

## Why the First Experiment Was Wrong

The February 2026 auto-scoring experiment (30 questions, scored by Claude on accuracy/depth/utility/coherence/coverage) produced a reversed result: THEOS 9.77/15, single-pass 14.03/15.

This was a measurement failure, not a THEOS failure.

The rubric rewarded confident completeness. THEOS produces dialectical tension and structural discovery. The instrument did not match the phenomenon.

→ [Full explanation: Why Normal Metrics Fail for THEOS](research/why-metrics-fail)

---

## The Insight Detection Rubric (IDR)

The new rubric measures what THEOS claims to produce:

| Dimension | The question it answers |
|-----------|------------------------|
| **Revelation** (0–3) | After reading this answer, do you understand something you genuinely did not before? |
| **Structural Discovery** (0–3) | Did it find dimensions or axes hidden in the question? |
| **Productive Tension** (0–3) | Does it hold two perspectives in tension and produce something neither alone could? |
| **Consequence Derivation** (0–3) | Does it derive non-trivial consequences that follow from the structure found? |
| **Question Interrogation** (0–3) | Does it name a hidden assumption that changes the answer? |

**Maximum: 15 points.** Same scale as before, fundamentally different dimensions.

---

## The New Experiment Design

Three conditions, 30 questions each:

| Label | Condition | LLM Calls | Purpose |
|-------|-----------|-----------|---------|
| A — SP | Direct single-pass answer | 1 | Baseline |
| B — IAD-P | Single prompt explicitly asking for I→A→D structure | 1 | Isolates structure from iteration |
| C — THEOS | Full two-engine multi-pass I→A→D | 6–12 | Full framework |

**The B condition is new.** It controls for number of LLM calls. The same underlying model is asked to follow the I→A→D structure in a single structured prompt — isolating whether the *structure* alone produces insight.

Four possible outcomes, all informative:
- A < B < C: Structure helps; iteration adds more. Full THEOS thesis supported.
- A < B ≈ C: Structure alone is sufficient; multi-pass overhead may not be needed.
- A ≈ B < C: Multi-pass iteration drives discovery; structure alone doesn't help.
- A ≈ B ≈ C: Null result; re-examine question types.

---

## How to Contribute Results

The experiment framework is ready. We need:

**Option 1 — Run the experiment yourself:**
```bash
git clone https://github.com/Frederick-Stalnecker/THEOS.git
cd THEOS
export ANTHROPIC_API_KEY=sk-ant-...
python3 experiments/insight_experiment.py --backend anthropic --questions 10
```

Rate the answers using the [Insight Detection Rubric](https://github.com/Frederick-Stalnecker/THEOS/blob/main/experiments/INSIGHT_RUBRIC.md) and [open an issue](https://github.com/Frederick-Stalnecker/THEOS/issues/new?template=experiment-report.md) with your results.

**Option 2 — Rate existing answers:**
The 30-question answer set (SP / CoT / THEOS) from February 2026 is in:
`experiments/results/run_20260226_194058.json`

Rate them using the IDR rubric (blind — you don't see which condition produced which answer until after rating). [Open an issue](https://github.com/Frederick-Stalnecker/THEOS/issues/new?template=experiment-report.md) with your ratings.

**Option 3 — Run on your domain:**
Have a domain where dialectical reasoning matters? (Law, medicine, strategy, ethics, research?) Run the experiment on your own questions and report what you find.

---

## Current Status

| Item | Status |
|------|--------|
| 30-question answer set generated | ✓ Complete |
| Auto-scored (wrong instrument) | ✓ Complete — negative result on wrong metric |
| Human rating with IDR | Pending |
| Insight Detection Experiment run | Ready to run |
| Statistical analysis | Pending first IDR data |

---

*The experiment is honest. If THEOS does not outperform single-pass on the IDR, we will report that. If it does, we will report that. We are here to find out.*
