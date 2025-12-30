#!/usr/bin/env python3
"""
Health Check Script for Ziggie 24/7 Pipeline
============================================
Monitors all pipeline components and reports status.
Designed to run on both local machine and VPS.

Usage:
  python health_check.py          # Check all components
  python health_check.py --json   # Output as JSON
  python health_check.py --alert  # Send Discord alert if issues found
"""

import os
import sys
import json
import subprocess
import platform
import shutil
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Detect environment
IS_VPS = platform.system() == "Linux" and Path("/opt/ziggie").exists()
IS_WINDOWS = platform.system() == "Windows"

# Configuration based on environment
if IS_VPS:
    BLENDER_PATH = "/usr/bin/blender"
    SCRIPTS_DIR = "/opt/ziggie/scripts"
    ASSETS_DIR = "/opt/ziggie/assets"
    LOGS_DIR = "/opt/ziggie/logs"
    VENV_PYTHON = "/opt/ziggie/pipeline/venv/bin/python"
else:
    BLENDER_PATH = "C:/Program Files/Blender Foundation/Blender 5.0/blender.exe"
    SCRIPTS_DIR = "C:/Ziggie/scripts"
    ASSETS_DIR = "C:/Ziggie/assets/test-results"
    LOGS_DIR = "C:/Ziggie/logs"
    VENV_PYTHON = sys.executable


def check_python_packages() -> Dict[str, bool]:
    """Check if required Python packages are installed."""
    required = ["PIL", "discord", "requests", "aiohttp", "gradio_client"]
    results = {}

    for pkg in required:
        try:
            if pkg == "PIL":
                import PIL
                results["pillow"] = True
            elif pkg == "discord":
                import discord
                results["discord.py"] = True
            else:
                __import__(pkg.replace("-", "_"))
                results[pkg] = True
        except ImportError:
            results[pkg] = False

    return results


def check_blender() -> Dict[str, any]:
    """Check if Blender is installed and accessible."""
    result = {"installed": False, "version": None, "path": BLENDER_PATH}

    try:
        if IS_WINDOWS:
            if os.path.exists(BLENDER_PATH):
                output = subprocess.run(
                    [BLENDER_PATH, "--version"],
                    capture_output=True, text=True, timeout=10
                )
                result["installed"] = True
                result["version"] = output.stdout.split("\n")[0] if output.stdout else "Unknown"
        else:
            output = subprocess.run(
                ["which", "blender"],
                capture_output=True, text=True
            )
            if output.returncode == 0:
                result["installed"] = True
                result["path"] = output.stdout.strip()

                version_output = subprocess.run(
                    ["blender", "--version"],
                    capture_output=True, text=True, timeout=10
                )
                result["version"] = version_output.stdout.split("\n")[0] if version_output.stdout else "Unknown"
    except Exception as e:
        result["error"] = str(e)

    return result


def check_disk_space() -> Dict[str, any]:
    """Check available disk space."""
    target_path = ASSETS_DIR if os.path.exists(ASSETS_DIR) else "/"

    try:
        total, used, free = shutil.disk_usage(target_path)
        return {
            "path": target_path,
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "free_percent": round((free / total) * 100, 1),
            "healthy": free > (5 * 1024**3)  # At least 5GB free
        }
    except Exception as e:
        return {"error": str(e), "healthy": False}


def check_discord_bot_service() -> Dict[str, any]:
    """Check if Discord bot systemd service is running (VPS only)."""
    if not IS_VPS:
        return {"available": False, "reason": "Not on VPS"}

    try:
        result = subprocess.run(
            ["systemctl", "is-active", "ziggie-discord-bot"],
            capture_output=True, text=True
        )
        status = result.stdout.strip()
        return {
            "available": True,
            "status": status,
            "healthy": status == "active"
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


def check_n8n() -> Dict[str, any]:
    """Check if n8n is responding."""
    urls = [
        "http://localhost:5678/healthz",
        "http://127.0.0.1:5678/healthz",
    ]

    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return {"healthy": True, "url": url, "status_code": 200}
        except:
            continue

    return {"healthy": False, "error": "n8n not responding"}


def check_api_keys() -> Dict[str, bool]:
    """Check if required API keys are set."""
    from dotenv import load_dotenv

    # Try to load .env file
    env_paths = [
        "/opt/ziggie/configs/.env",
        "C:/Ziggie/.secrets/.env.local",
        ".env",
    ]

    for path in env_paths:
        if os.path.exists(path):
            load_dotenv(path)
            break

    keys = {
        "RUNPOD_API_KEY": os.getenv("RUNPOD_API_KEY"),
        "MESHY_API_KEY": os.getenv("MESHY_API_KEY"),
        "DISCORD_BOT_TOKEN": os.getenv("DISCORD_BOT_TOKEN"),
        "DISCORD_WEBHOOK_URL": os.getenv("DISCORD_WEBHOOK_URL"),
    }

    return {k: bool(v and v != "CHANGE_ME") for k, v in keys.items()}


def check_cloud_apis() -> Dict[str, any]:
    """Test connectivity to cloud APIs (without consuming credits)."""
    results = {}

    # RunPod health check
    try:
        response = requests.get("https://api.runpod.io/v2/", timeout=5)
        results["runpod"] = {"reachable": True, "status_code": response.status_code}
    except Exception as e:
        results["runpod"] = {"reachable": False, "error": str(e)}

    # HuggingFace
    try:
        response = requests.get("https://huggingface.co/api/", timeout=5)
        results["huggingface"] = {"reachable": True, "status_code": response.status_code}
    except Exception as e:
        results["huggingface"] = {"reachable": False, "error": str(e)}

    # Meshy.ai
    try:
        response = requests.get("https://api.meshy.ai/", timeout=5)
        results["meshy"] = {"reachable": True, "status_code": response.status_code}
    except Exception as e:
        results["meshy"] = {"reachable": False, "error": str(e)}

    return results


def check_scripts() -> Dict[str, bool]:
    """Check if required pipeline scripts exist."""
    required_scripts = [
        "automated_pipeline.py",
        "discord_bot.py",
        "blender_8dir_render.py",
        "blender_thumbnail.py",
    ]

    return {
        script: os.path.exists(os.path.join(SCRIPTS_DIR, script))
        for script in required_scripts
    }


def run_full_health_check() -> Dict[str, any]:
    """Run all health checks and return comprehensive report."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "environment": "VPS" if IS_VPS else "Local (Windows)" if IS_WINDOWS else "Local (Other)",
        "checks": {}
    }

    print("Running health checks...")

    # Python packages
    print("  Checking Python packages...")
    report["checks"]["python_packages"] = check_python_packages()

    # Blender
    print("  Checking Blender...")
    report["checks"]["blender"] = check_blender()

    # Disk space
    print("  Checking disk space...")
    report["checks"]["disk_space"] = check_disk_space()

    # Discord bot service (VPS only)
    print("  Checking Discord bot service...")
    report["checks"]["discord_bot_service"] = check_discord_bot_service()

    # n8n
    print("  Checking n8n...")
    report["checks"]["n8n"] = check_n8n()

    # API keys
    print("  Checking API keys...")
    report["checks"]["api_keys"] = check_api_keys()

    # Cloud APIs
    print("  Checking cloud API connectivity...")
    report["checks"]["cloud_apis"] = check_cloud_apis()

    # Scripts
    print("  Checking scripts...")
    report["checks"]["scripts"] = check_scripts()

    # Calculate overall health
    critical_checks = [
        report["checks"]["disk_space"].get("healthy", False),
        all(report["checks"]["api_keys"].values()),
        report["checks"]["blender"].get("installed", False),
    ]

    if IS_VPS:
        critical_checks.append(report["checks"]["discord_bot_service"].get("healthy", False))

    report["overall_healthy"] = all(critical_checks)

    return report


def print_report(report: Dict[str, any]):
    """Print human-readable report."""
    print(f"\n{'='*60}")
    print(f"  ZIGGIE PIPELINE HEALTH CHECK")
    print(f"  {report['timestamp']}")
    print(f"  Environment: {report['environment']}")
    print(f"{'='*60}\n")

    # Python packages
    print("Python Packages:")
    for pkg, ok in report["checks"]["python_packages"].items():
        icon = "✅" if ok else "❌"
        print(f"  {icon} {pkg}")

    # Blender
    blender = report["checks"]["blender"]
    icon = "✅" if blender.get("installed") else "❌"
    print(f"\nBlender: {icon}")
    if blender.get("installed"):
        print(f"  Version: {blender.get('version', 'Unknown')}")
        print(f"  Path: {blender.get('path', 'Unknown')}")

    # Disk space
    disk = report["checks"]["disk_space"]
    icon = "✅" if disk.get("healthy") else "❌"
    print(f"\nDisk Space: {icon}")
    print(f"  Free: {disk.get('free_gb', 0):.1f} GB ({disk.get('free_percent', 0):.0f}%)")

    # Discord bot service
    dbs = report["checks"]["discord_bot_service"]
    if dbs.get("available"):
        icon = "✅" if dbs.get("healthy") else "❌"
        print(f"\nDiscord Bot Service: {icon} ({dbs.get('status', 'unknown')})")

    # n8n
    n8n = report["checks"]["n8n"]
    icon = "✅" if n8n.get("healthy") else "❌"
    print(f"\nn8n: {icon}")

    # API keys
    print("\nAPI Keys:")
    for key, ok in report["checks"]["api_keys"].items():
        icon = "✅" if ok else "❌"
        print(f"  {icon} {key}")

    # Cloud APIs
    print("\nCloud API Connectivity:")
    for api, status in report["checks"]["cloud_apis"].items():
        icon = "✅" if status.get("reachable") else "❌"
        print(f"  {icon} {api}")

    # Scripts
    print("\nPipeline Scripts:")
    for script, exists in report["checks"]["scripts"].items():
        icon = "✅" if exists else "❌"
        print(f"  {icon} {script}")

    # Overall
    print(f"\n{'='*60}")
    overall = "✅ ALL SYSTEMS GO" if report["overall_healthy"] else "❌ ISSUES DETECTED"
    print(f"  {overall}")
    print(f"{'='*60}\n")


def send_discord_alert(report: Dict[str, any]):
    """Send alert to Discord if issues detected."""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("Warning: DISCORD_WEBHOOK_URL not set, cannot send alert")
        return

    # Build message
    issues = []

    if not report["checks"]["disk_space"].get("healthy"):
        issues.append(f"⚠️ Low disk space: {report['checks']['disk_space'].get('free_gb', 0):.1f} GB free")

    if not report["checks"]["blender"].get("installed"):
        issues.append("❌ Blender not installed")

    if IS_VPS and not report["checks"]["discord_bot_service"].get("healthy"):
        issues.append("❌ Discord bot service not running")

    for key, ok in report["checks"]["api_keys"].items():
        if not ok:
            issues.append(f"❌ Missing API key: {key}")

    if not issues:
        return  # No issues to report

    message = {
        "content": f"🚨 **Ziggie Health Alert** ({report['environment']})\n\n" + "\n".join(issues)
    }

    try:
        requests.post(webhook_url, json=message, timeout=10)
        print("Alert sent to Discord")
    except Exception as e:
        print(f"Failed to send Discord alert: {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Ziggie Pipeline Health Check")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--alert", action="store_true", help="Send Discord alert if issues found")
    args = parser.parse_args()

    report = run_full_health_check()

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    if args.alert and not report["overall_healthy"]:
        send_discord_alert(report)

    return 0 if report["overall_healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
