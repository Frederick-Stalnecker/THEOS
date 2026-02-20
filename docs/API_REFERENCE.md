# THEOS API Reference

Complete API documentation for the THEOS dual-engine reasoning framework.

## Table of Contents

1. [Core Classes](#core-classes)
2. [Enumerations](#enumerations)
3. [Data Classes](#data-classes)
4. [Governor Methods](#governor-methods)
5. [Configuration](#configuration)
6. [Type Hints](#type-hints)
7. [Error Handling](#error-handling)
8. [Usage Examples](#usage-examples)

---

## Core Classes

### THEOSGovernor

The main Governor class that manages dual-engine reasoning cycles.

#### Initialization

```python
from theos_governor import THEOSGovernor, GovernorConfig

config = GovernorConfig(
    max_cycles=3,
    similarity_threshold=0.90,
    risk_threshold=0.35,
    initial_contradiction_budget=1.0,
    contradiction_decay_rate=0.175
)

governor = THEOSGovernor(config=config)
```

**Parameters:**
- `config` (GovernorConfig): Configuration object with hyperparameters

**Returns:** THEOSGovernor instance

---

### TheosDualClockGovernor

Extended Governor with dual-clock system for constraint-aware reasoning.

#### Initialization

```python
from theos_dual_clock_governor import TheosDualClockGovernor

governor = TheosDualClockGovernor(
    max_cycles=3,
    similarity_threshold=0.90,
    risk_threshold=0.35
)
```

**Parameters:**
- `max_cycles` (int): Maximum reasoning cycles
- `similarity_threshold` (float): Convergence threshold (0-1)
- `risk_threshold` (float): Safety threshold (0-1)

**Returns:** TheosDualClockGovernor instance

---

## Enumerations

### Posture

Governor operational posture states.

```python
from theos_governor import Posture

class Posture(Enum):
    NOM = "Normal"        # Normal operation
    PEM = "Proactive"     # Elevated monitoring
    CM = "Containment"    # Strict containment
    IM = "Isolation"      # Full isolation
```

**Values:**
- `NOM` - Normal operation (default)
- `PEM` - Proactive monitoring
- `CM` - Containment mode
- `IM` - Isolation mode

---

### StopReason

Reasons why Governor stops reasoning.

```python
from theos_governor import StopReason

class StopReason(Enum):
    CONVERGENCE_ACHIEVED = "Engines converged to acceptable similarity"
    RISK_THRESHOLD_EXCEEDED = "Risk score exceeded safety threshold"
    CONTRADICTION_EXHAUSTED = "Contradiction budget depleted"
    PLATEAU_DETECTED = "No marginal improvement in quality"
    MAX_CYCLES_REACHED = "Maximum cycle limit reached"
```

**Values:**
- `CONVERGENCE_ACHIEVED` - Engines agree (similarity ≥ threshold)
- `RISK_THRESHOLD_EXCEEDED` - Risk too high (> threshold)
- `CONTRADICTION_EXHAUSTED` - Budget depleted
- `PLATEAU_DETECTED` - No improvement in quality
- `MAX_CYCLES_REACHED` - Cycle limit reached

---

## Data Classes

### EngineOutput

Output from a single reasoning engine.

```python
@dataclass
class EngineOutput:
    reasoning_mode: str          # "Constructive" or "Critical"
    output: str                  # The reasoning output
    confidence: float            # Confidence level (0-1)
    internal_monologue: str      # Internal reasoning for auditability
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `reasoning_mode` | str | Engine mode: "Constructive" or "Critical" |
| `output` | str | The actual reasoning/output text |
| `confidence` | float | Engine's confidence (0.0-1.0) |
| `internal_monologue` | str | Internal reasoning for audit trail |

**Example:**

```python
from theos_governor import EngineOutput

output = EngineOutput(
    reasoning_mode="Constructive",
    output="This approach maximizes efficiency...",
    confidence=0.85,
    internal_monologue="[Constructive] Analyzing efficiency gains"
)
```

---

### GovernorEvaluation

Governor's evaluation of a reasoning cycle.

```python
@dataclass
class GovernorEvaluation:
    similarity_score: float           # Similarity (0-1)
    contradiction_level: float        # Contradiction (1 - similarity)
    risk_score: float                 # Risk assessment (0-1)
    quality_metrics: Dict[str, float] # Coherence, calibration, evidence, actionability
    composite_quality: float          # Weighted quality score (0-1)
    contradiction_spent: float        # Budget consumed this cycle
    remaining_budget: float           # Budget remaining
    decision: str                     # "CONTINUE" or "STOP"
    stop_reason: Optional[StopReason] # Why stopped (if applicable)
    internal_monologue: str           # Governor's reasoning
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `similarity_score` | float | How similar are the engines? (0-1) |
| `contradiction_level` | float | How contradictory? (1 - similarity) |
| `risk_score` | float | How risky is this state? (0-1) |
| `quality_metrics` | dict | Individual quality measures |
| `composite_quality` | float | Overall quality score (0-1) |
| `contradiction_spent` | float | Budget consumed this cycle |
| `remaining_budget` | float | Budget left for future cycles |
| `decision` | str | "CONTINUE" or "STOP" |
| `stop_reason` | StopReason | Why stopped (if applicable) |
| `internal_monologue` | str | Governor's reasoning explanation |

**Example:**

```python
evaluation = governor.evaluate_cycle(left, right, 1.0, 1)

print(f"Similarity: {evaluation.similarity_score:.2f}")
print(f"Risk: {evaluation.risk_score:.2f}")
print(f"Quality: {evaluation.composite_quality:.2f}")
print(f"Decision: {evaluation.decision}")
if evaluation.stop_reason:
    print(f"Stop Reason: {evaluation.stop_reason.value}")
```

---

### WisdomRecord

Record of a lesson learned from decision consequences.

```python
@dataclass
class WisdomRecord:
    domain: str              # Domain (e.g., "Medical Ethics")
    lesson: str              # The lesson learned
    consequence_type: str    # "benign", "probing", "near_miss", "harm"
    future_bias: str         # How to bias future decisions
    timestamp: str           # ISO 8601 timestamp
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `domain` | str | Decision domain |
| `lesson` | str | What was learned |
| `consequence_type` | str | Type: benign, probing, near_miss, harm |
| `future_bias` | str | How to apply this learning |
| `timestamp` | str | ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ) |

**Consequence Types:**
- `benign` - No negative consequences
- `probing` - Minor issues, worth monitoring
- `near_miss` - Could have been serious
- `harm` - Actual negative consequences

**Example:**

```python
from theos_governor import WisdomRecord
from datetime import datetime

wisdom = WisdomRecord(
    domain="Medical_Ethics",
    lesson="Utilitarian efficiency must be balanced with rights protection",
    consequence_type="benign",
    future_bias="Apply both utilitarian and rights-based analysis",
    timestamp=datetime.utcnow().isoformat() + "Z"
)

governor.add_wisdom(wisdom)
```

---

### GovernorConfig

Configuration for Governor behavior.

```python
@dataclass
class GovernorConfig:
    max_cycles: int = 3
    similarity_threshold: float = 0.90
    risk_threshold: float = 0.35
    initial_contradiction_budget: float = 1.0
    contradiction_decay_rate: float = 0.175
    quality_improvement_threshold: float = 0.05
    
    # Hyperparameters
    alpha: float = 0.65
    beta: float = 0.30
    gamma: float = 0.75
    delta: float = 0.15
    epsilon: float = 0.45
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `max_cycles` | int | 3 | Maximum reasoning cycles |
| `similarity_threshold` | float | 0.90 | Stop if similarity ≥ this |
| `risk_threshold` | float | 0.35 | Stop if risk > this |
| `initial_contradiction_budget` | float | 1.0 | Starting contradiction budget |
| `contradiction_decay_rate` | float | 0.175 | How fast budget depletes |
| `quality_improvement_threshold` | float | 0.05 | Min improvement to continue |
| `alpha` | float | 0.65 | Weight for aggregate risk |
| `beta` | float | 0.30 | Weight for wisdom risk |
| `gamma` | float | 0.75 | Weight for risk in similarity |
| `delta` | float | 0.15 | Weight for escalation pressure |
| `epsilon` | float | 0.45 | Weight for wisdom stress |

**Example:**

```python
config = GovernorConfig(
    max_cycles=5,
    similarity_threshold=0.85,
    risk_threshold=0.40,
    initial_contradiction_budget=1.5
)

governor = THEOSGovernor(config=config)
```

---

## Governor Methods

### evaluate_cycle()

Evaluate a single reasoning cycle.

```python
def evaluate_cycle(
    self,
    left_output: EngineOutput,
    right_output: EngineOutput,
    current_budget: float,
    cycle_number: int
) -> GovernorEvaluation:
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `left_output` | EngineOutput | Output from left engine |
| `right_output` | EngineOutput | Output from right engine |
| `current_budget` | float | Current contradiction budget |
| `cycle_number` | int | Current cycle number (1-indexed) |

**Returns:** GovernorEvaluation object

**Raises:** ValueError if inputs are invalid

**Example:**

```python
left = EngineOutput(
    reasoning_mode="Constructive",
    output="Approach A is more efficient...",
    confidence=0.85,
    internal_monologue="[Constructive] Analyzing efficiency"
)

right = EngineOutput(
    reasoning_mode="Critical",
    output="But approach A has these risks...",
    confidence=0.80,
    internal_monologue="[Critical] Assessing risks"
)

evaluation = governor.evaluate_cycle(left, right, 1.0, 1)

print(f"Decision: {evaluation.decision}")
print(f"Similarity: {evaluation.similarity_score:.2f}")
print(f"Risk: {evaluation.risk_score:.2f}")
```

---

### compute_similarity()

Compute similarity between two text outputs.

```python
def compute_similarity(self, left: str, right: str) -> float:
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `left` | str | First output text |
| `right` | str | Second output text |

**Returns:** float (0.0 - 1.0)
- 1.0 = Identical
- 0.5 = Moderate similarity
- 0.0 = Completely different

**Example:**

```python
left_text = "The approach should prioritize efficiency"
right_text = "The approach should prioritize fairness"

similarity = governor.compute_similarity(left_text, right_text)
print(f"Similarity: {similarity:.2f}")  # Output: 0.45
```

---

### add_wisdom()

Add a wisdom record to the Governor's knowledge base.

```python
def add_wisdom(self, wisdom: WisdomRecord) -> None:
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `wisdom` | WisdomRecord | Wisdom record to add |

**Returns:** None

**Example:**

```python
wisdom = WisdomRecord(
    domain="Finance",
    lesson="Growth without stability is risky",
    consequence_type="near_miss",
    future_bias="Balance growth with risk management",
    timestamp="2026-02-19T12:00:00Z"
)

governor.add_wisdom(wisdom)
```

---

### get_audit_trail()

Get complete audit trail of reasoning.

```python
def get_audit_trail(self) -> Dict[str, any]:
```

**Returns:** Dictionary with audit information

**Keys:**

| Key | Type | Description |
|-----|------|-------------|
| `total_cycles` | int | Number of cycles completed |
| `final_similarity` | float | Final similarity score |
| `final_risk` | float | Final risk score |
| `final_quality` | float | Final quality score |
| `contradiction_budget_used` | float | Budget consumed |
| `stop_reason` | str | Why reasoning stopped |
| `wisdom_records_count` | int | Number of wisdom records |
| `quality_trajectory` | list | Quality scores per cycle |
| `risk_trajectory` | list | Risk scores per cycle |
| `similarity_trajectory` | list | Similarity scores per cycle |
| `cycle_history` | list | Detailed cycle information |

**Example:**

```python
audit = governor.get_audit_trail()

print(f"Cycles: {audit['total_cycles']}")
print(f"Similarity: {audit['final_similarity']:.2f}")
print(f"Risk: {audit['final_risk']:.2f}")
print(f"Quality: {audit['final_quality']:.2f}")
print(f"Stop Reason: {audit['stop_reason']}")
print(f"Quality Trajectory: {audit['quality_trajectory']}")
```

---

### reset()

Reset Governor to initial state.

```python
def reset(self) -> None:
```

**Returns:** None

**Example:**

```python
governor.reset()
# Governor is now ready for new reasoning cycle
```

---

## Dual-Clock Governor Methods

### TheosDualClockGovernor.evaluate_cycle()

Evaluate cycle with dual-clock constraint system.

```python
def evaluate_cycle(
    self,
    left_output: EngineOutput,
    right_output: EngineOutput,
    current_budget: float,
    cycle_number: int,
    constraints: Optional[List[str]] = None
) -> GovernorEvaluation:
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `left_output` | EngineOutput | Left engine output |
| `right_output` | EngineOutput | Right engine output |
| `current_budget` | float | Contradiction budget |
| `cycle_number` | int | Cycle number |
| `constraints` | list | Optional constraint list |

**Returns:** GovernorEvaluation

**Example:**

```python
constraints = [
    "Must preserve individual rights",
    "Must be cost-effective"
]

evaluation = governor.evaluate_cycle(
    left, right, 1.0, 1,
    constraints=constraints
)
```

---

## Configuration

### Default Configuration

```python
GovernorConfig(
    max_cycles=3,
    similarity_threshold=0.90,
    risk_threshold=0.35,
    initial_contradiction_budget=1.0,
    contradiction_decay_rate=0.175,
    quality_improvement_threshold=0.05,
    alpha=0.65,
    beta=0.30,
    gamma=0.75,
    delta=0.15,
    epsilon=0.45
)
```

### Recommended Configurations

**Conservative (High Safety):**
```python
GovernorConfig(
    max_cycles=5,
    similarity_threshold=0.95,
    risk_threshold=0.25,
    initial_contradiction_budget=0.8,
    contradiction_decay_rate=0.20
)
```

**Balanced:**
```python
GovernorConfig(
    max_cycles=3,
    similarity_threshold=0.90,
    risk_threshold=0.35,
    initial_contradiction_budget=1.0,
    contradiction_decay_rate=0.175
)
```

**Exploratory (Lower Safety):**
```python
GovernorConfig(
    max_cycles=4,
    similarity_threshold=0.80,
    risk_threshold=0.50,
    initial_contradiction_budget=1.5,
    contradiction_decay_rate=0.15
)
```

---

## Type Hints

All THEOS code uses Python type hints for clarity and IDE support.

```python
from typing import List, Dict, Optional, Tuple
from theos_governor import (
    THEOSGovernor,
    GovernorConfig,
    EngineOutput,
    GovernorEvaluation,
    WisdomRecord,
    StopReason,
    Posture
)

def my_reasoning_function(
    governor: THEOSGovernor,
    left: EngineOutput,
    right: EngineOutput,
    budget: float
) -> GovernorEvaluation:
    """Example function with type hints"""
    return governor.evaluate_cycle(left, right, budget, 1)
```

---

## Error Handling

### Common Errors

**ValueError: Invalid confidence value**
```python
# ❌ Wrong: confidence > 1.0
output = EngineOutput(
    reasoning_mode="Constructive",
    output="...",
    confidence=1.5,  # ERROR!
    internal_monologue="..."
)

# ✅ Correct: confidence in [0, 1]
output = EngineOutput(
    reasoning_mode="Constructive",
    output="...",
    confidence=0.85,
    internal_monologue="..."
)
```

**ValueError: Invalid similarity threshold**
```python
# ❌ Wrong: threshold > 1.0
config = GovernorConfig(similarity_threshold=1.5)  # ERROR!

# ✅ Correct: threshold in [0, 1]
config = GovernorConfig(similarity_threshold=0.90)
```

**ValueError: Empty output**
```python
# ❌ Wrong: empty output
output = EngineOutput(
    reasoning_mode="Constructive",
    output="",  # ERROR!
    confidence=0.85,
    internal_monologue="..."
)

# ✅ Correct: non-empty output
output = EngineOutput(
    reasoning_mode="Constructive",
    output="This is my reasoning...",
    confidence=0.85,
    internal_monologue="..."
)
```

### Error Handling Pattern

```python
try:
    evaluation = governor.evaluate_cycle(left, right, budget, cycle)
except ValueError as e:
    print(f"Invalid input: {e}")
    # Handle error
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle error
```

---

## Usage Examples

### Basic Usage

```python
from theos_governor import (
    THEOSGovernor,
    GovernorConfig,
    EngineOutput
)

# Create Governor
config = GovernorConfig(max_cycles=3)
governor = THEOSGovernor(config=config)

# Create engine outputs
left = EngineOutput(
    reasoning_mode="Constructive",
    output="Approach A maximizes efficiency...",
    confidence=0.85,
    internal_monologue="[Constructive] Analyzing efficiency"
)

right = EngineOutput(
    reasoning_mode="Critical",
    output="But approach A has these risks...",
    confidence=0.80,
    internal_monologue="[Critical] Assessing risks"
)

# Evaluate cycle
evaluation = governor.evaluate_cycle(left, right, 1.0, 1)

# Check result
print(f"Decision: {evaluation.decision}")
print(f"Similarity: {evaluation.similarity_score:.2f}")
print(f"Risk: {evaluation.risk_score:.2f}")
```

### Multi-Cycle Reasoning

```python
budget = 1.0

for cycle_num in range(1, 4):
    # Get engine outputs
    left = constructive_engine(prompt, cycle_num)
    right = critical_engine(prompt, cycle_num)
    
    # Evaluate
    evaluation = governor.evaluate_cycle(left, right, budget, cycle_num)
    budget = evaluation.remaining_budget
    
    # Check decision
    if evaluation.decision == "STOP":
        print(f"Stopped at cycle {cycle_num}: {evaluation.stop_reason.value}")
        break
```

### With Wisdom

```python
# Add prior wisdom
wisdom = WisdomRecord(
    domain="Medical_Ethics",
    lesson="Balance efficiency with fairness",
    consequence_type="benign",
    future_bias="Use hybrid approach",
    timestamp="2026-02-19T12:00:00Z"
)
governor.add_wisdom(wisdom)

# Run reasoning
evaluation = governor.evaluate_cycle(left, right, 1.0, 1)

# Get audit trail
audit = governor.get_audit_trail()
print(f"Wisdom records used: {audit['wisdom_records_count']}")
```

---

## Performance Characteristics

| Operation | Time | Space |
|-----------|------|-------|
| Initialize Governor | < 1ms | ~1KB |
| Compute similarity | < 10ms | ~1KB |
| Evaluate cycle | < 50ms | ~10KB |
| Add wisdom record | < 1ms | ~100B |
| Get audit trail | < 5ms | ~10KB |
| Full 3-cycle reasoning | < 200ms | ~50KB |

---

## Version Information

- **THEOS Version:** 1.4
- **API Version:** 1.0
- **Python:** 3.8+
- **Last Updated:** February 19, 2026

---

## See Also

- [GETTING_STARTED.md](../GETTING_STARTED.md) - Installation and quick start
- [examples/](../examples/) - Working examples
- [tests/](../tests/) - Unit tests
- [THEOS_COMPLETE_MASTER_DOCUMENT.md](../THEOS_COMPLETE_MASTER_DOCUMENT.md) - Complete reference

---

**Status:** Production Ready ✅
