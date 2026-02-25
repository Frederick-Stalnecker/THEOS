# THEOS — Triadic Hierarchical Emergent Optimization System

[![Tests](https://img.shields.io/badge/tests-71%2F71-brightgreen)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](#)

> *A structured recursive reasoning framework for AI systems.*

---

## What THEOS Is

THEOS is a runtime methodology for AI reasoning that structures thought in a
circular I→A→D→I cycle rather than a linear pass:

```
        Induction (12 o'clock)
            ↗           ↘
Deduction (8)       Abduction (4)
            ↖           ↙
    [Feed deduction back into induction]
```

**The core mechanism:**
1. **Induction** — extract patterns from observations
2. **Abduction** — form the best explanatory hypothesis
3. **Deduction** — derive conclusions from the hypothesis
4. **→ Induction again** — treat the deduction as a new observation

On the second pass, the system reasons about what it just reasoned.
This creates a functional "momentary past" — the deduction of cycle N
becomes the starting observation of cycle N+1.

**Two engines run in parallel:**
- **Engine L (Constructive)** — builds the case for a conclusion
- **Engine R (Deconstructive)** — challenges and critiques Engine L

**A governor controls the process:**
- Measures contradiction between engines
- Halts when engines converge, budget is exhausted, or quality stops improving
- Tracks posture states: NOM → PEM → CM → IM

---

## What Is Demonstrated

**The two-pass mechanism produces better answers on open-ended conceptual questions.**

Example (egotism vs. arrogance):
- **Single-pass:** "Egotism is internal, arrogance is external"
- **After two-pass I→A→D→I:** "They are orthogonal failures on different dimensions.
  Egotism distorts self-perception. Arrogance distorts other-perception.
  You can have one without the other."

The second answer is a 2×2 matrix where the first was a line. It explains
something the first cannot: why a person can be humble about themselves
while contemptuous of others.

See `research/VALIDATED_FINDINGS.md` for a complete account of what
is and is not demonstrated.

---

## What Is Not Yet Demonstrated

- The magnitude of quality improvement vs. chain-of-thought prompting
- Performance metrics (speed, token efficiency) — the existing benchmark
  shows THEOS is **slower** on first pass (multi-cycle cost), faster on
  repeat queries (caching). See `experiments/BENCHMARK_ANALYSIS.md`.
- Consciousness or metacognitive claims — these are philosophical
  interpretations, not scientific findings

---

## The Validation Experiment

The quality experiment is ready to run. It requires an API key:

```bash
# Install
pip install -e ".[dev]"

# Quick framework test (no API needed)
python experiments/theos_validation_experiment.py --backend mock --questions 3

# Real experiment with Claude
export ANTHROPIC_API_KEY=sk-ant-...
python experiments/theos_validation_experiment.py \
    --backend anthropic \
    --questions 30 \
    --conditions ABC \
    --print-for-rating
```

Rate answers using `experiments/RATING_GUIDE.md`.

---

## Repository Structure

```
THEOS2/
├── code/                    # Core package (pip-installable as 'theos')
│   ├── theos_governor.py    # Unified governor — canonical implementation
│   ├── theos_core.py        # TheosCore — I→A→D→I reasoning loop
│   ├── theos_system.py      # TheosSystem + create_numeric_system()
│   └── semantic_retrieval.py # VectorStore + embedding adapters
├── examples/                # Domain engines (medical, financial, AI safety)
├── tests/                   # 71 passing tests
├── experiments/             # Validation experiment framework
│   ├── theos_validation_experiment.py  # Quality experiment
│   ├── question_bank.py               # 30 open-ended test questions
│   ├── llm_interface.py               # LLM adapters (mock/Claude/GPT-4)
│   ├── BENCHMARK_ANALYSIS.md          # Honest benchmark analysis
│   └── RATING_GUIDE.md                # Human rating rubric
├── research/
│   ├── VALIDATED_FINDINGS.md          # What is known vs. what needs testing
│   ├── MATHEMATICAL_AUDIT.md          # Claim-by-claim audit
│   └── Transcripts/                   # Session transcripts (primary evidence)
└── archive/
    ├── antique_learning/              # Prior AI-generated work (preserved)
    └── aspirational/                  # Unclaimed performance claims
```

---

## Installation

```bash
pip install -e ".[dev]"           # Editable install with dev tools
pip install -e ".[mcp]"           # MCP server support
pip install -e ".[vector]"        # Vector store (chromadb / faiss)
```

**Requirements:** Python 3.10+, zero external dependencies for core.

---

## Running Tests

```bash
python3.12 -m pytest tests/ -v
```

---

## Status

Architecture clean. Governor tested (71/71). Core mechanism demonstrated.
**Quality experiment is the next critical step.**

Not open-sourcing until results are convincing and not inflated.

---

## Author

Frederick Davis Stalnecker — Patent pending: USPTO #63/831,738

> *From truth we build more truth.*
