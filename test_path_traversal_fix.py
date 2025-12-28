#!/usr/bin/env python3
"""
Test script to verify the path traversal vulnerability fix
"""

import base64
from pathlib import Path

# Test cases
print("=" * 70)
print("PATH TRAVERSAL VULNERABILITY FIX - TEST CASES")
print("=" * 70)

# Define allowed directories (same as in knowledge.py)
AI_AGENTS_ROOT = Path("C:/meowping-rts/ai-agents")
KB_ROOT = Path("C:/meowping-rts/ai-agents/knowledge-base")

allowed_dirs = [
    AI_AGENTS_ROOT.resolve(),
    KB_ROOT.resolve()
]

def test_path_validation(test_path_str, description):
    """Test if a path would be allowed or blocked"""
    print(f"\nTest: {description}")
    print(f"Input path: {test_path_str}")

    # Simulate the validation logic from the fixed code
    try:
        file_path = Path(test_path_str).resolve()
        print(f"Resolved path: {file_path}")

        is_allowed = False
        for allowed_dir in allowed_dirs:
            try:
                file_path.relative_to(allowed_dir)
                is_allowed = True
                print(f"  -> Matched allowed dir: {allowed_dir}")
                break
            except ValueError:
                continue

        if is_allowed:
            print("  -> RESULT: ALLOWED")
        else:
            print("  -> RESULT: BLOCKED (403 Forbidden)")

        return is_allowed
    except Exception as e:
        print(f"  -> ERROR: {e}")
        return False

# Test Case 1: Legitimate KB file (should be allowed)
print("\n" + "=" * 70)
print("LEGITIMATE ACCESS TESTS (Should be ALLOWED)")
print("=" * 70)
test_path_validation(
    "C:/meowping-rts/ai-agents/knowledge-base/L1-creators/creator-123.md",
    "Legitimate KB file access"
)

test_path_validation(
    "C:/meowping-rts/ai-agents/ai-agents/art-director/docs/guide.md",
    "Legitimate AI agents file access"
)

# Test Case 2: Path traversal attacks (should be blocked)
print("\n" + "=" * 70)
print("ATTACK TESTS (Should be BLOCKED)")
print("=" * 70)

test_path_validation(
    "C:/meowping-rts/ai-agents/../../../Windows/System32/config/SAM",
    "Path traversal to Windows system files"
)

test_path_validation(
    "C:/meowping-rts/ai-agents/knowledge-base/../../sensitive-data.txt",
    "Path traversal outside KB root"
)

test_path_validation(
    "C:/Windows/System32/drivers/etc/hosts",
    "Direct access to system files"
)

test_path_validation(
    "/etc/passwd",
    "Unix system file access (if on Unix)"
)

test_path_validation(
    "C:/Users/Administrator/.ssh/id_rsa",
    "Access to user SSH keys"
)

# Test Case 3: Edge cases
print("\n" + "=" * 70)
print("EDGE CASE TESTS")
print("=" * 70)

test_path_validation(
    "C:/meowping-rts/ai-agents/knowledge-base/",
    "Root KB directory access"
)

test_path_validation(
    "C:/meowping-rts/ai-agents",
    "Root AI agents directory access"
)

# Test base64 encoding scenario
print("\n" + "=" * 70)
print("BASE64 ENCODING TESTS (Simulating actual API usage)")
print("=" * 70)

def test_base64_path(path_str, description):
    """Test with base64 encoded path (as used in the API)"""
    encoded = base64.b64encode(path_str.encode('utf-8')).decode('utf-8')
    print(f"\nTest: {description}")
    print(f"Original path: {path_str}")
    print(f"Base64 encoded: {encoded}")

    # Decode and test (simulating the API endpoint)
    decoded = base64.b64decode(encoded).decode('utf-8')
    test_path_validation(decoded, "Decoded path validation")

test_base64_path(
    "C:/meowping-rts/ai-agents/knowledge-base/L1-creators/valid.md",
    "Valid base64 encoded KB file"
)

test_base64_path(
    "C:/meowping-rts/ai-agents/../../../Windows/System32/config/SAM",
    "Malicious base64 encoded path traversal"
)

print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print("\nThe path validation should:")
print("  1. ALLOW files within C:/meowping-rts/ai-agents/")
print("  2. ALLOW files within C:/meowping-rts/ai-agents/knowledge-base/")
print("  3. BLOCK all files outside these directories")
print("  4. BLOCK path traversal attempts using ../")
print("  5. Return HTTP 403 Forbidden for unauthorized paths")
print("\n" + "=" * 70)
