#!/usr/bin/env bash
# Setup script for Ontonaut project using uv

set -e

echo "🚀 Setting up Ontonaut development environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   brew install uv"
    exit 1
fi

# Create virtual environment using uv
echo "📦 Creating virtual environment at .venv..."
uv venv .venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Install the package in editable mode with dev dependencies
echo "📥 Installing package with dev dependencies..."
uv pip install -e ".[dev]"

# Install pre-commit hooks (if pre-commit is available)
if command -v pre-commit &> /dev/null; then
    echo "🪝 Installing pre-commit hooks..."
    pre-commit install
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "⚡ To activate the virtual environment in your current shell:"
echo ""
echo "   source .venv/bin/activate"
echo ""
echo "📝 Quick tip: You can also run setup and activate in one command:"
echo ""
echo "   source scripts/setup.sh   (instead of ./scripts/setup.sh)"
echo ""
echo "Once activated, you can:"
echo "  • Run tests:  ./scripts/test.sh  or  make test"
echo "  • Run linter: ./scripts/ruff.sh  or  make ruff"
echo "  • Build pkg:  ./scripts/build.sh or  make build"
echo ""

# If the script was sourced (not executed), activate automatically
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    echo "🎉 Virtual environment activated! You're ready to go."
    echo ""
fi
