#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/main.py"

echo "Starting SpaceMouse script..."
python3 "$PYTHON_SCRIPT"
