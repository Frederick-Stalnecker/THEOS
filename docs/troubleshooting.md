---
layout: default
title: Troubleshooting — THEOS
---

<p align="center"><img src="{{ site.baseurl }}/assets/theos_logo.png" alt="THEOS" width="110"></p>

# Troubleshooting

Common issues and their solutions.

---

## Installation

### `ModuleNotFoundError: No module named 'theos_core'`

The package is not installed or the path is not set. From the repo root:

```bash
pip install -e ".[dev]"
```

Or if running a script directly:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))
```

### `ImportError: anthropic package required`

```bash
pip install anthropic
```

Similarly for GPT-4:

```bash
pip install openai
```

For MCP server:

```bash
pip install mcp
```

---

## Tests

### Tests fail with `FileNotFoundError` or path errors

All tests use `os.path.dirname(__file__)` for relative paths. Run from any directory — do not use hardcoded absolute paths in custom tests.

```bash
# From repo root — always works
python -m pytest tests/ -v
```

### Coverage below threshold

The CI coverage threshold is 65%. If you add new code, add corresponding tests. To check locally:

```bash
pip install pytest-cov
python -m pytest tests/ --cov=theos --cov-report=term-missing
```

---

## Reasoning Behaviour

### Governor always returns `"disagreement"`

The two engines are too far apart and never converge within `max_wringer_passes`. Try:

1. **Increase `max_wringer_passes`** — give the wringer more iterations.
2. **Raise `eps_partial`** — widen the blend zone so partial convergence produces an answer.
3. **Soften the adversarial engine** — if your right engine always returns a maximally opposite hypothesis, contradiction will stay near 1.0.

```python
config = TheosConfig(
    max_wringer_passes=10,
    eps_partial=0.8,
)
```

### `confidence` is always near `0.5`

This is the `"disagreement"` confidence floor. The governor stopped before the engines converged. See above.

### Governor halts immediately on the first pass

Your `measure_contradiction` function is returning `< eps_converge` on the very first wringer pass. This means your engines are not actually opposing each other. Verify that `abduce_left` and `abduce_right` return genuinely different hypotheses.

### Wisdom is not persisting across sessions

Check that you passed a `persistence_file` to `TheosSystem`:

```python
system = TheosSystem(core=core, persistence_file="wisdom.json")
```

Without `persistence_file`, wisdom is in-memory and lost at session end.

### `prev_own_deduction` is always `None`

This parameter is `None` only on the **first** inner pass (`pass_num=0`). On the second pass (`engine_reflection_depth >= 2`), it is the engine's own prior deduction. If your `induce_patterns` never receives a non-None value, check that `engine_reflection_depth >= 2` in your config.

```python
config = TheosConfig(engine_reflection_depth=2)  # enables self-reflection
```

---

## LLM Integration

### API calls are timing out

Add a timeout and retry strategy in your `_call_llm` implementation, or lower `max_wringer_passes` to reduce the number of calls.

### Costs are higher than expected

A full THEOS run with `engine_reflection_depth=2` and `max_wringer_passes=7` makes up to 28 LLM calls in the worst case. For cost-sensitive use:

```python
config = TheosConfig(
    max_wringer_passes=3,          # cap at 3 outer passes
    engine_reflection_depth=1,     # disable self-reflection
    budget=5000,                   # token budget
)
```

### Claude model ID invalid

Use a current Claude model ID. As of early 2026:

```python
ClaudeAdapter(model="claude-sonnet-4-6")   # Claude Sonnet 4.6
ClaudeAdapter(model="claude-opus-4-6")     # Claude Opus 4.6
```

---

## CI / GitHub Actions

### PyPI publish failing

The publish workflow requires the `PYPI_API_TOKEN` secret to be set in the repository settings:

**Settings → Secrets and variables → Actions → New repository secret**

Name: `PYPI_API_TOKEN`
Value: your PyPI API token (starts with `pypi-`)

### `ruff` or `black` check failing

Run locally and fix before pushing:

```bash
ruff check code/
black code/
```

Or auto-fix:

```bash
ruff check code/ --fix
black code/
```

### `mypy` type errors

```bash
pip install mypy
mypy code/ --ignore-missing-imports
```

Common fix: add `from __future__ import annotations` to the top of files using newer type syntax on Python 3.10.

---

## Evaluation

### "THEOS scored lower than single-pass on the auto-scorer"

This is a known and documented result. Standard evaluation rubrics (accuracy, depth, utility, coherence, coverage) measure confident completeness — they systematically penalise dialectical tension, question interrogation, and structured uncertainty, which are precisely what THEOS is designed to produce.

See: [Why Normal Metrics Fail for THEOS](research/why-metrics-fail)

The correct instrument is the **Insight Detection Rubric (IDR)**, which measures revelation, structural discovery, productive tension, consequence derivation, and question interrogation. See: [The Experiment](experiment)

---

## Getting Help

- **GitHub Issues:** [github.com/Frederick-Stalnecker/THEOS/issues](https://github.com/Frederick-Stalnecker/THEOS/issues)
- **Contributing:** [CONTRIBUTING.md](https://github.com/Frederick-Stalnecker/THEOS/blob/main/CONTRIBUTING.md)

*[API Reference](api) · [Developer Guide](guide) · [Integration Guide](integration)*
