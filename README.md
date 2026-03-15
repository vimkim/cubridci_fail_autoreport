# test-sql-autoreport

Toolchain for extracting and collecting failed `test_sql` test cases from a CUBRID CircleCI run, given a GitHub PR URL.

## Requirements

- [uv](https://docs.astral.sh/uv/)
- [just](https://github.com/casey/just)
- GitHub token (optional, avoids API rate limits): `GITHUB_TOKEN`
- CircleCI token (optional, for private projects): `CIRCLECI_TOKEN`

## Quick Start

```sh
# 1. Fetch failed TC list from a PR
just fetch pr=https://github.com/CUBRID/cubrid/pull/6904

# 2. Clone the failed TCs from your local cubrid-testcases checkout
just clone src=/path/to/cubrid-testcases

# Or run both steps at once
just run-fetch-clone pr=https://github.com/CUBRID/cubrid/pull/6904 src=/path/to/cubrid-testcases

# 3. Select a failed TC with fzf and analyze it with Claude
just analyze-single-tc
```

## Tools

### `get_failed_tc_list_from_pr.py`

Fetches the list of failed test cases from a PR's latest CircleCI `test_sql` job.

```sh
uv run get_failed_tc_list_from_pr.py <github-pr-url>
```

**Flow:**
1. Resolves the PR's head commit via GitHub API
2. Finds the CircleCI `test_sql` job from commit statuses / check-runs
3. Calls the CircleCI API v2 test metadata endpoint
4. Prints failed test case paths to stdout (one per line)

**Output format:**
```
linux_sql_64bit_release/cubrid-testcases/sql/_01_object/_02_class/_003_auto_increment/cases/1002.sql
linux_sql_64bit_release/cubrid-testcases/sql/_01_object/_02_class/_003_auto_increment/cases/1005.sql
...
```

### `clone_failed_tc.py`

Copies the failed test case files from a source directory to a destination directory, preserving the relative path structure.

```sh
uv run clone_failed_tc.py -l failed_tc_list.txt -s <source_dir> -d <dest_dir>
```

| Flag | Description |
|------|-------------|
| `-l` | Path to the failed TC list file |
| `-s` | Source root directory (your `cubrid-testcases` checkout) |
| `-d` | Destination directory (default: `./failed_tcs`) |

## Justfile Recipes

| Recipe | Description |
|--------|-------------|
| `just fetch [pr=<url>]` | Fetch failed TC list → `failed_tc_list.txt` |
| `just clone [src=<dir>]` | Copy TCs from source dir → `./failed_tcs` |
| `just run-fetch-clone [pr=<url>] [src=<dir>]` | Full pipeline (fetch + clone) |
| `just clean` | Remove `failed_tc_list.txt` and `./failed_tcs` |
| `just analyze-single-tc [dest=<dir>]` | Select a TC with fzf and analyze with Claude |
| `just run-ctp-sql` | Run CTP SQL suite with `example-sql.conf` |

Default variable values can be overridden on the command line:

```sh
just run-fetch-clone pr=https://github.com/CUBRID/cubrid/pull/6904 \
                     src=/path/to/cubrid-testcases \
                     dest=./my_output \
                     list=my_list.txt
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub personal access token |
| `CIRCLECI_TOKEN` | CircleCI personal API token |
