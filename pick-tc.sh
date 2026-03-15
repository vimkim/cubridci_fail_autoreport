#!/usr/bin/env bash
# Run this in any terminal to pick a test case for Claude to analyze.
# Selection is written to /tmp/tc_pick so Claude can read it.

FAILED_TCS_DIR="${1:-./failed_tcs}"

find "$FAILED_TCS_DIR" -name "*.sql" | sort | fzf \
    --prompt="Select test case: " \
    --preview="cat {}" \
    > /tmp/tc_pick

if [[ -s /tmp/tc_pick ]]; then
    echo "Selected: $(cat /tmp/tc_pick)"
    echo "Now trigger /analyze-tc in Claude Code."
else
    echo "No selection made."
fi
