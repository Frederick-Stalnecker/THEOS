# THEOS Quick Start Guide

**Get THEOS running in 5 minutes**

---

## Option 1: Try THEOS Online (30 seconds)

Visit the live demo: **[THEOS Interactive Demo](https://theosdemo.manus.space)**

No installation needed. Ask any question and watch THEOS think through it in real-time.

---

## Option 2: Run Locally (5 minutes)

### Prerequisites
- Python 3.11+
- Git
- API key for at least one LLM (Claude, GPT-4, Gemini, etc.)

### Installation

```bash
# Clone the repository
git clone https://github.com/Frederick-Stalnecker/THEOS.git
cd THEOS

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up API keys
export CLAUDE_API_KEY="your-api-key-here"
# or
export OPENAI_API_KEY="your-api-key-here"
```

### Run THEOS

```bash
# Run interactive demo
python code/demo_theos_complete.py

# Or run specific test
python benchmarks/multi_llm_test_suite.py --llm claude

# Or start Jupyter notebook
jupyter lab
```

---

## Option 3: Use GitHub Codespaces (1 click)

1. Go to: https://github.com/Frederick-Stalnecker/THEOS
2. Click **Code** → **Codespaces** → **Create codespace on main**
3. Wait 60 seconds for environment to load
4. Run: `python code/demo_theos_complete.py`

Everything is pre-configured. No installation needed.

---

## Basic Usage

### Simple Query

```python
from code.theos_complete import THEOS

# Initialize THEOS with Claude
theos = THEOS(llm="claude", api_key="your-key")

# Ask a question
result = theos.query("What are the implications of AI safety?")

# View results
print(result.answer)           # Final answer
print(result.reasoning)        # Complete reasoning trace
print(result.confidence)       # Confidence level
print(result.wisdom_used)      # Wisdom accumulated
```

### Compare LLMs

```python
# Test same question across multiple LLMs
llms = ["claude", "gpt4", "gemini"]

for llm in llms:
    theos = THEOS(llm=llm, api_key="your-key")
    result = theos.query("What is consciousness?")
    print(f"{llm}: {result.answer}")
```

### Run Benchmarks

```bash
# Energy benchmarking
python benchmarks/energy_measurement.py --llm claude

# Multi-LLM testing
python benchmarks/multi_llm_test_suite.py --cycles 3

# Generate comparison report
python benchmarks/generate_cross_llm_analysis.py
```

---

## Key Concepts

### The THEOS Process

1. **Generation Phase** - Generate initial response
2. **Contradiction Phase** - Find potential issues
3. **Verification Phase** - Verify and correct
4. **Wisdom Phase** - Learn for future queries

### Cycles

- **1 Cycle** - Quick answer (1 reasoning pass)
- **2 Cycles** - Better answer (2 reasoning passes)
- **3 Cycles** - Best answer (3 reasoning passes)

More cycles = better accuracy but more energy/time

### Wisdom Accumulation

THEOS learns from each query:
- Stores verified information
- Recognizes patterns
- Improves over time
- Reduces computational overhead

---

## Configuration

### API Keys

Set environment variables for your LLM providers:

```bash
export CLAUDE_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="..."
export COHERE_API_KEY="..."
```

### Settings

Configure THEOS behavior:

```python
theos = THEOS(
    llm="claude",
    cycles=2,                    # Number of reasoning cycles
    temperature=0.7,             # Creativity level
    max_tokens=2000,            # Response length
    enable_wisdom=True,         # Use accumulated wisdom
    enable_governance=True,     # Verify outputs
    verbose=True                # Show reasoning steps
)
```

---

## Common Tasks

### Verify Information

```python
result = theos.query(
    "Is it true that X?",
    require_sources=True  # Request evidence
)
```

### Get Multiple Perspectives

```python
result = theos.query(
    "What are arguments for and against X?",
    perspectives=2  # Get multiple viewpoints
)
```

### Analyze Complex Problem

```python
result = theos.query(
    "How should we approach X?",
    cycles=3,  # Use more reasoning cycles
    depth="deep"  # Thorough analysis
)
```

### Compare with Standard AI

```python
# Standard response
standard = llm.query("What is X?")

# THEOS response
theos_result = theos.query("What is X?")

# Compare
print(f"Standard: {standard}")
print(f"THEOS: {theos_result.answer}")
print(f"Reasoning: {theos_result.reasoning}")
```

---

## Troubleshooting

### "API Key Not Found"
```bash
# Check your environment variable is set
echo $CLAUDE_API_KEY

# If not set, add to your shell profile
echo 'export CLAUDE_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

### "Module Not Found"
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "Rate Limit Exceeded"
- Wait a few minutes before retrying
- Use a different LLM provider
- Reduce the number of cycles

### "Low Accuracy Results"
- Try more cycles (2 or 3 instead of 1)
- Enable wisdom accumulation
- Ask more specific questions
- Check that API key is valid

---

## Next Steps

1. **Try the Demo** - Run `python code/demo_theos_complete.py`
2. **Read the Docs** - See `docs/README.md` for full documentation
3. **Run Benchmarks** - See `benchmarks/README.md` for testing
4. **Explore Code** - See `code/README.md` for implementation details
5. **Join Community** - GitHub Discussions for questions and ideas

---

## Resources

- **Documentation:** [docs/README.md](../README.md)
- **Benchmarking:** [benchmarks/README.md](../../benchmarks/README.md)
- **Code:** [code/README.md](../../code/README.md)
- **GitHub:** https://github.com/Frederick-Stalnecker/THEOS
- **Dashboard:** https://frederick-stalnecker.github.io/THEOS
- **Issues:** https://github.com/Frederick-Stalnecker/THEOS/issues
- **Discussions:** https://github.com/Frederick-Stalnecker/THEOS/discussions

---

## Getting Help

**Questions?**
- Check [FAQ.md](../../FAQ.md)
- Search [GitHub Issues](https://github.com/Frederick-Stalnecker/THEOS/issues)
- Ask in [GitHub Discussions](https://github.com/Frederick-Stalnecker/THEOS/discussions)

**Found a Bug?**
- Report in [GitHub Issues](https://github.com/Frederick-Stalnecker/THEOS/issues/new)
- Include error message and steps to reproduce

**Want to Contribute?**
- See [CONTRIBUTING.md](../../CONTRIBUTING.md)
- Read [CODE_OF_CONDUCT.md](../../CODE_OF_CONDUCT.md)

---

**Ready to start? Run:** `python code/demo_theos_complete.py`

**Questions? Ask:** https://github.com/Frederick-Stalnecker/THEOS/discussions
