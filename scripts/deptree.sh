#!/usr/bin/env bash

# Show dependency tree for the project
# Uses pipdeptree to visualize package dependencies

set -e

echo "📦 Ontonaut Dependency Tree"
echo "=============================="
echo ""

# Check if pipdeptree is installed
if ! command -v pipdeptree &> /dev/null; then
    echo "📥 Installing pipdeptree..."
    pip install pipdeptree
    echo ""
fi

# Show dependency tree for ontonaut
echo "🔍 Direct dependencies:"
pipdeptree -p ontonaut --depth 1

echo ""
echo "🌳 Full dependency tree:"
pipdeptree -p ontonaut

echo ""
echo "📊 Reverse dependencies (what depends on ontonaut):"
pipdeptree -r -p ontonaut

echo ""
echo "✅ Dependency tree complete!"

