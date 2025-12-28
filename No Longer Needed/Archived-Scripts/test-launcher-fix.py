#!/usr/bin/env python3
"""
Test script for Ziggie Launcher - Editor Detection
Tests the robust editor finder functionality
"""

import os
import shutil
import sys


def find_editor_executable(editor):
    """
    Find the editor executable path with robust checking.

    Checks in order:
    1. PATH using shutil.which()
    2. Common Windows installation locations

    Args:
        editor: Either "code" (VS Code) or "cursor"

    Returns:
        Full path to the editor executable if found, None otherwise
    """
    # First, try to find in PATH
    if editor == "code":
        path_result = shutil.which("code")
        if path_result:
            return path_result

        # Check common VS Code installation locations
        vscode_paths = [
            r"C:\Users\minin\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
        ]
        for path in vscode_paths:
            if os.path.exists(path):
                return path

    elif editor == "cursor":
        path_result = shutil.which("cursor")
        if path_result:
            return path_result

        # Check common Cursor installation locations
        cursor_paths = [
            r"C:\Program Files\cursor\Cursor.exe",
            r"C:\Program Files (x86)\cursor\Cursor.exe",
            r"C:\Users\minin\AppData\Local\Programs\cursor\Cursor.exe",
        ]
        for path in cursor_paths:
            if os.path.exists(path):
                return path

    return None


def test_editor_detection():
    """Test editor detection for both VS Code and Cursor."""
    print("=" * 60)
    print("ZIGGIE LAUNCHER - EDITOR DETECTION TEST")
    print("=" * 60)
    print()

    # Test VS Code
    print("Testing VS Code detection...")
    print("-" * 40)
    vscode_path = find_editor_executable("code")
    if vscode_path:
        print(f"[PASS] VS Code FOUND: {vscode_path}")
        print(f"   File exists: {os.path.exists(vscode_path)}")
        print(f"   File size: {os.path.getsize(vscode_path) / (1024*1024):.1f} MB")
    else:
        print("[FAIL] VS Code NOT FOUND")
    print()

    # Test Cursor
    print("Testing Cursor detection...")
    print("-" * 40)
    cursor_path = find_editor_executable("cursor")
    if cursor_path:
        print(f"[PASS] Cursor FOUND: {cursor_path}")
        print(f"   File exists: {os.path.exists(cursor_path)}")
        print(f"   File size: {os.path.getsize(cursor_path) / (1024*1024):.1f} MB")
    else:
        print("[FAIL] Cursor NOT FOUND")
    print()

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    results = []
    if vscode_path:
        results.append("VS Code [PASS]")
    else:
        results.append("VS Code [FAIL]")

    if cursor_path:
        results.append("Cursor [PASS]")
    else:
        results.append("Cursor [FAIL]")

    print("Results: " + " | ".join(results))

    if vscode_path and cursor_path:
        print("\nSUCCESS: Both editors detected correctly!")
        print("\nThe launcher should now work properly.")
        return 0
    elif vscode_path or cursor_path:
        print("\nPARTIAL: At least one editor detected.")
        print("The launcher will work for detected editors.")
        return 0
    else:
        print("\nFAILURE: No editors detected.")
        print("Please verify VS Code or Cursor installation.")
        return 1


if __name__ == "__main__":
    sys.exit(test_editor_detection())
