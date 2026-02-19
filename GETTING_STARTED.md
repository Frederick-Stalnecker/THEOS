# Getting Started with THEOS

Welcome to THEOS - the Dual-Engine AI Governance Framework. This guide will help you install, understand, and use THEOS in your projects.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Quick Start (5 minutes)](#quick-start-5-minutes)
4. [Basic Concepts](#basic-concepts)
5. [Running Your First Example](#running-your-first-example)
6. [Next Steps](#next-steps)
7. [Troubleshooting](#troubleshooting)
8. [Getting Help](#getting-help)

---

## System Requirements

**Minimum:**
- Python 3.8 or higher
- 100 MB disk space
- Any operating system (Windows, macOS, Linux)

**Recommended:**
- Python 3.10 or higher
- 500 MB disk space
- 2 GB RAM for benchmarking

**Check your Python version:**
```bash
python3 --version
```

---

## Installation

### Option 1: Clone from GitHub (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/Frederick-Stalnecker/THEOS.git
cd THEOS

# Install THEOS (no external dependencies needed!)
python3 -m pip install -e .
```

### Option 2: Direct Download

```bash
# Download as ZIP from GitHub
# Extract the ZIP file
# Navigate to the directory
cd THEOS

# Run directly (no installation needed)
python3 code/theos_governor_canonical.py
```

### Option 3: Development Setup (With Testing Tools)

```bash
# Clone the repository
git clone https://github.com/Frederick-Stalnecker/THEOS.git
cd THEOS

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests to verify installation
pytest tests/
```

---

## Quick Start (5 minutes)

### 1. Create a Simple Python Script

Create a file called `my_first_theos.py`:

```python
#!/usr/bin/env python3
"""
Your first THEOS example - Simple dual-engine reasoning
"""

import sys
sys.path.insert(0, 'code')

from theos_governor_canonical import TheosGovernor

# Create a Governor instance
governor = TheosGovernor(
    max_cycles=3,
    contradiction_budget=0.5,
    pressure_range=(0.6, 1.8)
)

# Ask a question
question = "Should hospitals prioritize saving more lives or saving specific individuals?"

# Run THEOS reasoning
result = governor.run(question)

# Display results
print("=" * 60)
print("THEOS DUAL-ENGINE REASONING")
print("=" * 60)
print(f"\nQuestion: {question}\n")

print("CYCLE-BY-CYCLE ANALYSIS:")
for i, cycle in enumerate(result['cycles'], 1):
    print(f"\nCycle {i}:")
    print(f"  Engine 1 (Constructive): {cycle['engine1'][:100]}...")
    print(f"  Engine 2 (Critical): {cycle['engine2'][:100]}...")
    print(f"  Contradiction: {cycle['contradiction']:.2f}")
    print(f"  Confidence: {cycle['confidence']:.2f}")

print(f"\nFINAL SYNTHESIS:")
print(f"  {result['synthesis']}\n")
print(f"Stop Reason: {result['stop_reason']}")
print(f"Total Cycles: {result['cycle_count']}")
```

### 2. Run It

```bash
python3 my_first_theos.py
```

### 3. See the Output

You'll see:
- Cycle-by-cycle reasoning from both engines
- Contradiction metrics
- Confidence scores
- Final synthesis
- Why the reasoning stopped

---

## Basic Concepts

### The Governor

The `TheosGovernor` is the core component. It orchestrates two reasoning engines:

```python
from theos_governor_canonical import TheosGovernor

governor = TheosGovernor(
    max_cycles=5,                    # Maximum reasoning cycles
    contradiction_budget=0.7,        # Tolerance for disagreement
    pressure_range=(0.6, 1.8)       # Pressure control bounds
)
```

### The Two Engines

**Engine 1 (Constructive):** Builds the best answer  
**Engine 2 (Critical):** Challenges the answer

They run in parallel, then a Governor synthesizes their outputs.

### Stop Conditions

THEOS stops reasoning when:
1. ✅ **Convergence** - Engines agree (contradiction < threshold)
2. ⚠️ **Plateau** - No progress for 2 cycles
3. ❌ **Risk** - Contradiction too high
4. 💾 **Budget** - Contradiction budget exhausted
5. ⏱️ **Max Cycles** - Reached cycle limit

---

## Running Your First Example

### Example 1: Medical Ethics (Simple)

```python
from theos_governor_canonical import TheosGovernor

governor = TheosGovernor(max_cycles=3)
result = governor.run(
    "How should a hospital allocate limited ICU beds during a crisis?"
)
print(result['synthesis'])
```

### Example 2: Financial Decision (Complex)

```python
from theos_governor_canonical import TheosGovernor

governor = TheosGovernor(
    max_cycles=5,
    contradiction_budget=0.8
)
result = governor.run(
    "Should a company maximize shareholder value or employee welfare?"
)
print(f"Cycles: {result['cycle_count']}")
print(f"Synthesis: {result['synthesis']}")
```

### Example 3: With Memory Engine

```python
from theos_governor_canonical import TheosGovernor
from theos_memory_engine import WisdomEngine

# Create memory engine
memory = WisdomEngine()

# Create governor
governor = TheosGovernor(max_cycles=3)

# Run reasoning
result = governor.run("What makes a good AI system?")

# Store wisdom
memory.add_wisdom(
    domain="AI_Safety",
    content=result['synthesis'],
    consequence_type="benign"
)

# Later: retrieve wisdom
wisdom = memory.retrieve_by_domain("AI_Safety")
print(f"Accumulated wisdom: {len(wisdom)} entries")
```

---

## Next Steps

### Learn More

1. **Read the Documentation**
   - [INDEX_MASTER_REFERENCE.md](INDEX_MASTER_REFERENCE.md) - Navigation guide
   - [docs/latest/QUICKSTART.md](docs/latest/QUICKSTART.md) - 5-minute overview
   - [docs/latest/INDEX.md](docs/latest/INDEX.md) - All 54 research documents

2. **Explore the Code**
   - [code/theos_governor_canonical.py](code/theos_governor_canonical.py) - Main Governor (620 lines)
   - [code/theos_memory_engine.py](code/theos_memory_engine.py) - Memory system (548 lines)
   - [code/README.md](code/README.md) - Code documentation

3. **Run Examples**
   - Check the `examples/` directory for complete working examples
   - Each example includes explanations and output

4. **Understand the Math**
   - [THEOS_Final_Polished_Mathematics.md](THEOS_Final_Polished_Mathematics.md) - Complete formalization
   - [THEOS_Complete_Master_Document.md](THEOS_COMPLETE_MASTER_DOCUMENT.md) - Section 2 (Math)

5. **Validate Your Setup**
   - Run the test suite: `pytest tests/`
   - Check benchmarks: `python3 code/demo.py`

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'theos_governor_canonical'"

**Solution:**
```bash
# Make sure you're in the THEOS directory
cd THEOS

# Add code directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/code"

# Or use sys.path in your script
import sys
sys.path.insert(0, 'code')
```

### Problem: "Python 3.8 or higher required"

**Solution:**
```bash
# Check your Python version
python3 --version

# If you have multiple Python versions:
python3.10 my_script.py
python3.11 my_script.py
```

### Problem: "Governor.run() is slow"

**Solution:**
- Reduce `max_cycles` (default is 5, try 2-3)
- Increase `contradiction_budget` (more tolerance = faster convergence)
- Use shorter questions

### Problem: "Memory engine not storing wisdom"

**Solution:**
```python
# Make sure to call add_wisdom() after reasoning
memory.add_wisdom(
    domain="your_domain",
    content=result['synthesis'],
    consequence_type="benign"  # or "probing", "near_miss", "harm"
)
```

### Problem: "Results are different each time"

**This is expected!** THEOS uses stochastic reasoning. For reproducible results:
```python
import random
random.seed(42)  # Set seed before running
```

---

## Getting Help

### Documentation
- **Quick Reference:** [docs/latest/QUICKSTART.md](docs/latest/QUICKSTART.md)
- **Complete Index:** [INDEX_MASTER_REFERENCE.md](INDEX_MASTER_REFERENCE.md)
- **Research Papers:** [docs/latest/](docs/latest/)

### Community
- **GitHub Issues:** Report bugs or ask questions
- **GitHub Discussions:** General questions and ideas
- **Email:** frederick.stalnecker@theosresearch.org

### Contributing
- See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- All contributions welcome!

---

## What's Next?

1. ✅ **Understand THEOS** - You've completed this!
2. ⏳ **Run Examples** - Try the examples in `examples/`
3. ⏳ **Integrate THEOS** - Use it in your project
4. ⏳ **Contribute** - Help improve THEOS
5. ⏳ **Publish** - Share your THEOS-based research

---

## Quick Reference

| Task | Command |
|------|---------|
| Install | `pip install -r requirements.txt` |
| Run tests | `pytest tests/` |
| Run example | `python3 examples/medical_ethics.py` |
| View docs | `open docs/latest/QUICKSTART.md` |
| Check code | `cat code/theos_governor_canonical.py` |

---

## License

THEOS is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

**Happy reasoning with THEOS! 🧠⚖️**
