"""
Quick system check utility
Verifies all dependencies and paths before starting the server
"""
import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  [WARN] Python 3.8 or higher is recommended")
        return False
    else:
        print("  [OK] Python version is compatible")
        return True


def check_dependencies():
    """Check if all required packages are installed."""
    required_packages = [
        "fastapi",
        "uvicorn",
        "websockets",
        "psutil",
        "sqlalchemy",
        "aiosqlite",
        "pydantic",
        "pydantic_settings",
        "dotenv"
    ]

    print("\nDependency Check:")
    all_installed = True

    for package in required_packages:
        try:
            __import__(package)
            print(f"  [OK] {package}")
        except ImportError:
            print(f"  [MISSING] {package}")
            all_installed = False

    if not all_installed:
        print("\n  Run: pip install -r requirements.txt")

    return all_installed


def check_paths():
    """Check if configured paths exist."""
    print("\nPath Check:")
    paths_to_check = {
        "ComfyUI": Path(r"C:\ComfyUI"),
        "Ziggie": Path(r"C:\Ziggie"),
        "AI Agents": Path(r"C:\Ziggie\ai-agents"),
        "Knowledge Base": Path(r"C:\Ziggie\ai-agents\knowledge-base")
    }

    all_exist = True
    for name, path in paths_to_check.items():
        if path.exists():
            print(f"  [OK] {name}: {path}")
        else:
            print(f"  [MISSING] {name}: {path}")
            all_exist = False

    return all_exist


def check_ports():
    """Check if required ports are available."""
    print("\nPort Check:")
    try:
        import psutil
        connections = psutil.net_connections(kind='inet')
        port_8080_used = any(
            conn.laddr and conn.laddr.port == 8080
            for conn in connections
        )

        if port_8080_used:
            print("  [WARN] Port 8080 is already in use")
            print("         You may need to stop other services or change the port")
            return False
        else:
            print("  [OK] Port 8080 is available")
            return True
    except Exception as e:
        print(f"  [ERROR] Could not check ports: {e}")
        return True  # Don't fail the check


def check_files():
    """Check if critical files exist."""
    print("\nCritical Files:")
    critical_files = [
        "main.py",
        "config.py",
        "requirements.txt",
        "api/system.py",
        "api/services.py",
        "api/knowledge.py",
        "services/process_manager.py",
        "services/port_scanner.py",
        "database/models.py",
        "database/db.py"
    ]

    all_exist = True
    for file in critical_files:
        path = Path(file)
        if path.exists():
            print(f"  [OK] {file}")
        else:
            print(f"  [MISSING] {file}")
            all_exist = False

    return all_exist


def main():
    """Run all checks."""
    print("=" * 70)
    print("Control Center Backend - System Check")
    print("=" * 70)
    print()

    checks = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Paths": check_paths(),
        "Ports": check_ports(),
        "Files": check_files()
    }

    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    for check_name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"{check_name}: [{status}]")

    print()

    if all(checks.values()):
        print("Result: ALL CHECKS PASSED")
        print("\nYou can start the server with: python main.py")
        return 0
    else:
        print("Result: SOME CHECKS FAILED")
        print("\nPlease fix the issues before starting the server.")
        return 1


if __name__ == "__main__":
    exit(main())
