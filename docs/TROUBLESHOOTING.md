# THEOS Troubleshooting Guide

Common issues and solutions for THEOS.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Runtime Issues](#runtime-issues)
3. [Quality Issues](#quality-issues)
4. [Performance Issues](#performance-issues)
5. [FAQ](#faq)

---

## Installation Issues

### Issue: Import Error - Module Not Found

**Error:** `ModuleNotFoundError: No module named 'theos_governor'`

**Cause:** THEOS code directory not in Python path.

**Solution:**

```python
import sys
from pathlib import Path

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent / "code"))

from theos_governor import THEOSGovernor
```

Or set PYTHONPATH:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/code"
python3 your_script.py
```

---

### Issue: Dependency Error

**Error:** `ImportError: No module named 'dataclasses'`

**Cause:** Using Python < 3.7 (dataclasses added in 3.7).

**Solution:** Upgrade Python:

```bash
python3 --version  # Check version
python3.10 your_script.py  # Use newer version
```

---

### Issue: Permission Denied

**Error:** `PermissionError: [Errno 13] Permission denied`

**Cause:** File permissions issue.

**Solution:**

```bash
# Make files readable
chmod +r code/*.py

# Make directory readable
chmod +rx code/
```

---

## Runtime Issues

### Issue: ValueError - Invalid Confidence

**Error:** `ValueError: Confidence must be between 0 and 1`

**Cause:** Confidence value outside [0, 1] range.

**Solution:**

```python
# ❌ Wrong
output = EngineOutput(
    reasoning_mode="Constructive",
    output="...",
    confidence=1.5,  # ERROR!
    internal_monologue="..."
)

# ✅ Correct
output = EngineOutput(
    reasoning_mode="Constructive",
    output="...",
    confidence=0.85,  # Valid [0, 1]
    internal_monologue="..."
)
```

---

### Issue: ValueError - Empty Output

**Error:** `ValueError: Output cannot be empty`

**Cause:** Empty string in output field.

**Solution:**

```python
# ❌ Wrong
output = EngineOutput(
    reasoning_mode="Constructive",
    output="",  # ERROR!
    confidence=0.85,
    internal_monologue="..."
)

# ✅ Correct
output = EngineOutput(
    reasoning_mode="Constructive",
    output="This is my reasoning...",
    confidence=0.85,
    internal_monologue="..."
)
```

---

### Issue: ValueError - Invalid Threshold

**Error:** `ValueError: Similarity threshold must be between 0 and 1`

**Cause:** Configuration parameter outside valid range.

**Solution:**

```python
# ❌ Wrong
config = GovernorConfig(similarity_threshold=1.5)  # ERROR!

# ✅ Correct
config = GovernorConfig(similarity_threshold=0.90)  # Valid [0, 1]
```

---

### Issue: NoneType Error

**Error:** `AttributeError: 'NoneType' object has no attribute ...`

**Cause:** Accessing attribute on None value.

**Solution:**

```python
# ❌ Wrong
evaluation = governor.evaluate_cycle(left, right, 1.0, 1)
print(evaluation.stop_reason.value)  # ERROR if stop_reason is None!

# ✅ Correct
evaluation = governor.evaluate_cycle(left, right, 1.0, 1)
if evaluation.stop_reason:
    print(evaluation.stop_reason.value)
else:
    print("No stop reason")
```

---

## Quality Issues

### Issue: Low Similarity Score

**Problem:** Engines always disagree (similarity < 0.5).

**Cause:** Engines are too different or outputs are poor quality.

**Solution:**

1. **Improve engine outputs:**
   ```python
   # Ensure outputs are substantive and coherent
   output = EngineOutput(
       reasoning_mode="Constructive",
       output="""
       Detailed analysis:
       1. Evidence: ...
       2. Reasoning: ...
       3. Conclusion: ...
       """,
       confidence=0.85,
       internal_monologue="Detailed reasoning"
   )
   ```

2. **Adjust configuration:**
   ```python
   config = GovernorConfig(
       similarity_threshold=0.70,  # Lower threshold
       max_cycles=5  # More cycles to converge
   )
   ```

3. **Check engine alignment:**
   - Are engines addressing the same question?
   - Are they using compatible reasoning frameworks?

---

### Issue: High Risk Score

**Problem:** Governor stops due to high risk (> threshold).

**Cause:** Reasoning state is risky or engines are misaligned.

**Solution:**

1. **Improve engine quality:**
   ```python
   # Ensure outputs are well-reasoned and evidence-based
   ```

2. **Adjust risk threshold:**
   ```python
   config = GovernorConfig(risk_threshold=0.50)  # Higher threshold
   ```

3. **Reduce contradiction budget:**
   ```python
   config = GovernorConfig(
       initial_contradiction_budget=0.8,  # Lower budget
       contradiction_decay_rate=0.20  # Faster depletion
   )
   ```

---

### Issue: Low Quality Scores

**Problem:** Composite quality is low (< 0.5).

**Cause:** Engine outputs lack coherence, calibration, evidence, or actionability.

**Solution:**

1. **Improve coherence:**
   - Structure outputs logically
   - Use clear reasoning chains
   - Avoid contradictions within single output

2. **Improve calibration:**
   - Match confidence to actual quality
   - Don't overstate certainty
   - Acknowledge limitations

3. **Improve evidence:**
   - Ground claims in data
   - Reference sources
   - Provide examples

4. **Improve actionability:**
   - Provide clear recommendations
   - Explain implementation steps
   - Address feasibility

---

## Performance Issues

### Issue: Slow Similarity Computation

**Problem:** `compute_similarity()` takes > 100ms.

**Cause:** Very long outputs or inefficient implementation.

**Solution:**

1. **Reduce output length:**
   ```python
   # Limit output to key points
   output = EngineOutput(
       reasoning_mode="Constructive",
       output="Key points: 1. ... 2. ... 3. ...",  # Concise
       confidence=0.85,
       internal_monologue="..."
   )
   ```

2. **Cache results:**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=1000)
   def cached_similarity(left: str, right: str) -> float:
       return governor.compute_similarity(left, right)
   ```

3. **Use approximate matching:**
   - For very long texts, use sampling
   - Compare key sections instead of full text

---

### Issue: High Memory Usage

**Problem:** Governor uses > 100MB memory.

**Cause:** Large audit trails or many wisdom records.

**Solution:**

1. **Limit cycle history:**
   ```python
   config = GovernorConfig(max_cycles=3)  # Fewer cycles
   ```

2. **Clear old wisdom:**
   ```python
   governor.reset()  # Clear all state
   ```

3. **Batch process:**
   ```python
   # Process decisions one at a time
   # Don't accumulate in memory
   ```

---

### Issue: Slow Evaluation

**Problem:** `evaluate_cycle()` takes > 500ms.

**Cause:** Complex quality calculations or large inputs.

**Solution:**

1. **Reduce input size:**
   - Limit output length
   - Summarize key points

2. **Simplify quality metrics:**
   - Use fewer metrics
   - Skip expensive calculations

3. **Optimize configuration:**
   ```python
   config = GovernorConfig(
       max_cycles=2,  # Fewer cycles
       quality_improvement_threshold=0.10  # Less strict
   )
   ```

---

## FAQ

### Q: What's the difference between Constructive and Critical engines?

**A:** Constructive engine builds the best case for an approach. Critical engine challenges it with concerns and risks. Together, they explore the decision space more thoroughly than either alone.

---

### Q: When should I use THEOS vs. a simple decision tree?

**A:** Use THEOS when:
- Decision involves genuine contradictions
- You need to preserve multiple perspectives
- Auditability is important
- You want to learn from consequences

Use decision trees when:
- Decision is simple and deterministic
- All relevant factors are known
- Speed is critical
- Interpretability is less important

---

### Q: How do I know if my configuration is good?

**A:** Monitor these metrics:

| Metric | Good Range | Action |
|--------|-----------|--------|
| Similarity | 0.70-0.95 | Adjust threshold if outside |
| Risk | 0.20-0.40 | Reduce if > 0.40, increase if < 0.20 |
| Quality | 0.60-0.90 | Improve outputs if < 0.60 |
| Cycles to convergence | 2-4 | Adjust budget if > 4 |

---

### Q: Can I use THEOS for real-time decisions?

**A:** Yes, with caveats:
- THEOS is fast (< 200ms for 3 cycles)
- Suitable for decisions with 100ms-1s latency budget
- Not suitable for < 10ms latency requirements
- Cache engine outputs for faster processing

---

### Q: How do I integrate THEOS with an LLM?

**A:** Use LLM to generate engine outputs:

```python
from openai import OpenAI

client = OpenAI()

def get_constructive_analysis(prompt: str) -> EngineOutput:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a constructive analyzer..."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return EngineOutput(
        reasoning_mode="Constructive",
        output=response.choices[0].message.content,
        confidence=0.85,
        internal_monologue="[LLM] Generated constructive analysis"
    )

def get_critical_analysis(prompt: str) -> EngineOutput:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a critical analyzer..."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return EngineOutput(
        reasoning_mode="Critical",
        output=response.choices[0].message.content,
        confidence=0.85,
        internal_monologue="[LLM] Generated critical analysis"
    )

# Use with Governor
governor = THEOSGovernor()
left = get_constructive_analysis(prompt)
right = get_critical_analysis(prompt)
evaluation = governor.evaluate_cycle(left, right, 1.0, 1)
```

---

### Q: How do I handle decisions that don't converge?

**A:** Not all decisions converge - that's okay:

```python
evaluation = governor.evaluate_cycle(left, right, budget, cycle)

if evaluation.decision == "STOP":
    if evaluation.stop_reason == StopReason.CONVERGENCE_ACHIEVED:
        # Engines agree - high confidence
        decision = "Proceed with confidence"
    elif evaluation.stop_reason == StopReason.CONTRADICTION_EXHAUSTED:
        # Can't resolve - preserve both perspectives
        decision = "Balanced approach incorporating both views"
    elif evaluation.stop_reason == StopReason.RISK_THRESHOLD_EXCEEDED:
        # Too risky - escalate
        decision = "Escalate to human review"
```

---

### Q: Can I use THEOS for real-time monitoring?

**A:** Yes:

```python
import time

while True:
    # Get current state
    left = monitor_constructive_view()
    right = monitor_critical_view()
    
    # Evaluate
    evaluation = governor.evaluate_cycle(left, right, budget, cycle)
    
    # Alert if risk high
    if evaluation.risk_score > 0.40:
        send_alert(f"Risk: {evaluation.risk_score:.2f}")
    
    # Sleep before next check
    time.sleep(60)
```

---

### Q: How do I debug THEOS decisions?

**A:** Use audit trails:

```python
evaluation = governor.evaluate_cycle(left, right, 1.0, 1)

# Print detailed information
print(f"Decision: {evaluation.decision}")
print(f"Similarity: {evaluation.similarity_score:.2f}")
print(f"Risk: {evaluation.risk_score:.2f}")
print(f"Quality: {evaluation.composite_quality:.2f}")
print(f"Quality Metrics: {evaluation.quality_metrics}")
print(f"Governor Reasoning: {evaluation.internal_monologue}")

# Get full audit trail
audit = governor.get_audit_trail()
print(f"Audit Trail: {audit}")
```

---

### Q: What's the cost of using THEOS?

**A:** THEOS has minimal computational cost:
- Governor initialization: < 1ms
- Similarity computation: < 10ms
- Cycle evaluation: < 50ms
- Full 3-cycle reasoning: < 200ms

Memory usage is also minimal (< 10MB for typical use).

---

### Q: Can I extend THEOS?

**A:** Yes, THEOS is designed for extension:

1. **Custom quality metrics:**
   - Modify `calculate_quality_metrics()`
   - Add domain-specific metrics

2. **Custom stop conditions:**
   - Add new `StopReason` values
   - Implement custom stopping logic

3. **Custom wisdom types:**
   - Extend `WisdomRecord`
   - Implement custom wisdom application

See code comments for extension points.

---

## Getting Help

If you encounter an issue not covered here:

1. **Check the logs:** Review error messages carefully
2. **Check examples:** See `examples/` for working code
3. **Check tests:** See `tests/` for test patterns
4. **Check API reference:** See `docs/API_REFERENCE.md`
5. **Open an issue:** https://github.com/Frederick-Stalnecker/THEOS/issues

---

**Status:** Production Ready ✅  
**Last Updated:** February 19, 2026
