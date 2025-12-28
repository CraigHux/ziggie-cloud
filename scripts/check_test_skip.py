#!/usr/bin/env python3
"""
Pre-commit hook to detect test.skip() violations.

This script enforces Know Thyself Principle #2 from CLAUDE.md:
"NO test.skip() in codebase - Zero `test.skip()` in codebase = Sprint FAILURE"

Patterns detected:
- test.skip()
- test.todo()
- it.skip() / describe.skip()
- xit() / xdescribe()
- @pytest.mark.skip
- @unittest.skip
- pytest.skip()

Exit codes:
- 0: No violations found
- 1: Violations found (commit blocked)
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# Patterns that indicate skipped tests (PROHIBITED per CLAUDE.md)
SKIP_PATTERNS = [
    # JavaScript/TypeScript patterns
    (r'\btest\.skip\s*\(', 'test.skip()'),
    (r'\btest\.todo\s*\(', 'test.todo()'),
    (r'\bit\.skip\s*\(', 'it.skip()'),
    (r'\bdescribe\.skip\s*\(', 'describe.skip()'),
    (r'\bxit\s*\(', 'xit()'),
    (r'\bxdescribe\s*\(', 'xdescribe()'),
    (r'\bxtest\s*\(', 'xtest()'),
    (r'\btest\.only\s*\(', 'test.only() - focused test'),
    (r'\bit\.only\s*\(', 'it.only() - focused test'),
    (r'\bdescribe\.only\s*\(', 'describe.only() - focused test'),

    # Python pytest patterns
    (r'@pytest\.mark\.skip\b', '@pytest.mark.skip'),
    (r'@pytest\.mark\.skipif\b', '@pytest.mark.skipif'),
    (r'\bpytest\.skip\s*\(', 'pytest.skip()'),
    (r'@unittest\.skip\b', '@unittest.skip'),
    (r'@unittest\.skipIf\b', '@unittest.skipIf'),
    (r'@unittest\.skipUnless\b', '@unittest.skipUnless'),

    # Commented out tests (less strict but flagged)
    # (r'^\s*#\s*(def test_|test\()', 'Commented out test'),
]

# Allowed patterns (false positive prevention)
ALLOWED_PATTERNS = [
    r'check_test_skip',  # This script itself
    r'\.skip\s*=',       # Assignment, not function call
    r'skipif.*condition',# Legitimate conditional skips with reason
]


def check_file(filepath: str) -> List[Tuple[int, str, str]]:
    """
    Check a file for test.skip() violations.

    Args:
        filepath: Path to the file to check

    Returns:
        List of (line_number, line_content, violation_type) tuples
    """
    violations = []
    path = Path(filepath)

    if not path.exists():
        return violations

    try:
        content = path.read_text(encoding='utf-8')
    except (UnicodeDecodeError, PermissionError):
        return violations

    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        # Skip empty lines
        if not line.strip():
            continue

        # Check if line matches any allowed pattern
        is_allowed = any(re.search(pattern, line) for pattern in ALLOWED_PATTERNS)
        if is_allowed:
            continue

        # Check for violations
        for pattern, violation_name in SKIP_PATTERNS:
            if re.search(pattern, line):
                violations.append((line_num, line.strip(), violation_name))
                break  # Only report first violation per line

    return violations


def main() -> int:
    """
    Main entry point for the pre-commit hook.

    Returns:
        Exit code (0 = success, 1 = violations found)
    """
    if len(sys.argv) < 2:
        print("Usage: check_test_skip.py <file1> [file2] ...")
        return 0

    files = sys.argv[1:]
    all_violations = []

    for filepath in files:
        violations = check_file(filepath)
        if violations:
            all_violations.append((filepath, violations))

    if not all_violations:
        return 0

    # Report violations
    print("\n" + "=" * 70)
    print("KNOW THYSELF PRINCIPLE #2 VIOLATION: test.skip() detected!")
    print("=" * 70)
    print("\nPer CLAUDE.md: 'NO test.skip() in codebase = Sprint FAILURE'")
    print("\nViolations found:\n")

    total_violations = 0
    for filepath, violations in all_violations:
        print(f"\n  File: {filepath}")
        for line_num, line_content, violation_type in violations:
            total_violations += 1
            print(f"    Line {line_num}: [{violation_type}]")
            print(f"      {line_content[:80]}{'...' if len(line_content) > 80 else ''}")

    print("\n" + "-" * 70)
    print(f"Total violations: {total_violations}")
    print("\nREMEDIATION:")
    print("  1. IMPLEMENT the feature to make tests pass")
    print("  2. Or REMOVE the test if no longer applicable")
    print("  3. NEVER skip tests to make the build pass")
    print("-" * 70 + "\n")

    return 1


if __name__ == '__main__':
    sys.exit(main())
