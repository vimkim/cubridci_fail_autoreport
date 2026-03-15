#!/usr/bin/env python3
"""
get_failed_tc_list_from_pr.py

Usage:
    uv run get_failed_tc_list_from_pr.py <github-pr-url>

Example:
    uv run get_failed_tc_list_from_pr.py https://github.com/CUBRID/cubrid/pull/6904

Prints the list of failed test case names, one per line.

Environment variables:
    GITHUB_TOKEN    - GitHub personal access token (optional, avoids rate limits)
    CIRCLECI_TOKEN  - CircleCI personal API token (optional, for private projects)
"""

import os
import re
import sys

import requests


GITHUB_API = "https://api.github.com"
CIRCLECI_API = "https://circleci.com/api/v2"


def parse_pr_url(url: str) -> tuple[str, str, int]:
    """Parse a GitHub PR URL into (owner, repo, pr_number)."""
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", url.rstrip("/"))
    if not m:
        sys.exit(f"Error: not a valid GitHub PR URL: {url}")
    return m.group(1), m.group(2), int(m.group(3))


def github_headers() -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def circleci_headers() -> dict:
    token = os.environ.get("CIRCLECI_TOKEN")
    headers = {"Accept": "application/json"}
    if token:
        headers["Circle-Token"] = token
    return headers


def get_pr_head_sha(owner: str, repo: str, pr_number: int) -> str:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}"
    resp = requests.get(url, headers=github_headers())
    resp.raise_for_status()
    sha = resp.json()["head"]["sha"]
    print(f"[*] PR head commit: {sha}", file=sys.stderr)
    return sha


def find_circleci_test_sql_job_url(owner: str, repo: str, sha: str) -> str:
    """
    Search commit statuses for a CircleCI test_sql job and return its target URL.
    Falls back to check runs if not found in statuses.
    """
    # Try commit statuses first
    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits/{sha}/statuses"
    resp = requests.get(url, headers=github_headers(), params={"per_page": 100})
    resp.raise_for_status()
    statuses = resp.json()

    # Sort by updated_at descending to get the most recent run
    statuses.sort(key=lambda s: s.get("updated_at", ""), reverse=True)

    for status in statuses:
        context = status.get("context", "")
        target_url = status.get("target_url", "")
        if "test_sql" in context.lower() and "circleci" in target_url:
            print(f"[*] Found CircleCI status: {context} -> {target_url}", file=sys.stderr)
            return target_url

    # Try check runs
    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits/{sha}/check-runs"
    resp = requests.get(url, headers=github_headers(), params={"per_page": 100})
    resp.raise_for_status()
    check_runs = resp.json().get("check_runs", [])
    check_runs.sort(key=lambda c: c.get("completed_at") or "", reverse=True)

    for run in check_runs:
        name = run.get("name", "")
        details_url = run.get("details_url", "")
        if "test_sql" in name.lower() and "circleci" in details_url:
            print(f"[*] Found CircleCI check run: {name} -> {details_url}", file=sys.stderr)
            return details_url

    sys.exit("Error: could not find a CircleCI test_sql job for this PR.")


def extract_job_number(circleci_url: str) -> tuple[str, int]:
    """
    Extract (project_slug, job_number) from a CircleCI URL.

    Handles:
      https://circleci.com/gh/CUBRID/cubrid/118648
      https://app.circleci.com/pipelines/github/CUBRID/cubrid/26895/workflows/.../jobs/118648
    """
    # app.circleci.com/pipelines/github/ORG/REPO/.../jobs/JOB_NUM
    m = re.search(r"pipelines/(github|bitbucket|gitlab)/([^/]+)/([^/]+)/.*?/jobs/(\d+)", circleci_url)
    if m:
        vcs, org, repo, job_num = m.group(1), m.group(2), m.group(3), m.group(4)
        return f"{vcs}/{org}/{repo}", int(job_num)

    # circleci.com/gh/ORG/REPO/JOB_NUM
    m = re.search(r"circleci\.com/gh/([^/]+)/([^/]+)/(\d+)", circleci_url)
    if m:
        org, repo, job_num = m.group(1), m.group(2), m.group(3)
        return f"github/{org}/{repo}", int(job_num)

    sys.exit(f"Error: could not parse CircleCI job URL: {circleci_url}")


def get_failed_tests(project_slug: str, job_number: int) -> list[str]:
    """Call CircleCI API v2 to retrieve test metadata and return failed test names."""
    url = f"{CIRCLECI_API}/project/{project_slug}/{job_number}/tests"
    print(f"[*] Fetching test results from: {url}", file=sys.stderr)

    failed = []
    params = {}

    while True:
        resp = requests.get(url, headers=circleci_headers(), params=params)
        resp.raise_for_status()
        data = resp.json()

        for test in data.get("items", []):
            if test.get("result") in ("failure", "error"):
                # Prefer 'file' field; fall back to classname + name
                name = test.get("file") or test.get("name") or ""
                classname = test.get("classname", "")
                if not name and classname:
                    name = classname
                elif classname and name and not name.startswith(classname):
                    name = f"{classname}/{name}"
                if name:
                    failed.append(name)

        next_token = data.get("next_page_token")
        if not next_token:
            break
        params["page-token"] = next_token

    return failed


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    pr_url = sys.argv[1]
    owner, repo, pr_number = parse_pr_url(pr_url)
    print(f"[*] PR: {owner}/{repo}#{pr_number}", file=sys.stderr)

    sha = get_pr_head_sha(owner, repo, pr_number)
    job_url = find_circleci_test_sql_job_url(owner, repo, sha)
    project_slug, job_number = extract_job_number(job_url)
    print(f"[*] CircleCI project: {project_slug}, job: {job_number}", file=sys.stderr)

    failed = get_failed_tests(project_slug, job_number)

    if not failed:
        print("[*] No failed test cases found.", file=sys.stderr)
    else:
        print(f"[*] {len(failed)} failed test case(s):", file=sys.stderr)
        for tc in failed:
            print(tc)


if __name__ == "__main__":
    main()
