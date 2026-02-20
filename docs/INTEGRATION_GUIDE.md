# THEOS Integration Guide

Best practices and patterns for integrating THEOS into applications.

## Table of Contents

1. [Integration Patterns](#integration-patterns)
2. [Common Use Cases](#common-use-cases)
3. [Best Practices](#best-practices)
4. [Performance Optimization](#performance-optimization)
5. [Testing Integration](#testing-integration)
6. [Troubleshooting](#troubleshooting)

---

## Integration Patterns

### Pattern 1: Simple Decision Support

Use THEOS to evaluate a single decision with two perspectives.

```python
from theos_governor import THEOSGovernor, GovernorConfig, EngineOutput

def evaluate_decision(prompt: str) -> dict:
    """Evaluate a decision using THEOS"""
    
    # Initialize Governor
    config = GovernorConfig(max_cycles=3)
    governor = THEOSGovernor(config=config)
    
    # Get engine outputs (from LLM, domain experts, etc.)
    left = get_constructive_analysis(prompt)
    right = get_critical_analysis(prompt)
    
    # Evaluate
    evaluation = governor.evaluate_cycle(left, right, 1.0, 1)
    
    # Return decision
    return {
        "decision": evaluation.decision,
        "similarity": evaluation.similarity_score,
        "risk": evaluation.risk_score,
        "quality": evaluation.composite_quality,
        "reasoning": evaluation.internal_monologue
    }

# Usage
result = evaluate_decision("Should we implement feature X?")
print(f"Decision: {result['decision']}")
print(f"Risk: {result['risk']:.2f}")
```

---

### Pattern 2: Multi-Cycle Reasoning

Run multiple reasoning cycles to reach convergence.

```python
def multi_cycle_reasoning(prompt: str, max_cycles: int = 5) -> dict:
    """Run multiple reasoning cycles"""
    
    config = GovernorConfig(max_cycles=max_cycles)
    governor = THEOSGovernor(config=config)
    
    budget = config.initial_contradiction_budget
    results = []
    
    for cycle_num in range(1, max_cycles + 1):
        # Get engine outputs
        left = get_constructive_analysis(prompt, cycle_num)
        right = get_critical_analysis(prompt, cycle_num)
        
        # Evaluate
        evaluation = governor.evaluate_cycle(left, right, budget, cycle_num)
        budget = evaluation.remaining_budget
        
        # Record result
        results.append({
            "cycle": cycle_num,
            "similarity": evaluation.similarity_score,
            "risk": evaluation.risk_score,
            "quality": evaluation.composite_quality,
            "decision": evaluation.decision
        })
        
        # Stop if decided
        if evaluation.decision == "STOP":
            break
    
    return {
        "cycles": results,
        "final_decision": results[-1]["decision"],
        "convergence_cycle": len(results)
    }

# Usage
result = multi_cycle_reasoning("Complex policy decision")
print(f"Converged in {result['convergence_cycle']} cycles")
```

---

### Pattern 3: Wisdom-Informed Reasoning

Use accumulated wisdom to inform decisions.

```python
from theos_governor import WisdomRecord
from datetime import datetime

def wisdom_informed_reasoning(prompt: str, domain: str) -> dict:
    """Reasoning informed by prior wisdom"""
    
    config = GovernorConfig(max_cycles=3)
    governor = THEOSGovernor(config=config)
    
    # Load relevant wisdom from database
    wisdom_records = load_wisdom_for_domain(domain)
    for wisdom in wisdom_records:
        governor.add_wisdom(wisdom)
    
    # Run reasoning
    left = get_constructive_analysis(prompt)
    right = get_critical_analysis(prompt)
    evaluation = governor.evaluate_cycle(left, right, 1.0, 1)
    
    # Get audit trail showing wisdom influence
    audit = governor.get_audit_trail()
    
    return {
        "decision": evaluation.decision,
        "quality": evaluation.composite_quality,
        "wisdom_records_used": audit['wisdom_records_count'],
        "audit_trail": audit
    }

# Usage
result = wisdom_informed_reasoning(
    "Medical treatment decision",
    domain="Medical_Ethics"
)
print(f"Used {result['wisdom_records_used']} wisdom records")
```

---

### Pattern 4: Constraint-Aware Reasoning

Use dual-clock Governor with constraints.

```python
from theos_dual_clock_governor import TheosDualClockGovernor

def constraint_aware_reasoning(
    prompt: str,
    constraints: list
) -> dict:
    """Reasoning with explicit constraints"""
    
    governor = TheosDualClockGovernor(
        max_cycles=3,
        similarity_threshold=0.90,
        risk_threshold=0.35
    )
    
    # Get engine outputs
    left = get_constructive_analysis(prompt)
    right = get_critical_analysis(prompt)
    
    # Evaluate with constraints
    evaluation = governor.evaluate_cycle(
        left, right, 1.0, 1,
        constraints=constraints
    )
    
    return {
        "decision": evaluation.decision,
        "constraints_satisfied": evaluation.quality_metrics.get("constraints", 1.0),
        "reasoning": evaluation.internal_monologue
    }

# Usage
constraints = [
    "Must preserve individual rights",
    "Must be cost-effective",
    "Must be implementable within 6 months"
]

result = constraint_aware_reasoning(
    "Policy implementation decision",
    constraints=constraints
)
```

---

## Common Use Cases

### Medical Decision Support

```python
def medical_decision_support(patient_case: str) -> dict:
    """Support for medical decisions"""
    
    config = GovernorConfig(
        max_cycles=4,
        similarity_threshold=0.85,  # Medical decisions may not fully converge
        risk_threshold=0.40,        # Higher risk tolerance for medical decisions
        initial_contradiction_budget=1.2
    )
    
    governor = THEOSGovernor(config=config)
    
    # Constructive: Standard treatment protocol
    left = EngineOutput(
        reasoning_mode="Constructive",
        output=get_standard_protocol(patient_case),
        confidence=0.90,
        internal_monologue="[Medical] Standard protocol analysis"
    )
    
    # Critical: Alternative approaches and risks
    right = EngineOutput(
        reasoning_mode="Critical",
        output=get_alternative_approaches(patient_case),
        confidence=0.85,
        internal_monologue="[Medical] Risk assessment"
    )
    
    evaluation = governor.evaluate_cycle(left, right, 1.2, 1)
    
    return {
        "recommendation": evaluation.decision,
        "confidence": evaluation.composite_quality,
        "risk_assessment": evaluation.risk_score,
        "alternatives_considered": evaluation.similarity_score < 0.9
    }
```

### Financial Decision Support

```python
def financial_decision_support(investment_proposal: dict) -> dict:
    """Support for financial decisions"""
    
    config = GovernorConfig(
        max_cycles=3,
        similarity_threshold=0.75,  # Financial decisions often diverge
        risk_threshold=0.50,        # Risk is acceptable if managed
        initial_contradiction_budget=1.3
    )
    
    governor = THEOSGovernor(config=config)
    
    # Constructive: Growth potential
    left = EngineOutput(
        reasoning_mode="Constructive",
        output=analyze_growth_potential(investment_proposal),
        confidence=0.80,
        internal_monologue="[Finance] Growth analysis"
    )
    
    # Critical: Risk assessment
    right = EngineOutput(
        reasoning_mode="Critical",
        output=analyze_risks(investment_proposal),
        confidence=0.85,
        internal_monologue="[Finance] Risk analysis"
    )
    
    evaluation = governor.evaluate_cycle(left, right, 1.3, 1)
    
    return {
        "recommendation": "Balanced approach",
        "growth_potential": left.confidence,
        "risk_level": evaluation.risk_score,
        "allocation_suggestion": calculate_allocation(evaluation)
    }
```

### Policy Analysis

```python
def policy_analysis(policy_proposal: str) -> dict:
    """Analyze policy proposals"""
    
    config = GovernorConfig(
        max_cycles=5,
        similarity_threshold=0.80,
        risk_threshold=0.45,
        initial_contradiction_budget=1.5
    )
    
    governor = THEOSGovernor(config=config)
    
    budget = config.initial_contradiction_budget
    cycles_data = []
    
    for cycle in range(1, 6):
        # Progressive refinement
        left = EngineOutput(
            reasoning_mode="Constructive",
            output=get_policy_benefits(policy_proposal, cycle),
            confidence=0.80,
            internal_monologue=f"[Policy] Cycle {cycle} benefits"
        )
        
        right = EngineOutput(
            reasoning_mode="Critical",
            output=get_policy_concerns(policy_proposal, cycle),
            confidence=0.80,
            internal_monologue=f"[Policy] Cycle {cycle} concerns"
        )
        
        evaluation = governor.evaluate_cycle(left, right, budget, cycle)
        budget = evaluation.remaining_budget
        
        cycles_data.append({
            "cycle": cycle,
            "similarity": evaluation.similarity_score,
            "quality": evaluation.composite_quality
        })
        
        if evaluation.decision == "STOP":
            break
    
    return {
        "analysis": cycles_data,
        "recommendation": synthesize_recommendation(cycles_data),
        "convergence": cycles_data[-1]["similarity"]
    }
```

---

## Best Practices

### 1. Configure Appropriately

Choose configuration based on decision type:

```python
# High-stakes decisions: Conservative
config = GovernorConfig(
    max_cycles=5,
    similarity_threshold=0.95,
    risk_threshold=0.25,
    initial_contradiction_budget=0.8
)

# Balanced decisions: Default
config = GovernorConfig()  # Uses defaults

# Exploratory decisions: Permissive
config = GovernorConfig(
    max_cycles=4,
    similarity_threshold=0.80,
    risk_threshold=0.50,
    initial_contradiction_budget=1.5
)
```

### 2. Provide Quality Engine Outputs

Engine outputs should be:
- **Substantive** - Not empty or trivial
- **Coherent** - Logically structured
- **Calibrated** - Confidence matches actual quality
- **Evidence-based** - Grounded in facts

```python
# ❌ Poor quality output
output = EngineOutput(
    reasoning_mode="Constructive",
    output="This is good",  # Too vague
    confidence=0.95,        # Overconfident
    internal_monologue="thinking..."
)

# ✅ Good quality output
output = EngineOutput(
    reasoning_mode="Constructive",
    output="""
    Analysis of approach A:
    1. Efficiency: 85% improvement (based on pilot data)
    2. Cost: $500K implementation (within budget)
    3. Timeline: 6 months (acceptable)
    4. Risks: Integration complexity (mitigated by team expertise)
    
    Recommendation: Proceed with approach A
    """,
    confidence=0.82,  # Calibrated to evidence
    internal_monologue="[Constructive] Analyzed efficiency, cost, timeline, risks"
)
```

### 3. Use Wisdom Accumulation

Learn from past decisions:

```python
# After a decision with consequences
if decision_had_negative_consequences():
    wisdom = WisdomRecord(
        domain="Your_Domain",
        lesson="What you learned",
        consequence_type="harm",  # or "near_miss", "probing", "benign"
        future_bias="How to apply this learning",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
    
    # Store in database
    save_wisdom_to_db(wisdom)
    
    # Use in future decisions
    governor.add_wisdom(wisdom)
```

### 4. Monitor Audit Trails

Always capture and review audit trails:

```python
evaluation = governor.evaluate_cycle(left, right, budget, cycle)
audit = governor.get_audit_trail()

# Log for compliance
log_decision({
    "timestamp": datetime.utcnow(),
    "decision": evaluation.decision,
    "similarity": evaluation.similarity_score,
    "risk": evaluation.risk_score,
    "quality": evaluation.composite_quality,
    "stop_reason": evaluation.stop_reason,
    "audit_trail": audit
})

# Alert if high risk
if evaluation.risk_score > 0.40:
    alert_stakeholders(f"High risk decision: {evaluation.risk_score:.2f}")
```

### 5. Handle Convergence Gracefully

Not all decisions converge:

```python
budget = config.initial_contradiction_budget

for cycle in range(1, config.max_cycles + 1):
    evaluation = governor.evaluate_cycle(left, right, budget, cycle)
    budget = evaluation.remaining_budget
    
    if evaluation.decision == "STOP":
        if evaluation.stop_reason == StopReason.CONVERGENCE_ACHIEVED:
            # Engines agree - high confidence
            confidence = "high"
        elif evaluation.stop_reason == StopReason.RISK_THRESHOLD_EXCEEDED:
            # Risk too high - escalate
            escalate_to_human_review()
        elif evaluation.stop_reason == StopReason.CONTRADICTION_EXHAUSTED:
            # Can't resolve contradiction - preserve both perspectives
            confidence = "mixed"
        
        break
```

---

## Performance Optimization

### 1. Cache Engine Outputs

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_constructive_analysis(prompt: str, cycle: int) -> EngineOutput:
    """Cache engine outputs to avoid recomputation"""
    # ... implementation
    pass
```

### 2. Batch Process Decisions

```python
def batch_process_decisions(decisions: list) -> list:
    """Process multiple decisions efficiently"""
    
    config = GovernorConfig()
    results = []
    
    for decision in decisions:
        governor = THEOSGovernor(config=config)
        
        left = get_constructive_analysis(decision)
        right = get_critical_analysis(decision)
        
        evaluation = governor.evaluate_cycle(left, right, 1.0, 1)
        results.append(evaluation)
    
    return results
```

### 3. Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_decisions(decisions: list, max_workers: int = 4) -> list:
    """Process decisions in parallel"""
    
    def process_decision(decision):
        governor = THEOSGovernor(config=GovernorConfig())
        left = get_constructive_analysis(decision)
        right = get_critical_analysis(decision)
        return governor.evaluate_cycle(left, right, 1.0, 1)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_decision, decisions))
    
    return results
```

---

## Testing Integration

### Unit Tests

```python
import pytest
from theos_governor import THEOSGovernor, EngineOutput

def test_decision_support():
    """Test decision support integration"""
    
    governor = THEOSGovernor()
    
    left = EngineOutput(
        reasoning_mode="Constructive",
        output="Approach A is efficient",
        confidence=0.85,
        internal_monologue="[Test] Constructive"
    )
    
    right = EngineOutput(
        reasoning_mode="Critical",
        output="Approach A has risks",
        confidence=0.80,
        internal_monologue="[Test] Critical"
    )
    
    evaluation = governor.evaluate_cycle(left, right, 1.0, 1)
    
    assert evaluation.decision in ["CONTINUE", "STOP"]
    assert 0 <= evaluation.similarity_score <= 1
    assert 0 <= evaluation.risk_score <= 1
```

### Integration Tests

```python
def test_full_workflow():
    """Test complete decision workflow"""
    
    # Setup
    config = GovernorConfig(max_cycles=3)
    governor = THEOSGovernor(config=config)
    
    budget = config.initial_contradiction_budget
    
    # Run cycles
    for cycle in range(1, 4):
        left = create_test_output("constructive", cycle)
        right = create_test_output("critical", cycle)
        
        evaluation = governor.evaluate_cycle(left, right, budget, cycle)
        budget = evaluation.remaining_budget
        
        # Verify state
        assert budget >= 0
        assert evaluation.decision in ["CONTINUE", "STOP"]
        
        if evaluation.decision == "STOP":
            break
    
    # Verify audit trail
    audit = governor.get_audit_trail()
    assert audit['total_cycles'] > 0
    assert len(audit['quality_trajectory']) == audit['total_cycles']
```

---

## Troubleshooting

### Issue: Engines Always Converge

**Problem:** Engines agree too quickly, not exploring contradictions.

**Solution:** Increase contradiction budget and reduce similarity threshold:

```python
config = GovernorConfig(
    initial_contradiction_budget=1.5,
    similarity_threshold=0.80,  # Lower threshold
    max_cycles=5
)
```

### Issue: Engines Never Converge

**Problem:** Engines remain contradictory, reasoning doesn't terminate.

**Solution:** Increase similarity threshold or reduce budget:

```python
config = GovernorConfig(
    similarity_threshold=0.95,  # Higher threshold
    initial_contradiction_budget=0.8,  # Lower budget
    max_cycles=3
)
```

### Issue: Risk Score Too High

**Problem:** Governor stops due to high risk.

**Solution:** Improve engine outputs or increase risk threshold:

```python
# Option 1: Increase threshold
config = GovernorConfig(risk_threshold=0.50)

# Option 2: Improve engine outputs
left = get_better_constructive_analysis(prompt)
right = get_better_critical_analysis(prompt)
```

### Issue: Low Quality Scores

**Problem:** Composite quality is low.

**Solution:** Improve engine output quality:

```python
# Ensure outputs are:
# - Substantive (not trivial)
# - Coherent (logically structured)
# - Calibrated (confidence matches quality)
# - Evidence-based (grounded in facts)

output = EngineOutput(
    reasoning_mode="Constructive",
    output="""
    Detailed analysis with:
    1. Evidence and data
    2. Logical reasoning
    3. Clear conclusions
    """,
    confidence=0.85,  # Calibrated
    internal_monologue="Detailed reasoning"
)
```

---

## References

- [API_REFERENCE.md](./API_REFERENCE.md) - Complete API documentation
- [GETTING_STARTED.md](../GETTING_STARTED.md) - Installation and quick start
- [examples/](../examples/) - Working examples
- [tests/](../tests/) - Unit tests

---

**Status:** Production Ready ✅  
**Last Updated:** February 19, 2026
