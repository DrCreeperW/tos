#!/usr/bin/env bash
#
# run.sh — Start TOS (Terminal Operating System)
# Simple launcher for development
#

set -e

cd "$(dirname "$0")"

echo "╔══════════════════════════════════════╗"
echo "║      TOS — Starting                  ║"
echo "╚══════════════════════════════════════╝"

# Try to use venv python if it exists (recommended)
if [ -f "../tosenv/bin/python" ]; then
    PYTHON="../tosenv/bin/python"
elif [ -f "../tosenv/Scripts/python.exe" ]; then
    # Windows venv fallback (Git Bash / WSL interop)
    PYTHON="../tosenv/Scripts/python.exe"
else
    PYTHON="python3"
fi

echo "[TOS] Using Python: $PYTHON"
echo "[TOS] Launching shell..."

$PYTHON shell.py

echo "[TOS] Shutdown complete."