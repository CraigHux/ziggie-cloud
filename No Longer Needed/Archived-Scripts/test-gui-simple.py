#!/usr/bin/env python3
"""
Simple test to verify the launcher detects editors correctly
Runs the actual launcher code inline
"""

import os
import shutil


def find_editor_executable(editor):
    """Find the editor executable path with robust checking."""
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


print("=" * 60)
print("LAUNCHER EDITOR DETECTION TEST")
print("=" * 60)
print()

# Test VS Code
vscode = find_editor_executable("code")
print(f"VS Code: {vscode if vscode else 'NOT FOUND'}")

# Test Cursor
cursor = find_editor_executable("cursor")
print(f"Cursor: {cursor if cursor else 'NOT FOUND'}")

print()
print("=" * 60)

if vscode and cursor:
    print("RESULT: [PASS] Both editors found!")
    print("\nYou can now run the launcher GUI:")
    print("  python ziggie-launcher.py")
elif vscode or cursor:
    print("RESULT: [PARTIAL] At least one editor found")
    print("\nYou can now run the launcher GUI:")
    print("  python ziggie-launcher.py")
else:
    print("RESULT: [FAIL] No editors found")
