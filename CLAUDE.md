# test-sql-autoreport

Toolchain for generating automated analysis reports of failed `test_sql` CircleCI test cases from a CUBRID GitHub PR.

## Project Goal

Given a GitHub PR URL for `github.com/CUBRID/cubrid`, automatically:
1. Find the most recent CircleCI `test_sql` job for that PR
2. Extract the list of failed test cases
3. Copy those test case files to a local directory for analysis

## Tools

### `get_failed_tc_list_from_pr.py`

Fetches the list of failed test cases from a PR's latest CircleCI `test_sql` run.

```
uv run get_failed_tc_list_from_pr.py https://github.com/CUBRID/cubrid/pull/6904
```

**Flow:**
1. Take a GitHub PR URL
2. Find the most recently run CircleCI `test_sql` job linked to that PR
3. Navigate to the CircleCI job's `/tests` endpoint (e.g. `https://app.circleci.com/pipelines/github/CUBRID/cubrid/<pipeline>/workflows/<workflow>/jobs/<job>/tests`)
4. Collect and output the list of failed test cases

### `clone_failed_tc.py`

Copies only the failed test case files from a source directory to a destination directory.

```
uv run clone_failed_tc.py -l failed_tc_list.txt -s <source_tc_directory> -d <destination_directory>
```

**Arguments:**
- `-l` — path to file containing failed TC list (output of `get_failed_tc_list_from_pr.py`)
- `-s` — source directory containing all test cases
- `-d` — destination directory to copy failed TCs into

## Development

This project uses `uv` for dependency management.

```
uv run <script.py>
```
