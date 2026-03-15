#!/usr/bin/env bash
# analyze_tc.sh — select a failed SQL test with fzf, compare result/answer, analyze with claude

set -euo pipefail

FAILED_TCS_DIR="${1:-./failed_tcs}"

# 1. Select a .sql file via fzf
SQL_FILE=$(find "$FAILED_TCS_DIR" -name "*.sql" | sort | fzf --prompt="Select test case: " --preview="cat {}")

if [[ -z "$SQL_FILE" ]]; then
    echo "No file selected. Exiting."
    exit 1
fi

echo "Selected: $SQL_FILE"
echo

# 2. Derive paths for answer and result files
CASES_DIR=$(dirname "$SQL_FILE")
TC_NAME=$(basename "$SQL_FILE" .sql)
ANSWERS_DIR="${CASES_DIR%/cases}/answers"
ANSWER_FILE="$ANSWERS_DIR/${TC_NAME}.answer"
RESULT_FILE="$CASES_DIR/${TC_NAME}.result"

# 3. Read answer and result files
if [[ ! -f "$ANSWER_FILE" ]]; then
    echo "Error: answer file not found: $ANSWER_FILE"
    exit 1
fi

if [[ ! -f "$RESULT_FILE" ]]; then
    echo "Error: result file not found: $RESULT_FILE"
    exit 1
fi

EXPECTED_OUTPUT=$(cat "$ANSWER_FILE")
ACTUAL_OUTPUT=$(cat "$RESULT_FILE")
SQL_CONTENT=$(cat "$SQL_FILE")
DIFF_OUTPUT=$(diff "$ANSWER_FILE" "$RESULT_FILE" || true)

echo "=== Diff (answer vs result) ==="
echo "$DIFF_OUTPUT"
echo

# 4. Ask claude to analyze
PROMPT=$(cat <<EOF
A CUBRID SQL test case failed. Please analyze why.

## Test file: $SQL_FILE

## SQL content:
\`\`\`sql
$SQL_CONTENT
\`\`\`

## Expected output (.answer file):
\`\`\`
$EXPECTED_OUTPUT
\`\`\`

## Actual output (.result file):
\`\`\`
$ACTUAL_OUTPUT
\`\`\`

## Diff (expected vs actual):
\`\`\`diff
$DIFF_OUTPUT
\`\`\`

Please explain:
1. What the test is trying to verify
2. What went wrong (compare expected vs actual output)
3. The likely root cause of the failure
EOF
)

echo "=== Claude Analysis ==="
echo "$PROMPT" | claude --print
