Build a Python toolchain for extracting failed `test_sql` test cases from a CUBRID CircleCI run, given a GitHub PR URL.

## Tools to implement

### `get_failed_tc_list_from_pr.py`

```
uv run get_failed_tc_list_from_pr.py https://github.com/CUBRID/cubrid/pull/6904
```

**Steps:**
1. Parse the PR URL to extract owner, repo, and PR number.
2. Call the GitHub API to get the PR's head commit SHA.
3. Search the commit's statuses and check-runs for a CircleCI job whose name contains `test_sql`. Pick the most recent one.
4. Extract the CircleCI job number from the status target URL.
   - Short form: `https://circleci.com/gh/CUBRID/cubrid/118648`
   - Long form: `https://app.circleci.com/pipelines/github/CUBRID/cubrid/26895/workflows/<uuid>/jobs/118648`
5. Call the CircleCI API v2 test metadata endpoint:
   `GET https://circleci.com/api/v2/project/github/CUBRID/cubrid/118648/tests`
   Handle pagination via `next_page_token`.
6. Filter for tests where `result` is `failure` or `error`.
7. Print the `file` field of each failed test to stdout, one per line.

**Output format:**
```
linux_sql_64bit_release/cubrid-testcases/sql/_01_object/_02_class/_003_auto_increment/cases/1002.sql
linux_sql_64bit_release/cubrid-testcases/sql/_01_object/_02_class/_003_auto_increment/cases/1005.sql
```

**Auth (via environment variables):**
- `GITHUB_TOKEN` — optional, avoids GitHub rate limits
- `CIRCLECI_TOKEN` — optional, needed for private projects

---

### `clone_failed_tc.py`

```
uv run clone_failed_tc.py -l failed_tc_list.txt -s <source_dir> -d <dest_dir>
```

**Steps:**
1. Read TC paths from the list file (one per line, ignore blank lines and `#` comments).
2. For each TC path, locate the file under the source directory:
   - Try it as a relative path directly.
   - Fall back to a recursive basename search; if multiple matches, score by path component overlap.
3. Copy found files to the destination, preserving relative directory structure.
4. Report not-found entries after all copies.

---

## Justfile

Provide a `justfile` with these recipes:

- `just fetch [pr=<url>]` — run `get_failed_tc_list_from_pr.py`, save output to `failed_tc_list.txt`
- `just clone [src=<dir>]` — run `clone_failed_tc.py` using `failed_tc_list.txt`
- `just run [pr=<url>] [src=<dir>]` — fetch then clone in one step
- `just clean` — delete `failed_tc_list.txt` and the output directory

Default variable values: `list=failed_tc_list.txt`, `dest=./failed_tcs`.

---

## Project setup

- Use `uv` for dependency management (`pyproject.toml`).
- Only external dependency needed: `requests`.
