#!/usr/bin/env python3
"""
clone_failed_tc.py

Copies failed test case files from a source directory to a destination directory.

Usage:
    uv run clone_failed_tc.py -l failed_tc_list.txt -s <source_dir> -d <dest_dir>

Arguments:
    -l, --list      Path to file containing failed TC names, one per line
                    (output of get_failed_tc_list_from_pr.py)
    -s, --source    Root directory containing all test cases
    -d, --dest      Destination directory to copy failed TCs into

The script searches for each TC name under the source directory.
It preserves the relative directory structure under the destination.
"""

import argparse
import shutil
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy failed test cases from source to destination directory."
    )
    parser.add_argument("-l", "--list", required=True, help="File with failed TC names (one per line)")
    parser.add_argument("-s", "--source", required=True, help="Source root directory of test cases")
    parser.add_argument("-d", "--dest", required=True, help="Destination directory")
    return parser.parse_args()


def read_tc_list(list_path: Path) -> list[str]:
    lines = list_path.read_text().splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def find_tc_file(tc_name: str, source_root: Path) -> Path | None:
    """
    Resolve a TC name to a file under source_root.

    Tries in order:
      1. Exact relative path match: source_root / tc_name
      2. Recursive search for a file whose name matches the basename of tc_name
    """
    # 1. Treat tc_name as a relative path
    candidate = source_root / tc_name
    if candidate.is_file():
        return candidate

    # Strip leading slashes and try again
    tc_name_stripped = tc_name.lstrip("/")
    candidate = source_root / tc_name_stripped
    if candidate.is_file():
        return candidate

    # 2. Search recursively by basename
    basename = Path(tc_name).name
    matches = list(source_root.rglob(basename))
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        # Prefer the match whose path contains the most path components from tc_name
        tc_parts = Path(tc_name_stripped).parts
        def score(p: Path) -> int:
            p_parts = p.parts
            return sum(1 for part in tc_parts if part in p_parts)
        matches.sort(key=score, reverse=True)
        return matches[0]

    return None


def copy_tc(tc_file: Path, source_root: Path, dest_root: Path) -> None:
    relative = tc_file.relative_to(source_root)
    dest_file = dest_root / relative
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(tc_file, dest_file)


def main():
    args = parse_args()

    list_path = Path(args.list)
    source_root = Path(args.source)
    dest_root = Path(args.dest)

    if not list_path.is_file():
        sys.exit(f"Error: list file not found: {list_path}")
    if not source_root.is_dir():
        sys.exit(f"Error: source directory not found: {source_root}")

    dest_root.mkdir(parents=True, exist_ok=True)

    tc_names = read_tc_list(list_path)
    if not tc_names:
        print("No test cases in list. Nothing to do.")
        return

    print(f"Copying {len(tc_names)} test case(s) from '{source_root}' to '{dest_root}'...")

    copied = 0
    not_found = []

    for tc_name in tc_names:
        tc_file = find_tc_file(tc_name, source_root)
        if tc_file is None:
            print(f"  [NOT FOUND] {tc_name}")
            not_found.append(tc_name)
        else:
            copy_tc(tc_file, source_root, dest_root)
            print(f"  [OK] {tc_file.relative_to(source_root)}")
            copied += 1

    print(f"\nDone: {copied} copied, {len(not_found)} not found.")
    if not_found:
        print("Not found:")
        for name in not_found:
            print(f"  {name}")


if __name__ == "__main__":
    main()
