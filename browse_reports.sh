#!/usr/bin/env bash
# browse_reports.sh — interactively search and open failure reports with fzf

set -euo pipefail

REPORTS_DIR="${1:-./reports}"

if [[ ! -d "$REPORTS_DIR" ]]; then
    echo "No reports directory found: $REPORTS_DIR"
    echo "Run analyze_single_tc.sh first to generate reports."
    exit 1
fi

EDITOR="${EDITOR:-vi}"

REPORT=$(find "$REPORTS_DIR" -name "*.md" | sort | fzf \
    --prompt="Select report: " \
    --preview="cat {}" \
    --preview-window="right:60%:wrap")

if [[ -z "$REPORT" ]]; then
    echo "No report selected. Exiting."
    exit 0
fi

"$EDITOR" "$REPORT"
