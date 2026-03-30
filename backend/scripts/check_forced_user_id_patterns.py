#!/usr/bin/env python3
"""Fail CI on forced/hardcoded user_id patterns outside test fixtures."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

CHECK_GLOBS = ("**/*.py",)
EXCLUDED_SUBSTRINGS = (
    "/.git/",
    "/.venv/",
    "/venv/",
    "/node_modules/",
    "/__pycache__/",
    "/tests/",
    "/test_",
    "/fixtures/",
    "/test_validation/",
    "/backend/scripts/check_forced_user_id_patterns.py",
)

RULES = [
    (re.compile(r"\buser_id\s*=\s*1\b"), "hardcoded `user_id = 1`"),
    (re.compile(r"force\s+user_id", re.IGNORECASE), "`force user_id` marker"),
]


def is_excluded(path: Path) -> bool:
    normalized = f"/{path.as_posix()}"
    return any(part in normalized for part in EXCLUDED_SUBSTRINGS)


def iter_candidate_files() -> list[Path]:
    files: set[Path] = set()
    for glob in CHECK_GLOBS:
        files.update(REPO_ROOT.glob(glob))
    return sorted(p for p in files if p.is_file() and not is_excluded(p.relative_to(REPO_ROOT)))


def main() -> int:
    violations: list[tuple[Path, int, str, str]] = []

    for file_path in iter_candidate_files():
        rel_path = file_path.relative_to(REPO_ROOT)
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            for pattern, label in RULES:
                if pattern.search(line):
                    violations.append((rel_path, line_number, label, line.strip()))

    if not violations:
        print("✅ No forced/hardcoded user_id patterns found outside test fixtures.")
        return 0

    print("❌ Found forbidden forced/hardcoded user_id patterns:")
    for path, line, label, source_line in violations:
        print(f" - {path}:{line} [{label}] -> {source_line}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
