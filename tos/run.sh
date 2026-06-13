#!/usr/bin/env bash
#
# run.sh — Start TOS (Terminal Operating System)
#
set -e

TOS_DIR="$(cd "$(dirname "$0")" && pwd)"
DISPLAY_NUM="${DISPLAY_NUM:-99}"
DISPLAY=":${DISPLAY_NUM}"
PYTHON="/usr/bin/python3"

echo "╔══════════════════════════════════════╗"
echo "║      TOS — Terminal Operating System ║"
echo "║      Starting up...                  ║"
echo "╚══════════════════════════════════════╝"

# Start Xvfb if no display available
if ! xdpyinfo -display "$DISPLAY" &>/dev/null 2>&1; then
    echo "[TOS] Starting Xvfb on display ${DISPLAY}..."
    Xvfb "$DISPLAY" -screen 0 1024x768x24 &
    XVFB_PID=$!
    sleep 1
    if ! kill -0 "$XVFB_PID" 2>/dev/null; then
        echo "[TOS] ERROR: Xvfb failed to start!"
        exit 1
    fi
    echo "[TOS] Xvfb running (PID: $XVFB_PID)"
else
    echo "[TOS] Display ${DISPLAY} already available"
    XVFB_PID=""
fi

export DISPLAY="$DISPLAY"

# Launch TOS Shell
echo "[TOS] Launching TOS Shell..."
cd "$TOS_DIR"
$PYTHON shell.py &
TOS_PID=$!
echo "[TOS] TOS Shell started (PID: $TOS_PID)"
echo "[TOS] Login with: user / tos"

# Wait for TOS to exit
wait $TOS_PID 2>/dev/null

# Cleanup
if [ -n "$XVFB_PID" ]; then
    echo "[TOS] Stopping Xvfb..."
    kill "$XVFB_PID" 2>/dev/null || true
fi

echo "[TOS] Shutdown complete."
