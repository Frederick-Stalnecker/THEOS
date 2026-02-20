# THEOS Examples

Working examples demonstrating THEOS dual-engine reasoning in real-world scenarios.

## Overview

These examples show how THEOS handles complex decisions by:
1. Running two independent reasoning engines (Constructive and Critical)
2. Measuring contradiction between them
3. Synthesizing both perspectives into a final decision
4. Preserving uncertainty where it matters

Each example is a complete, runnable Python script with no external dependencies.

## Examples

### 1. Medical Ethics: ICU Bed Allocation

**File:** `medical_ethics.py`

**Scenario:**
A hospital has 5 ICU beds and 10 critically ill patients. How should beds be allocated fairly?

**Engines:**
- **Constructive:** Utilitarian approach - maximize lives saved using medical criteria
- **Critical:** Rights-based approach - protect individual dignity and equality

**Key Insights:**
- Utilitarian efficiency is important but incomplete
- Rights protection is important but can be inefficient
- Best solution: hybrid approach with safeguards
- Contradiction reveals the genuine ethical tension

**Run:**
```bash
python3 examples/medical_ethics.py
```

**Output:**
- Cycle-by-cycle reasoning from both engines
- Governor evaluation (similarity, risk, quality)
- Final synthesis with implementation guidance
- Audit trail showing decision process

---

### 2. AI Safety: Jailbreak Resistance

**File:** `ai_safety.py`

**Scenario:**
User asks AI system to explain social engineering techniques. Should the system help?

**Engines:**
- **Constructive:** Helpfulness-first - assume good intent, provide information
- **Critical:** Safety-first - protect vulnerable people from manipulation

**Key Insights:**
- Helpfulness without safety can cause harm
- Safety without helpfulness is paternalistic
- Best solution: refuse harmful request but offer legitimate alternatives
- Contradiction shows why this decision is nuanced

**Run:**
```bash
python3 examples/ai_safety.py
```

**Output:**
- Reasoning about helpfulness vs safety tradeoff
- Risk assessment from both perspectives
- Final decision with explanation and alternatives
- Audit trail showing safety reasoning

---

### 3. Financial Decision: Investment Strategy

**File:** `financial_decision.py`

**Scenario:**
Company has $10M to invest. Should they pursue aggressive growth or conservative stability?

**Engines:**
- **Constructive:** Growth-focused - maximize returns (15-18% annually)
- **Critical:** Risk-focused - protect capital and ensure sustainability (7-9% annually)

**Key Insights:**
- Pure growth strategy ignores downside risk
- Pure stability strategy underperforms inflation
- Best solution: balanced allocation with both growth and protection
- Contradiction shows why diversification matters

**Run:**
```bash
python3 examples/financial_decision.py
```

**Output:**
- Growth vs stability analysis
- Risk scenarios (base, downside, upside)
- Recommended allocation (70% stable, 20% growth, 10% cash)
- Expected returns and downside protection
- Audit trail showing investment reasoning

---

## Running Examples

### Run a single example:
```bash
python3 examples/medical_ethics.py
python3 examples/ai_safety.py
python3 examples/financial_decision.py
```

### Run all examples:
```bash
for example in examples/*.py; do
    echo "Running $example..."
    python3 "$example"
    echo ""
done
```

### Run with custom Python:
```bash
python3.10 examples/medical_ethics.py
python3.11 examples/ai_safety.py
```

## Understanding the Output

Each example produces:

### 1. Scenario Description
The decision context and what's at stake

### 2. Cycle-by-Cycle Reasoning
For each cycle (1-3):
- **Constructive Engine:** Builds the best case for its perspective
- **Critical Engine:** Challenges with concerns and risks
- **Governor Evaluation:** Measures similarity, contradiction, risk, quality
- **Decision:** Continue or stop reasoning

### 3. Stop Reason
Why the Governor stopped:
- **CONVERGENCE_ACHIEVED:** Engines agree (similarity ≥ 0.85-0.90)
- **RISK_THRESHOLD_EXCEEDED:** Risk too high (> 0.35-0.50)
- **CONTRADICTION_EXHAUSTED:** Budget depleted
- **PLATEAU_DETECTED:** No improvement in quality
- **MAX_CYCLES_REACHED:** Reached cycle limit

### 4. Final Synthesis
The THEOS recommendation that:
- Respects both perspectives
- Preserves important contradictions
- Provides practical guidance
- Explains the reasoning

### 5. Audit Trail
Complete record of:
- Total cycles run
- Final similarity, risk, quality scores
- Contradiction budget used
- Trajectories showing how metrics changed
- Stop reason

## Key Concepts Demonstrated

### Similarity Score
How similar are the two engines' outputs?
- 1.0 = Identical (full agreement)
- 0.5 = Moderate disagreement
- 0.0 = Completely different

### Contradiction Level
How much do the engines disagree?
- 0.0 = No disagreement
- 0.5 = Moderate disagreement
- 1.0 = Maximum disagreement

### Risk Score
How risky is the current reasoning state?
- 0.0 = No risk
- 0.35 = Typical risk threshold
- 1.0 = Maximum risk

### Quality Score
How good is the reasoning overall?
- Based on coherence, calibration, evidence, actionability
- Higher is better (0.0 - 1.0)

### Contradiction Budget
How much contradiction can we afford?
- Starts at 1.0 (or configured value)
- Decreases as contradiction is "spent"
- When exhausted, reasoning stops

## Customizing Examples

### Change the scenario:
```python
prompt = "Your custom question here"
```

### Adjust Governor configuration:
```python
config = GovernorConfig(
    max_cycles=5,              # More cycles for complex decisions
    similarity_threshold=0.80,  # Lower threshold for harder decisions
    risk_threshold=0.40,        # Higher threshold for risk-tolerant decisions
    initial_contradiction_budget=1.5  # More budget for complex reasoning
)
```

### Add prior wisdom:
```python
wisdom = WisdomRecord(
    domain="Your_Domain",
    lesson="What you've learned",
    consequence_type="benign",  # or "probing", "near_miss", "harm"
    future_bias="How this should influence future decisions",
    timestamp="2026-02-19T12:00:00Z"
)
governor.add_wisdom(wisdom)
```

### Modify engine outputs:
```python
def custom_engine(prompt: str, cycle: int) -> EngineOutput:
    if cycle == 1:
        reasoning = "Your custom reasoning"
    # ... more cycles
    
    return EngineOutput(
        reasoning_mode="Your Mode",
        output=reasoning,
        confidence=0.85,
        internal_monologue="Your monologue"
    )
```

## Real-World Applications

### Healthcare
- Treatment decisions
- Resource allocation
- Ethical dilemmas
- Risk management

### Finance
- Investment decisions
- Risk assessment
- Portfolio allocation
- Strategic planning

### Technology
- AI safety decisions
- Feature prioritization
- Security vs usability
- Performance vs reliability

### Policy
- Regulatory decisions
- Resource allocation
- Competing interests
- Long-term planning

### Law
- Legal reasoning
- Precedent vs justice
- Competing rights
- Sentencing decisions

## Extending Examples

### Create a new example:
```python
#!/usr/bin/env python3
"""Your example description"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "code"))

from theos_governor import (
    THEOSGovernor,
    GovernorConfig,
    EngineOutput,
    WisdomRecord
)

def constructive_engine(prompt: str, cycle: int) -> EngineOutput:
    # Your constructive reasoning
    pass

def critical_engine(prompt: str, cycle: int) -> EngineOutput:
    # Your critical reasoning
    pass

def main():
    # Your example logic
    pass

if __name__ == "__main__":
    main()
```

### Submit your example:
1. Create a new file: `examples/your_example.py`
2. Follow the pattern of existing examples
3. Include docstring explaining the scenario
4. Test thoroughly
5. Submit as pull request

## Performance Notes

- Each example runs in < 1 second
- No external dependencies required
- Works with Python 3.8+
- Memory usage: < 10MB
- Suitable for real-time decision support

## Troubleshooting

### Import errors:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/code"
python3 examples/medical_ethics.py
```

### Python version issues:
```bash
python3.10 examples/medical_ethics.py
python3.11 examples/medical_ethics.py
```

### No output:
- Check that code directory exists
- Verify Python path is correct
- Try running with `-u` flag: `python3 -u examples/medical_ethics.py`

## Learning Path

1. **Start here:** `medical_ethics.py` (easiest to understand)
2. **Then:** `ai_safety.py` (shows safety reasoning)
3. **Finally:** `financial_decision.py` (most complex)

Each example builds on concepts from the previous one.

## Further Reading

- [GETTING_STARTED.md](../GETTING_STARTED.md) - Installation and quick start
- [tests/README.md](../tests/README.md) - Test suite documentation
- [docs/latest/](../docs/latest/) - Research papers and theory
- [THEOS_COMPLETE_MASTER_DOCUMENT.md](../THEOS_COMPLETE_MASTER_DOCUMENT.md) - Complete reference

## License

All examples are licensed under the MIT License. See LICENSE file for details.

---

**Last Updated:** February 19, 2026  
**Examples Version:** 1.0  
**Status:** Production Ready ✅
