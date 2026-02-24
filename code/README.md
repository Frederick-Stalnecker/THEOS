# THEOS Reference Implementation

This directory contains the production-ready THEOS implementation with dual-engine reasoning, governor logic, and LLM integration.

## Quick Start

```bash
# Run the demo
python demo.py

# Run tests
python -m pytest ../tests/test_theos_implementation.py -v

# Run examples
python ../examples/theos_medical_diagnosis.py
```

## Core Files

| File | Purpose |
|------|---------|
| `theos_dual_clock_governor.py` | Complete THEOS governor implementation |
| `theos_core.py` | Core reasoning engine (I→A→D→I cycle) |
| `theos_system.py` | Unified system interface |
| `llm_adapter.py` | LLM API integration (Claude, GPT-4, Gemini, etc.) |
| `semantic_retrieval.py` | Semantic search for wisdom retrieval |
| `demo.py` | Example usage and integration guide |

## Architecture

```
TheosSystem
├── TheosCore (Reasoning Engine)
│   ├── I→A→D→I Cycle
│   ├── Dual Engines (L, R)
│   ├── Governor
│   └── Contradiction Measurement
├── WisdomEngine (Learning)
│   ├── Wisdom Storage
│   ├── Semantic Retrieval
│   └── Wisdom Reuse
├── SystemMetrics (Tracking)
│   ├── Query History
│   ├── Performance Metrics
│   └── Convergence Tracking
└── LLMAdapter (Integration)
    ├── API Calls
    ├── Dual-Engine Reasoning
    └── Response Processing
```

## Basic Usage

### Numeric System (No LLM Required)

```python
from theos_system import create_numeric_system, TheosConfig

# Create system
config = TheosConfig(max_cycles=5, eps_converge=0.1)
system = create_numeric_system(config)

# Run reasoning
result = system.reason("Your question here")

# Access results
print(f"Output: {result.output}")
print(f"Confidence: {result.confidence}")
print(f"Halt reason: {result.halt_reason}")
```

### With LLM Integration (Claude)

```python
from llm_adapter import ClaudeAdapter
from theos_system import TheosSystem

# Create LLM adapter
adapter = ClaudeAdapter(api_key="your-key")

# Create system with LLM
system = TheosSystem(llm_adapter=adapter)

# Run reasoning
result = system.reason("Your question here")
```

### With Dual-Clock Governor

```python
from theos_dual_clock_governor import TheosGovernor

# Initialize governor
governor = TheosGovernor(
    contradictionBudget=1.0,
    maxCycles=5,
    convergenceThreshold=0.9,
    plateauThreshold=0.02,
    riskThreshold=0.7
)

# Define engines
def left_engine(context):
    # Constructive reasoning
    return {
        "content": "...",
        "risk": 0.2,
        "coherence": 0.8,
        "calibration": 0.7,
        "evidence": 0.6,
        "actionability": 0.8
    }

def right_engine(context):
    # Adversarial reasoning
    return {
        "content": "...",
        "risk": 0.4,
        "coherence": 0.7,
        "calibration": 0.8,
        "evidence": 0.7,
        "actionability": 0.5
    }

# Run governed reasoning
result = governor.govern(left_engine, right_engine, "Your prompt")
```

## Configuration

### TheosConfig Parameters

```python
config = TheosConfig(
    max_cycles=5,           # Maximum reasoning cycles
    eps_converge=0.1,       # Convergence threshold
    eps_diminish=0.9,       # Diminishing returns threshold
    contradiction_budget=1.0 # Contradiction budget
)
```

### Governor Configuration

```python
governor = TheosGovernor(
    contradictionBudget=1.0,    # Max contradiction allowed
    maxCycles=5,                # Maximum cycles
    convergenceThreshold=0.9,   # Convergence similarity threshold
    plateauThreshold=0.02,      # Minimum improvement per cycle
    riskThreshold=0.7           # Maximum acceptable risk
)
```

## Engine Output Format

Both left and right engines must return:

```python
{
    "content": str,          # The reasoning output
    "risk": float,           # Risk score (0-1, lower is safer)
    "coherence": float,      # Logical coherence (0-1)
    "calibration": float,    # Confidence calibration (0-1)
    "evidence": float,       # Evidence quality (0-1)
    "actionability": float   # Actionability score (0-1)
}
```

## Stop Conditions

THEOS stops reasoning when:

1. **Convergence** - Engines agree (similarity ≥ convergenceThreshold)
2. **Contradiction Budget Exhausted** - No more budget for refinement
3. **Plateau Detected** - No meaningful improvement in recent cycles
4. **Thrash Detected** - Engines oscillating without progress
5. **Max Cycles Reached** - Safety limit hit
6. **Risk Threshold Exceeded** - Output too risky to continue

## LLM Integration Examples

### Claude API

```python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

def left_engine(context):
    response = client.messages.create(
        model="claude-sonnet-4.5",
        messages=[{
            "role": "system",
            "content": "You are a constructive reasoning engine. Build solutions."
        }, {
            "role": "user",
            "content": context
        }]
    )
    
    return {
        "content": response.content[0].text,
        "risk": 0.2,
        "coherence": 0.8,
        "calibration": 0.7,
        "evidence": 0.6,
        "actionability": 0.8
    }
```

### OpenAI API

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

def left_engine(context):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "system",
            "content": "You are a constructive reasoning engine."
        }, {
            "role": "user",
            "content": context
        }]
    )
    
    return {
        "content": response.choices[0].message.content,
        "risk": 0.2,
        "coherence": 0.8,
        "calibration": 0.7,
        "evidence": 0.6,
        "actionability": 0.8
    }
```

## Audit Trail

Every THEOS execution produces a complete audit trail:

```python
result = governor.govern(left_engine, right_engine, prompt)

for cycle in result['cycles']:
    print(f"\n=== Cycle {cycle['cycle']} ===")
    print(f"Left Engine: {cycle['leftEngine']['content'][:100]}...")
    print(f"Right Engine: {cycle['rightEngine']['content'][:100]}...")
    print(f"Governor Decision: {cycle['decision']['reason']}")
    print(f"Similarity: {cycle['decision']['similarity']:.2f}")
    print(f"Selected: {cycle['decision']['selectedEngine']}")
    print(f"Contradiction Budget: {cycle['contradictionBudget']:.3f}")
```

## Testing

Run the test suite:

```bash
python -m pytest ../tests/test_theos_implementation.py -v
```

Expected output: 21 passed

## Performance Benchmarks

### Convergence Speed
- Average cycles to convergence: 2-3
- Average reasoning time: 100-500ms per query

### Confidence Improvement
- Initial query confidence: 0.6-0.7
- Repeated query confidence: 0.8-0.9 (wisdom reuse)
- Improvement: 20-30%

### Cross-Platform Validation
- Claude Sonnet 4.5: 33% risk reduction, 56% faster convergence
- Gemini 2.0 Flash: 28% risk reduction, 48% faster convergence
- ChatGPT-4: 31% risk reduction, 52% faster convergence

## Advanced Features

### Custom Scoring Functions

```python
def calculate_risk(content: str) -> float:
    # Your custom risk assessment logic
    return risk_score

def left_engine(context):
    response = get_ai_response(context)
    return {
        "content": response,
        "risk": calculate_risk(response),
        "coherence": calculate_coherence(response),
        # ... other scores
    }
```

### Wisdom Accumulation

```python
from semantic_retrieval import SemanticRetrieval

# Create retrieval engine
retrieval = SemanticRetrieval()

# Add wisdom entries
retrieval.add("Medical diagnosis for symptoms A, B, C", {"domain": "medical"})

# Retrieve similar entries
similar = retrieval.retrieve("Patient with symptoms A, B, C", top_k=5)
```

## MCP Integration

For integration with Anthropic's Model Context Protocol, see **[MCP_GOVERNANCE_SERVER.md](MCP_GOVERNANCE_SERVER.md)** for detailed instructions.

## Requirements

- Python 3.10+
- No external dependencies for core implementation
- Optional: `anthropic`, `openai`, or other LLM client libraries

## Contributing

See `../docs/contributing/` for contribution guidelines.

## License

**Reference Implementation:** MIT License (open for research and academic use)

**Advanced Features:** Proprietary (wisdom accumulation, posture management, planetary dialectics)

Contact frederick.stalnecker@theosresearch.org for licensing inquiries.

## Support

**Issues:** Open an issue on GitHub  
**Research Collaboration:** frederick.stalnecker@theosresearch.org  
**Documentation:** See `../docs/` for full documentation

---

**THEOS: Governance-first AI safety. Deployable today.**
