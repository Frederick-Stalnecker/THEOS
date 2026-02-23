#!/bin/bash
set -e

echo "🚀 Setting up THEOS Research Environment..."

# Update pip
python -m pip install --upgrade pip

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "🛠️ Installing development tools..."
pip install \
    pytest pytest-cov pytest-asyncio \
    black isort flake8 pylint \
    jupyter jupyterlab \
    pandas matplotlib seaborn \
    psutil memory-profiler \
    bandit safety

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p results benchmarks/data docs/dashboard

# Initialize git hooks (optional)
if [ -f .githooks/pre-commit ]; then
    git config core.hooksPath .githooks
    echo "✅ Git hooks configured"
fi

# Download test data if needed
if [ ! -f benchmarks/data/test_scenarios.json ]; then
    echo "📥 Downloading test scenarios..."
    # Add download logic here
fi

echo "✅ Environment setup complete!"
echo ""
echo "📚 Quick Start:"
echo "  - Run tests: pytest tests/"
echo "  - Run benchmarks: python benchmarks/multi_llm_test_suite.py"
echo "  - Start Jupyter: jupyter lab"
echo "  - View dashboard: python -m http.server 8000 --directory docs/dashboard"
echo ""
echo "🔗 Resources:"
echo "  - Documentation: docs/README.md"
echo "  - Benchmarking: benchmarks/README.md"
echo "  - Contributing: CONTRIBUTING.md"
