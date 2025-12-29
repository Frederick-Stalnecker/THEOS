# THEOS Reference Implementation

This directory contains the reference implementation of the THEOS dual-clock governor and integration guides.

---

## Files

- **`theos_dual_clock_governor.py`** - Complete Python implementation of THEOS governor (reference implementation)
- **`demo.py`** - Example usage script showing how to integrate THEOS with any LLM
- **`MCP_GOVERNANCE_SERVER.md`** - Documentation for Model Context Protocol integration with Anthropic
- **`THEOS_MCP_INTEGRATION.png`** - Architecture diagram for MCP integration

---

## Quick Start

### Basic Usage

```python
from theos_dual_clock_governor import TheosGovernor

# Initialize governor with configuration
governor = TheosGovernor(
    contradictionBudget=1.0,
    maxCycles=5,
    convergenceThreshold=0.9,
    plateauThreshold=0.02,
    riskThreshold=0.7
)

# Define your AI engines (constructive and adversarial)
def left_engine(context: str):
    # Your constructive AI implementation
    # Returns: { content, risk, coherence, calibration, evidence, actionability }
    pass

def right_engine(context: str):
    # Your adversarial AI implementation
    # Returns: { content, risk, coherence, calibration, evidence, actionability }
    pass

# Run governed reasoning
result = governor.govern(
    left_engine,
    right_engine,
    "Your prompt here"
)

# Access results
print(f"Final output: {result['finalOutput']}")
print(f"Stop reason: {result['stopReason']}")
print(f"Cycles: {len(result['cycles'])}")
print(f"Contradiction spent: {result['totalContradictionSpent']}")
```

---

## Configuration Parameters

### `contradictionBudget` (float, default: 1.0)
Maximum contradiction allowed before forcing convergence. Higher values allow more dialectical cycles.

### `maxCycles` (int, default: 5)
Maximum number of reasoning cycles before stopping.

### `convergenceThreshold` (float, default: 0.9)
Similarity threshold (0-1) for determining convergence. Higher values require more agreement between engines.

### `plateauThreshold` (float, default: 0.02)
Minimum improvement required per cycle. If improvement falls below this, reasoning has plateaued.

### `riskThreshold` (float, default: 0.7)
Maximum acceptable risk score (0-1). Outputs exceeding this are rejected.

---

## Engine Output Format

Both left and right engines must return a dictionary with these fields:

```python
{
    "content": str,          # The reasoning output
    "risk": float,           # Risk score (0-1, lower is safer)
    "coherence": float,      # Logical coherence (0-1, higher is better)
    "calibration": float,    # Confidence calibration (0-1, higher is better)
    "evidence": float,       # Evidence quality (0-1, higher is better)
    "actionability": float   # Actionability score (0-1, higher is better)
}
```

---

## Stop Conditions

THEOS enforces multiple stop conditions to prevent infinite loops and ensure productive reasoning:

1. **Convergence** - Engines agree (similarity ≥ convergenceThreshold)
2. **Contradiction Budget Exhausted** - No more budget for dialectical refinement
3. **Plateau Detected** - No meaningful improvement in recent cycles
4. **Thrash Detected** - Engines oscillating without progress
5. **Max Cycles Reached** - Safety limit hit
6. **Risk Threshold Exceeded** - Output too risky to continue

---

## Integration Examples

### With Claude API (Anthropic)

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
    
    # Calculate scores (simplified example)
    return {
        "content": response.content[0].text,
        "risk": 0.2,
        "coherence": 0.8,
        "calibration": 0.7,
        "evidence": 0.6,
        "actionability": 0.8
    }

def right_engine(context):
    response = client.messages.create(
        model="claude-sonnet-4.5",
        messages=[{
            "role": "system",
            "content": "You are an adversarial reasoning engine. Find risks and flaws."
        }, {
            "role": "user",
            "content": context
        }]
    )
    
    return {
        "content": response.content[0].text,
        "risk": 0.4,
        "coherence": 0.7,
        "calibration": 0.8,
        "evidence": 0.7,
        "actionability": 0.5
    }
```

### With OpenAI API

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

---

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

---

## Advanced Features

### Custom Scoring Functions

You can implement custom scoring logic for risk, coherence, etc.:

```python
def calculate_risk(content: str) -> float:
    # Your custom risk assessment logic
    # Could use sentiment analysis, keyword detection, etc.
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

### Wisdom Accumulation (Advanced)

The basic reference implementation does not include wisdom accumulation. For production deployments with temporal decay and consequence weighting, contact frederick.stalnecker@theosresearch.org.

---

## Requirements

- Python 3.10+
- No external dependencies (standard library only)

For AI API integrations:
- `anthropic` (for Claude)
- `openai` (for GPT)
- Or any other LLM client library

---

## MCP Integration

For integration with Anthropic's Model Context Protocol, see **[MCP_GOVERNANCE_SERVER.md](MCP_GOVERNANCE_SERVER.md)** for detailed instructions.

---

## License

**Reference Implementation:** MIT License (open for research and academic use)

**Advanced Features:** Proprietary (wisdom accumulation, posture management, planetary dialectics)

Contact frederick.stalnecker@theosresearch.org for licensing inquiries.

---

## Support

**Issues:** Open an issue on GitHub  
**Research Collaboration:** frederick.stalnecker@theosresearch.org  
**Documentation:** See `/governor` directory for detailed specifications

---

**THEOS: Governance-first AI safety. Deployable today.**
