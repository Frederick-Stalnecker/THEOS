#!/bin/bash
set -e

echo "Setting up THEOS Development Environment..."

# Update pip
python -m pip install --upgrade pip

# Install THEOS package in editable mode with all dev and LLM dependencies
echo "Installing THEOS package and dependencies..."
pip install -e ".[dev,llm]"

# Create results directory for experiments
mkdir -p experiments/results

echo ""
echo "THEOS environment ready."
echo ""
echo "Quick Start:"
echo "  Run tests:           pytest tests/ -v"
echo "  Run demo:            python code/theos_system.py"
echo "  Run experiment:      python experiments/insight_experiment.py --backend mock --questions 3"
echo "  Real experiment:     ANTHROPIC_API_KEY=sk-... python experiments/insight_experiment.py --backend anthropic --questions 10"
echo ""
echo "Key files:"
echo "  code/theos_core.py        — The I->A->D->I cycle"
echo "  code/theos_governor.py    — The contradiction governor"
echo "  experiments/INSIGHT_RUBRIC.md — How to evaluate THEOS output"
echo ""
