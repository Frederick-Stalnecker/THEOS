# Contributing to THEOS

Thank you for your interest. THEOS is an early-stage research framework. Contributions
that advance the science honestly are welcome. Contributions that inflate claims are not.

---

## What We Need Most

### 1. Quality experiment runs
Run the validation experiment with your own API key and submit your rated results:

```bash
python experiments/theos_validation_experiment.py --backend anthropic --questions 30
python experiments/score_results.py experiments/results/your_run.json
```

Share your results as a GitHub Discussion. Every honest data point strengthens or
weakens the claim — both outcomes are valuable.

### 2. Domain implementations
Build a THEOS engine for a domain you know well (legal reasoning, scientific hypothesis
testing, clinical decision support, financial risk). Use the injection pattern in
`examples/` as your template. Submit as a PR to `examples/`.

### 3. Native architecture
The biggest open research question: can THEOS be implemented natively inside a
transformer's inference loop (using KV cache for inner passes, hidden states for
contradiction measurement)? If you have the background to attempt this, open a
Discussion first.

### 4. Bug reports and test coverage
Open an issue with a minimal reproduction case. All core claims should be testable.

---

## What We Don't Need

- Performance claims without measured data
- Comparisons to other frameworks that haven't been run head-to-head
- "Improvements" to the architecture that haven't been validated experimentally
- Consciousness or sentience claims — these are not scientific

---

## How to Submit

1. Fork the repository
2. Create a branch: `git checkout -b your-feature`
3. Write tests for new functionality
4. Ensure all existing tests pass: `python -m pytest tests/ -v`
5. Submit a pull request with a clear description of what you measured or built

---

## Code Standards

- Python 3.10+, no external dependencies for `code/` (core)
- Type annotations on public functions
- Docstrings explaining *why*, not just *what*
- No fabricated benchmarks — if you can't measure it, say so

---

## Questions

Open a GitHub Discussion. We read everything.

---

*Frederick Davis Stalnecker — inventor*
*Patent pending: USPTO #63/831,738*
