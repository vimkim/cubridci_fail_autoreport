# Agent Guide — cubrid-test-ai-report

This project automates extraction and analysis of failed `test_sql` test cases from CUBRID CircleCI runs.

## Project Layout

```
get_failed_tc_list_from_pr.py  # Fetch failed TC paths from a CircleCI run via GitHub PR URL
clone_failed_tc.py             # Copy failed TC files from cubrid-testcases checkout
analyze_single_tc.sh           # fzf picker + Claude analysis for a single failed TC
justfile                       # Recipes for all common tasks
failed_tc_list.txt             # Generated: list of failed TC paths (one per line)
failed_tcs/                    # Generated: local copies of failed TC files
```

## Test Case File Structure

Failed TCs are stored under `failed_tcs/sql/` with this layout:

```
failed_tcs/sql/<category>/cases/<name>.sql      # SQL input
failed_tcs/sql/<category>/cases/<name>.result   # Actual output from CI run
failed_tcs/sql/<category>/answers/<name>.answer # Expected output
```

A test fails when `.result` does not match `.answer`.

## Typical Workflow

1. **Fetch** failed TC list from a PR:
   ```sh
   just fetch pr=https://github.com/CUBRID/cubrid/pull/NNNN
   ```

2. **Clone** the TC files from a local `cubrid-testcases` checkout:
   ```sh
   just clone src=/path/to/cubrid-testcases
   ```

3. **Analyze** a single failure interactively:
   ```sh
   just analyze-single-tc
   ```
   This opens fzf to pick a `.sql` file, then diffs `.answer` vs `.result` and asks Claude to explain the failure.

## Justfile Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `pr` | `https://github.com/CUBRID/cubrid/pull/6904` | GitHub PR URL |
| `src` | `/home/vimkim/gh/tc/cubrid-testcases/` | Local cubrid-testcases root |
| `dest` | `./failed_tcs` | Output directory for cloned TCs |
| `list` | `failed_tc_list.txt` | Failed TC list file |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub personal access token (avoids rate limits) |
| `CIRCLECI_TOKEN` | CircleCI API token (needed for private projects) |

## analyze_single_tc.sh

Accepts one optional argument: the root directory to search for `.sql` files (default: `./failed_tcs`).

Steps:
1. `find <dir> -name "*.sql" | fzf` — pick a test
2. Read `<cases>/<name>.result` and `<answers>/<name>.answer`
3. Run `diff` on the two files
4. Pass SQL content + expected + actual + diff to `claude --print` for analysis
