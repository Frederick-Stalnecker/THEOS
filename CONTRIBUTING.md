# Contributing to THEOS

Thank you for your interest in contributing to THEOS! This guide explains how to participate in the project, whether you're fixing bugs, adding features, improving documentation, or conducting research.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [Documentation](#documentation)
7. [Submitting Changes](#submitting-changes)
8. [Research Contributions](#research-contributions)

---

## Code of Conduct

THEOS is committed to providing a welcoming and inclusive environment. All contributors are expected to:

- Treat all people with respect and dignity
- Be constructive and collaborative in discussions
- Focus on the work, not personal criticism
- Report violations to the maintainers

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of THEOS concepts (read [GETTING_STARTED.md](GETTING_STARTED.md))

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/Frederick-Stalnecker/THEOS.git
cd THEOS

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verify installation
pytest tests/ -v
```

### Project Structure

Understanding the project layout helps you navigate the codebase:

```
THEOS/
├── code/                    # Core implementation
│   ├── theos_governor.py    # Main Governor class
│   ├── theos_dual_clock_governor.py  # Dual-clock system
│   └── demo.py              # Demo script
├── tests/                   # Test suite
│   ├── test_governor.py     # Governor tests
│   └── test_memory_engine.py # Memory engine tests
├── examples/                # Working examples
│   ├── medical_ethics.py
│   ├── ai_safety.py
│   └── financial_decision.py
├── docs/                    # Documentation
│   ├── API_REFERENCE.md
│   ├── INTEGRATION_GUIDE.md
│   └── TROUBLESHOOTING.md
└── .github/                 # GitHub configuration
    ├── workflows/           # CI/CD workflows
    └── ISSUE_TEMPLATE/      # Issue templates
```

---

## Development Workflow

### 1. Create an Issue

Before starting work, create an issue describing what you want to do:

- **Bug Report** - Use the bug report template
- **Feature Request** - Use the feature request template
- **Documentation** - Create a general issue

This allows discussion before you invest time in implementation.

### 2. Fork and Branch

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/THEOS.git
cd THEOS

# Create a feature branch
git checkout -b feature/your-feature-name
# or for bug fixes
git checkout -b fix/bug-description
```

### 3. Make Changes

Make your changes following the coding standards below. Keep commits atomic and descriptive:

```bash
git add file1.py file2.py
git commit -m "Add feature X

Description of what was added and why.
Fixes #123"
```

### 4. Test Your Changes

Run the full test suite before submitting:

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_governor.py::TestGovernorCore -v

# Run with coverage
pytest tests/ --cov=code --cov-report=html

# Check code formatting
black --check code/ tests/

# Check imports
isort --check-only code/ tests/

# Run linter
flake8 code/ --max-line-length=120
```

### 5. Push and Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create pull request on GitHub
# Fill out the pull request template
# Link the issue: "Fixes #123"
```

### 6. Address Review Comments

Respond to reviewer feedback, make requested changes, and push updates:

```bash
# Make changes
git add file.py
git commit -m "Address review feedback"
git push origin feature/your-feature-name
```

### 7. Merge

Once approved, the maintainer will merge your pull request.

---

## Coding Standards

### Python Style

THEOS follows PEP 8 with these tools:

**Black** - Code formatting:
```bash
black code/ tests/ examples/
```

**isort** - Import sorting:
```bash
isort code/ tests/ examples/
```

**flake8** - Linting:
```bash
flake8 code/ --max-line-length=120
```

### Type Hints

All code should include type hints:

```python
from typing import List, Dict, Optional

def evaluate_cycle(
    self,
    left_output: EngineOutput,
    right_output: EngineOutput,
    current_budget: float,
    cycle_number: int
) -> GovernorEvaluation:
    """Evaluate a single reasoning cycle."""
    pass
```

### Docstrings

Use docstrings for all public classes and methods:

```python
def compute_similarity(self, left: str, right: str) -> float:
    """
    Compute similarity between two text outputs.
    
    Args:
        left: First output text
        right: Second output text
    
    Returns:
        Similarity score (0.0-1.0)
        - 1.0: Identical
        - 0.5: Moderate similarity
        - 0.0: Completely different
    
    Raises:
        ValueError: If either input is empty
    """
    pass
```

### Comments

Use comments to explain why, not what:

```python
# ✅ Good: Explains the reasoning
# Use a higher similarity threshold for medical decisions
# to ensure engines strongly agree before proceeding
similarity_threshold = 0.95

# ❌ Bad: Just restates the code
# Set similarity threshold to 0.95
similarity_threshold = 0.95
```

### Naming Conventions

- **Classes** - PascalCase (THEOSGovernor, EngineOutput)
- **Functions/Methods** - snake_case (evaluate_cycle, compute_similarity)
- **Constants** - UPPER_SNAKE_CASE (MAX_CYCLES, DEFAULT_THRESHOLD)
- **Private** - Prefix with underscore (_internal_method)

---

## Testing

### Writing Tests

All new code should include tests. Use pytest:

```python
import pytest
from code.theos_governor import THEOSGovernor, EngineOutput

class TestMyFeature:
    """Tests for my new feature."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        governor = THEOSGovernor()
        
        left = EngineOutput(
            reasoning_mode="Constructive",
            output="Test output",
            confidence=0.85,
            internal_monologue="Test"
        )
        
        right = EngineOutput(
            reasoning_mode="Critical",
            output="Test output",
            confidence=0.80,
            internal_monologue="Test"
        )
        
        evaluation = governor.evaluate_cycle(left, right, 1.0, 1)
        
        assert evaluation.decision in ["CONTINUE", "STOP"]
        assert 0 <= evaluation.similarity_score <= 1
    
    def test_edge_case(self):
        """Test edge case."""
        # Test implementation
        pass
```

### Test Coverage

Aim for high test coverage:

```bash
# Generate coverage report
pytest tests/ --cov=code --cov-report=html

# View report
open htmlcov/index.html
```

Current coverage: **100% of core functionality**

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_governor.py -v

# Run specific test class
pytest tests/test_governor.py::TestGovernorCore -v

# Run specific test
pytest tests/test_governor.py::TestGovernorCore::test_similarity -v

# Run with output
pytest tests/ -v -s

# Run with coverage
pytest tests/ --cov=code --cov-report=html
```

---

## Documentation

### Writing Documentation

Documentation is as important as code. When adding features:

1. **Update docstrings** - Add/update method docstrings
2. **Update API reference** - Add to [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
3. **Update examples** - Add example in [examples/](examples/) if applicable
4. **Update guides** - Update relevant guides in [docs/](docs/)

### Documentation Standards

- Use clear, concise language
- Include examples where helpful
- Explain the "why" not just the "what"
- Keep documentation up-to-date with code

### Markdown Style

- Use headers hierarchically (H1 → H2 → H3)
- Use code blocks with language specification
- Use tables for structured data
- Use blockquotes for important notes
- Link to related documentation

---

## Submitting Changes

### Pull Request Checklist

Before submitting a pull request, ensure:

- [ ] Code follows style guidelines (black, isort, flake8)
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] Docstrings added/updated
- [ ] No new linting warnings
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains changes clearly

### Pull Request Template

Use the provided template in [.github/pull_request_template.md](.github/pull_request_template.md):

- Describe the changes
- Link related issues
- Explain testing approach
- List any breaking changes

### Commit Messages

Write clear, descriptive commit messages:

```
Add feature X to improve Y

- Implemented new functionality
- Added comprehensive tests
- Updated documentation

Fixes #123
```

### Code Review

All pull requests require review before merging. Reviewers will check:

- **Correctness** - Does the code work correctly?
- **Quality** - Does it follow standards?
- **Tests** - Are there adequate tests?
- **Documentation** - Is it documented?
- **Performance** - Does it have acceptable performance?

---

## Research Contributions

THEOS welcomes research contributions and validation work.

### Research Areas

- **Cross-platform validation** - Test THEOS on new AI platforms
- **Performance optimization** - Improve speed or memory usage
- **Formal verification** - Mathematical proofs of properties
- **Wisdom systems** - Improve wisdom accumulation
- **New architectures** - Explore native implementations
- **Applications** - Real-world use cases and case studies

### Research Workflow

1. **Propose research** - Open an issue describing your research question
2. **Discuss approach** - Get feedback on methodology
3. **Conduct research** - Perform the research work
4. **Document findings** - Write up results and methodology
5. **Submit results** - Create pull request with findings
6. **Peer review** - Get feedback from community

### Publishing Research

If you conduct research using THEOS:

- Cite THEOS in your publications
- Share results with the community
- Consider contributing findings back to THEOS
- Link to your publications in THEOS documentation

---

## Getting Help

### Resources

- **Documentation** - [docs/](docs/) directory
- **Examples** - [examples/](examples/) directory
- **Tests** - [tests/](tests/) directory
- **Issues** - GitHub Issues for questions
- **Discussions** - GitHub Discussions (when enabled)

### Asking Questions

When asking questions:

- Search existing issues first
- Provide minimal reproducible example
- Include Python version and THEOS version
- Describe what you expected vs. what happened

---

## Recognition

Contributors are recognized in:

- **CHANGELOG.md** - Listed in release notes
- **GitHub** - Shown as contributor
- **Documentation** - Acknowledged in relevant sections

---

## License

By contributing to THEOS, you agree that your contributions will be licensed under the MIT License.

---

## Questions?

If you have questions about contributing:

1. Check this guide
2. Check existing issues
3. Open a new issue with your question
4. Contact the maintainer

---

**Thank you for contributing to THEOS!**

---

**Last Updated:** February 19, 2026  
**Maintainer:** Frederick Davis Stalnecker
