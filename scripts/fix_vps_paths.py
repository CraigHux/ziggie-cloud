#!/usr/bin/env python3
"""Fix VPS detection code in automated_pipeline.py"""

# Read the file
with open("/opt/ziggie/scripts/automated_pipeline.py", "r") as f:
    lines = f.readlines()

# Find and fix the collapsed line
for i, line in enumerate(lines):
    if 'Hostingerimport platform' in line:
        # This is the collapsed line - replace it with properly formatted code
        lines[i] = '''# VPS Environment Detection - Apply VPS paths if running on Hostinger
import platform
if platform.system() == "Linux" and Path("/opt/ziggie").exists():
    try:
        from vps_config import apply_vps_config
        CONFIG = apply_vps_config(CONFIG)
        print("[VPS] Running on Hostinger VPS - paths configured for /opt/ziggie")
    except ImportError:
        print("[VPS] Warning: vps_config.py not found, using default paths")

'''
        print(f"Fixed line {i+1}")
        break
else:
    print("Collapsed line not found - may already be fixed")

# Write back
with open("/opt/ziggie/scripts/automated_pipeline.py", "w") as f:
    f.writelines(lines)

print("Done!")
