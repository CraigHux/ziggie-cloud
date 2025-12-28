#!/usr/bin/env python3
"""
Test script for Ziggie Launcher - Full GUI Test
Tests the launcher GUI without actually launching editors
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add the current directory to path to import the launcher
sys.path.insert(0, r"C:\Ziggie")

# Import the launcher class
from ziggie_launcher import ZiggieLauncher


def test_editor_detection():
    """Test that the launcher can detect both editors."""
    print("=" * 60)
    print("ZIGGIE LAUNCHER - GUI DETECTION TEST")
    print("=" * 60)
    print()

    # Create a hidden root window for testing
    root = tk.Tk()
    root.withdraw()  # Hide the window

    # Create launcher instance
    launcher = ZiggieLauncher(root)

    # Test VS Code detection
    print("Testing VS Code detection...")
    print("-" * 40)
    vscode_path = launcher.find_editor_executable("code")
    vscode_installed = launcher.is_editor_installed("code")
    print(f"Path: {vscode_path}")
    print(f"Installed: {vscode_installed}")
    print()

    # Test Cursor detection
    print("Testing Cursor detection...")
    print("-" * 40)
    cursor_path = launcher.find_editor_executable("cursor")
    cursor_installed = launcher.is_editor_installed("cursor")
    print(f"Path: {cursor_path}")
    print(f"Installed: {cursor_installed}")
    print()

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    if vscode_installed and cursor_installed:
        print("\n[PASS] Both editors detected successfully!")
        print("\nVS Code:")
        print(f"  Path: {vscode_path}")
        print("\nCursor:")
        print(f"  Path: {cursor_path}")
        print("\nThe launcher GUI should work without errors.")
        result = 0
    elif vscode_installed or cursor_installed:
        print("\n[PARTIAL] At least one editor detected.")
        if vscode_installed:
            print(f"  VS Code: {vscode_path}")
        if cursor_installed:
            print(f"  Cursor: {cursor_path}")
        print("\nThe launcher will work for detected editors.")
        result = 0
    else:
        print("\n[FAIL] No editors detected.")
        print("\nPlease verify VS Code or Cursor installation.")
        result = 1

    # Clean up
    root.destroy()

    return result


if __name__ == "__main__":
    try:
        sys.exit(test_editor_detection())
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
