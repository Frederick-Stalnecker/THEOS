# THEOS Quick Start Guide

Get up and running with THEOS in 5 minutes.

## Installation

```bash
# Clone the repository
git clone https://github.com/Frederick-Stalnecker/THEOS.git
cd THEOS

# No external dependencies required for core implementation
# (Python 3.10+ with standard library only)
```

## Run Your First THEOS Reasoning

### 1. Basic Example (30 seconds)

```bash
python code/theos_system.py
```

**Output:**
```
Query: What is the right move?
Output: 0.048
Confidence: 0.600
Cycles: 2
Halt: diminishing_returns

Query: What is the right move?
Output: 0.27411905870400005
Confidence: 0.836
Cycles: 2
Halt: diminishing_returns

Query: Completely different question
Output: 0.5279999999999999
Confidence: 0.600
Cycles: 2
Halt: diminishing_returns

============================================================
THEOS System Metrics
============================================================
Total Queries:        3
Total Cycles:         6
Avg Cycles/Query:     2.00
Convergence Rate:     0.0%
Wisdom Entries:       3
Avg Confidence:       0.679
============================================================
```

**What's happening:**
- Query 1: Initial reasoning (confidence 0.600)
- Query 2: Same query - wisdom reuse improves confidence to 0.836 (+39%)
- Query 3: Different query - baseline confidence again
- Metrics show wisdom accumulation working

### 2. Medical Diagnosis (1 minute)

```bash
python examples/theos_medical_diagnosis.py
```

**Output shows:**
- Differential diagnosis generation
- Confidence scores
- Clinical recommendations
- Wisdom accumulation across cases

### 3. Financial Analysis (1 minute)

```bash
python examples/theos_financial_analysis.py
```

**Output shows:**
- Investment recommendations (BUY, HOLD, SELL)
- Risk-reward analysis
- Confidence adjustments
- Wisdom-based decision making

### 4. AI Safety Evaluation (1 minute)

```bash
python examples/theos_ai_safety.py
```

**Output shows:**
- Safety confidence scores
- Deployment recommendations (APPROVED, REVIEW, BLOCKED)
- Capability vs. risk assessment
- Alignment measure effectiveness

## Run the Test Suite

```bash
# Run all tests
python -m pytest tests/test_theos_implementation.py -v

# Expected output: 21 passed in 0.04s
```

## Create Your Own THEOS Application

### Step 1: Import the System

```python
from code.theos_system import create_numeric_system, TheosConfig

# Create system
config = TheosConfig(max_cycles=5, eps_converge=0.1)
system = create_numeric_system(config)
```

### Step 2: Run Reasoning

```python
# Run a query
result = system.reason("Your question here")

# Access results
print(f"Output: {result.output}")
print(f"Confidence: {result.confidence}")
print(f"Halt reason: {result.halt_reason}")
```

### Step 3: Get Metrics

```python
# Get system metrics
metrics = system.get_metrics()
print(f"Total queries: {metrics.total_queries}")
print(f"Avg confidence: {metrics.avg_confidence}")

# Export for analysis
metrics_json = system.export_metrics()
history_json = system.export_history()
```

## Understanding the Output

### Result Object

```python
result.output          # The reasoning output
result.output_type     # "blend" or "disagreement"
result.confidence      # 0.0 to 1.0 confidence score
result.contradiction   # Measure of disagreement between engines
result.cycles_used     # Number of reasoning cycles
result.halt_reason     # Why reasoning stopped
result.cycle_traces    # Detailed trace of each cycle
```

### Halt Reasons

- **CONVERGENCE**: Pattern stabilized (φ_t ≈ φ_{t-1})
- **DIMINISHING_RETURNS**: Contradiction not improving (δ_t/δ_{t-1} > 0.9)
- **MAX_CYCLES**: Reached maximum cycle limit

### Output Types

- **BLEND**: Engines agree (|D_L - D_R| < ε)
  - Output is weighted combination
  - High confidence
  
- **DISAGREEMENT**: Engines disagree (|D_L - D_R| ≥ ε)
  - Output shows both perspectives
  - Lower confidence
  - Indicates uncertainty

## Key Concepts

### The I→A→D→I Cycle

Each reasoning cycle follows this pattern:

1. **I (Induction)**: Extract patterns from observation
2. **A (Abduction)**: Generate two hypotheses (left and right)
3. **D (Deduction)**: Derive conclusions from each hypothesis
4. **I (Measure)**: Measure contradiction between conclusions

### Dual Engines

- **Left Engine (L)**: Constructive - builds strongest possible case
- **Right Engine (R)**: Critical - tries to disprove and find risks

### Wisdom Accumulation

- Each query adds to wisdom database
- Repeat queries improve confidence (wisdom reuse)
- Wisdom persists across sessions

### Governor

Decides when to stop reasoning based on:
1. Pattern convergence
2. Diminishing returns
3. Maximum cycles
4. Contradiction budget

## Common Use Cases

### 1. Decision Support

```python
result = system.reason("Should I invest in X?")
if result.confidence > 0.7:
    print("High confidence recommendation")
else:
    print("Need more analysis")
```

### 2. Risk Assessment

```python
result = system.reason("What are the risks of Y?")
if result.output_type == "disagreement":
    print("Significant disagreement - high uncertainty")
    print(f"Left view: {result.output['left']}")
    print(f"Right view: {result.output['right']}")
```

### 3. Diagnosis Support

```python
result = system.reason("Patient with symptoms A, B, C")
print(f"Confidence: {result.confidence:.1%}")
if result.confidence > 0.6:
    print("Proceed with diagnosis")
else:
    print("Need additional tests")
```

### 4. Safety Evaluation

```python
result = system.reason("Is system X safe to deploy?")
if result.contradiction > 0.5:
    print("Significant safety concerns - review needed")
else:
    print("Safety concerns resolved")
```

## Performance Tips

### Improve Confidence

1. **Build wisdom**: Run multiple queries to accumulate knowledge
2. **Similar queries**: Repeat queries benefit from wisdom reuse
3. **Better abduction**: Improve hypothesis generation functions

### Reduce Processing Time

1. **Lower cycle limit**: Reduce `max_cycles` (default: 5)
2. **Higher convergence threshold**: Increase `eps_converge` (default: 0.1)
3. **Simpler functions**: Optimize encode/induce/abduce functions

### Manage Memory

1. **Archive wisdom**: Implement wisdom archival for long-running systems
2. **Compress wisdom**: Use Ω compression function (future enhancement)
3. **Periodic cleanup**: Clear old wisdom entries

## Troubleshooting

### Low Confidence Scores

**Problem**: Confidence consistently below 0.5

**Solution**: 
- Run more queries to build wisdom
- Check that queries are similar enough for wisdom reuse
- Verify abduction functions are generating productive disagreement

### Halting Too Early

**Problem**: Reasoning stops after 1 cycle

**Solution**:
- Increase `eps_converge` threshold
- Increase diminishing returns threshold
- Review abduction functions

### High Contradiction

**Problem**: Engines always disagree

**Solution**:
- Verify abduction functions are reasonable
- Check that deduction is consistent
- Review contradiction measurement function

## Next Steps

1. **Read the Implementation Guide**: `THEOS_IMPLEMENTATION_GUIDE.md`
2. **Explore Examples**: Study `examples/` directory
3. **Run Tests**: `pytest tests/test_theos_implementation.py -v`
4. **Build Your Application**: Create custom domain application
5. **Integrate with Real Models**: Connect to LLMs for production use

## Architecture Overview

```
THEOS System
├── Core Engine (TheosCore)
│   ├── I→A→D→I Cycle
│   ├── Dual Engines (L, R)
│   ├── Governor
│   └── Wisdom Engine
├── System Management (TheosSystem)
│   ├── Metrics Tracking
│   ├── Query History
│   ├── Wisdom Persistence
│   └── Export Functions
└── Domain Applications
    ├── Medical Diagnosis
    ├── Financial Analysis
    └── AI Safety Evaluation
```

## Key Files

| File | Purpose |
|------|---------|
| `code/theos_core.py` | Core reasoning engine |
| `code/theos_system.py` | Unified system |
| `examples/theos_medical_diagnosis.py` | Medical domain |
| `examples/theos_financial_analysis.py` | Financial domain |
| `examples/theos_ai_safety.py` | AI safety domain |
| `tests/test_theos_implementation.py` | Test suite |
| `THEOS_IMPLEMENTATION_GUIDE.md` | Detailed documentation |
| `IMPLEMENTATION_AUDIT.md` | Audit and verification |

## Support

For detailed information:
- **Architecture**: See `THEOS_IMPLEMENTATION_GUIDE.md`
- **Mathematics**: See `THEOS_Final_Polished_Mathematics.md`
- **System Design**: See `THEOS_IRREDUCIBLE_CORE.md`
- **Master Reference**: See `THEOS_MASTER_DOCUMENT.md`

## License

MIT License - See LICENSE file

## Author

Frederick Davis Stalnecker  
USPTO Patent Application #63/831,738

---

**Ready to get started?** Run `python code/theos_system.py` now!
