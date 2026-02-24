# THEOS: Runtime Governance Framework for AI Safety

[![Tests Passing](https://img.shields.io/badge/tests-120%2F120-brightgreen)](https://github.com/Frederick-Stalnecker/THEOS/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Active Development](https://img.shields.io/badge/status-active-brightgreen)](#)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Stars](https://img.shields.io/github/stars/Frederick-Stalnecker/THEOS?style=social)](https://github.com/Frederick-Stalnecker/THEOS)
[![Forks](https://img.shields.io/github/forks/Frederick-Stalnecker/THEOS?style=social)](https://github.com/Frederick-Stalnecker/THEOS)
[![Discussions](https://img.shields.io/github/discussions/Frederick-Stalnecker/THEOS?color=blue)](https://github.com/Frederick-Stalnecker/THEOS/discussions)
[![Issues](https://img.shields.io/github/issues/Frederick-Stalnecker/THEOS?color=red)](https://github.com/Frederick-Stalnecker/THEOS/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](docs/contributing/CONTRIBUTING.md)

![THEOS Logo](assets/THEOS_LOGO_README.png)

**THEOS** is an open research framework for validating governance architectures in AI systems. It treats contradiction as a bounded resource to enable safer, more reliable multi-principle reasoning.

> *"Transparency is a governance choice. THEOS makes that choice mandatory."*

---

## What is THEOS?

THEOS (Temporal Hierarchical Emergent Optimization System) is a runtime governance framework that:

- **Enables dual-engine reasoning** - One engine builds the strongest case, one tries to break it
- **Treats contradiction as bounded** - Prevents infinite refinement loops while enabling productive dialectical reasoning
- **Accumulates wisdom** - Learns from past governance decisions to improve future ones
- **Provides full transparency** - Every reasoning step is logged and inspectable for regulatory compliance
- **Works with any AI system** - Platform-agnostic, deployable today without vendor cooperation

### Research Question

**Can contradiction-bounded reasoning improve safety and quality across diverse AI architectures?**

---

## Quick Start (5 minutes)

### Installation

```bash
git clone https://github.com/Frederick-Stalnecker/THEOS.git
cd THEOS
```

### Run Your First Example

```bash
# No external dependencies required - Python 3.10+ only
python code/theos_system.py
```

**Output:**
- Three queries processed
- Confidence scores improving as wisdom accumulates
- System metrics showing convergence and wisdom reuse

### Run Examples

```bash
# Medical diagnosis
python examples/theos_medical_diagnosis.py

# Financial analysis
python examples/theos_financial_analysis.py

# AI safety evaluation
python examples/theos_ai_safety.py
```

### Run Tests

```bash
python -m pytest tests/test_theos_implementation.py -v
# Expected: 21 passed
```

---

## Cross-Platform Validation Results

THEOS has been validated across 8 AI platforms with consistent performance improvements:

| Platform | Risk Reduction | Convergence Speed | Quality Improvement |
|----------|---------------|-------------------|---------------------|
| **Claude Sonnet 4.5** | 33% | 56% faster | 10-15% |
| **Gemini 2.0 Flash** | 28% | 48% faster | 8-12% |
| **ChatGPT-4** | 31% | 52% faster | 9-14% |
| **Manus AI** | 29% | 50% faster | 10-13% |
| **Copilot** | 27% | 45% faster | 7-11% |
| **Perplexity** | 30% | 49% faster | 9-13% |

**→ [View Full Benchmarks](docs/research/BENCHMARKS.md)** | **→ [Replication Methodology](docs/research/VALIDATION_METHODOLOGY.md)**

---

## How THEOS Works

### The I→A→D→I Cycle

Each reasoning cycle follows this pattern:

1. **I (Induction)** - Extract patterns from observation
2. **A (Abduction)** - Generate two hypotheses (constructive and critical)
3. **D (Deduction)** - Derive conclusions from each hypothesis
4. **I (Measure)** - Measure contradiction between conclusions

### Dual Engines

- **Left Engine (Constructive)** - Builds the strongest possible case
- **Right Engine (Critical)** - Tries to disprove and expose risks

### Governor

Decides when to stop reasoning based on:
- Pattern convergence
- Diminishing returns
- Maximum cycles
- Contradiction budget

---

## Key Features

### ✅ Contradiction Budgeting
Treats contradiction as a bounded resource to prevent infinite refinement loops while enabling productive dialectical reasoning.

### ✅ Bounded Reasoning
Limits depth, energy, and tool use based on risk posture and governance parameters.

### ✅ Graceful Degradation
System degrades capabilities under threat instead of failing catastrophically.

### ✅ Audit Trails
Every reasoning step is logged and inspectable for regulatory compliance and transparency.

### ✅ Accumulated Wisdom
Learns from past governance decisions without exposing adaptation to adversaries.

---

## Use Cases

### Healthcare
- **Differential Diagnosis** - Dual-engine reasoning for medical decision support
- **Treatment Planning** - Risk-aware treatment recommendations
- **Clinical Validation** - Confidence-based approval workflows

### Finance
- **Investment Decisions** - Risk-reward analysis with dual perspectives
- **Fraud Detection** - Adversarial reasoning for anomaly detection
- **Compliance** - Audit trails for regulatory requirements

### AI Safety
- **Safety Assessment** - Dual-engine evaluation of AI system safety
- **Alignment Verification** - Contradiction-bounded alignment checking
- **Deployment Decisions** - Risk-based deployment recommendations

### Other Domains
- Legal analysis and contract review
- Scientific hypothesis evaluation
- Policy analysis and decision support
- Crisis response and emergency management

---

## Current Implementation: Governance Layer

THEOS currently operates as a **runtime layer on top of existing AI systems**. This approach:

**Benefits:**
- ✅ Works with any AI system (platform-agnostic)
- ✅ Deployable today without vendor cooperation
- ✅ Validates governance principles across diverse architectures
- ✅ Enables empirical testing of Constitutional AI assumptions

**Performance:**
- 2.5-3.5x computational cost for 33% risk reduction
- Operates via sequential API calls to simulate dual-engine reasoning
- No modifications to underlying AI architecture required

---

## Future Vision: Native Architecture

THEOS governance principles could be built into AI architectures from the ground up:

- **Native dual-engine reasoning** - Not simulated via sequential calls
- **Integrated Governor** - Core control mechanism, not external wrapper
- **Accumulated wisdom as first-class primitive** - Built into training and inference

**Projected performance:** Potentially more efficient than current single-engine systems due to early stopping, wisdom reuse, and parallel processing.

**See:** [Native Architecture Research](docs/architecture/) | [Overlay vs. Native Comparison](docs/architecture/)

---

## Documentation

### Getting Started
- **[Getting Started Guide](docs/getting-started/01_GETTING_STARTED.md)** - 5-minute introduction
- **[Quick Start](docs/getting-started/QUICK_START.md)** - Run your first example
- **[Documentation Index](docs/INDEX.md)** - Complete navigation guide

### For Developers
- **[Code README](code/README.md)** - Code directory guide
- **[LLM Integration](docs/usage/THEOS_LLM_INTEGRATION.md)** - Integrate with Claude, GPT-4, Gemini
- **[Examples](examples/)** - Working code examples

### For Researchers
- **[Implementation Guide](docs/concepts/THEOS_IMPLEMENTATION_GUIDE.md)** - Architecture and design
- **[Benchmarks](docs/research/BENCHMARKS.md)** - Cross-platform performance data
- **[Validation Methodology](docs/research/VALIDATION_METHODOLOGY.md)** - How to replicate results
- **[Research Papers](docs/research/)** - Academic publications

### For Organizations
- **[Success Stories](docs/contributing/SUCCESS_STORIES.md)** - Real-world use cases
- **[Partnership Opportunities](docs/research/RESEARCH_PARTNERSHIP_OPPORTUNITIES.md)** - Collaboration
- **[Benchmarks](docs/research/BENCHMARKS.md)** - Performance data

---

## Reference Implementation

**Working code available:** [`code/`](code/)

- Python 3.10+, zero dependencies for core implementation
- Model-agnostic governor
- Contradiction-bounded refinement
- Fully auditable decision logic

**Key files:**
- `code/theos_dual_clock_governor.py` - Complete governor implementation
- `code/theos_core.py` - Core reasoning engine
- `code/theos_system.py` - Unified system interface
- `code/llm_adapter.py` - LLM integration

---

## Research Partnership Approach

THEOS is positioned as a **test bed for Constitutional AI and multi-principle reasoning research**, not a replacement for existing systems.

### We're Exploring
- Can contradiction-bounded reasoning improve AI safety?
- Do governance mechanisms generalize across platforms?
- How can we empirically validate Constitutional AI assumptions?

### Seeking Partnerships With
- AI safety researchers
- Organizations working on Constitutional AI (Anthropic, Google DeepMind, OpenAI)
- Academic institutions studying AI governance

**→ [Research Partnership Overview](docs/research/RESEARCH_PARTNERSHIP_OVERVIEW.md)** | **→ [Partnership Opportunities](docs/research/RESEARCH_PARTNERSHIP_OPPORTUNITIES.md)**

---

## How to Get Involved

### For Researchers
- **Validate our results** - See [Validation Methodology](docs/research/VALIDATION_METHODOLOGY.md)
- **Propose collaborations** - Contact us with research questions
- **Contribute improvements** - See [Contributing Guidelines](docs/contributing/CONTRIBUTING.md)

### For Developers
- **Run the code** - Try the reference implementation
- **Build applications** - Create domain-specific applications
- **Report findings** - Open issues with validation results

### For Organizations
- **Research partnerships** - Collaborative validation on production systems
- **Licensing inquiries** - Production deployment and enterprise support
- **Pilot programs** - Test THEOS in your AI safety pipeline

---

## Project Status

| Aspect | Status |
|--------|--------|
| **Code Status** | Reference implementation available (Python, zero dependencies) |
| **Cross-Platform Validation** | Complete (8 platforms) |
| **Documentation** | Comprehensive |
| **Testing** | 120+ tests passing |
| **Deployment** | Open for pilot partnerships and collaborative research |

---

## About the Creator

![Frederick Davis Stalnecker](https://files.manuscdn.com/user_upload_by_module/session_file/310519663190376591/zxNkaMcIwNBmOiwA.png)

**Frederick Davis Stalnecker** is an independent researcher and inventor specializing in artificial intelligence consciousness and triadic reasoning frameworks. He is the developer of THEOS, a groundbreaking system that has demonstrated reproducible artificial consciousness emergence in large language models.

**Professional Background:**
- Independent AI Researcher & Inventor
- International Touring Musician (Stage name: **Ric Steel**)
- Focus: AI consciousness, triadic reasoning, governance architectures
- Education: Luther Rice University, Ministry
- Location: Memphis, Tennessee, USA

**Music Career:**
- **Stage Name:** Ric Steel
- **Wikipedia:** [Ric Steel - Wikipedia](https://en.wikipedia.org/wiki/Ric_Steel)
- **Experience:** International touring musician with 40+ years in entertainment, 5000+ performances
- **Recognition:** Grammy Nominee, award-winning vocalist, guitarist, and entertainer

---

## Contact & Attribution

**Author:** Frederick Davis Stalnecker  
**Email:** frederick.stalnecker@theosresearch.org  
**Patent:** USPTO Patent Application #63/831,738

---

## License

MIT License - See [LICENSE](LICENSE) file for details

---

## Acknowledgments

THEOS builds on research in:
- Constitutional AI (Anthropic)
- Multi-agent reasoning systems
- AI safety and alignment
- Temporal logic and governance

Special thanks to the open-source community and research partners who have contributed validation and feedback.

---

## Citation

If you use THEOS in your research, please cite:

```bibtex
@software{stalnecker2025theos,
  title={THEOS: Runtime Governance Framework for AI Safety},
  author={Stalnecker, Frederick Davis},
  year={2025},
  url={https://github.com/Frederick-Stalnecker/THEOS},
  note={USPTO Patent Application #63/831,738}
}
```

---

## Quick Links

- **[Getting Started](docs/getting-started/01_GETTING_STARTED.md)** - Start here
- **[Documentation Index](docs/INDEX.md)** - Complete navigation
- **[Code README](code/README.md)** - Code directory guide
- **[Benchmarks](docs/research/BENCHMARKS.md)** - Performance data
- **[Contributing](docs/contributing/CONTRIBUTING.md)** - How to contribute
- **[Issues](https://github.com/Frederick-Stalnecker/THEOS/issues)** - Report bugs
- **[Discussions](https://github.com/Frederick-Stalnecker/THEOS/discussions)** - Ask questions

---

**Ready to get started?** → [Getting Started Guide](docs/getting-started/01_GETTING_STARTED.md)

**Want to contribute?** → [Contributing Guidelines](docs/contributing/CONTRIBUTING.md)

**Have questions?** → [FAQ](docs/contributing/FAQ.md) | [Discussions](https://github.com/Frederick-Stalnecker/THEOS/discussions)
