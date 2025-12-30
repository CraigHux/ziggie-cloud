#!/usr/bin/env python3
"""
CSV Pipeline Runner - Automated Asset Generation from Tracking Spreadsheet

This script reads from MEOW_PING_NFT_ASSET_TRACKING.csv and triggers
Stage 1-7 pipeline for each asset with PENDING status.

Usage:
    python csv_pipeline_runner.py --category Hero --limit 5
    python csv_pipeline_runner.py --priority P0 --dry-run
    python csv_pipeline_runner.py --biome Desert_Wastes

Environment Variables Required:
    RUNPOD_API_KEY      - For Stage 1 (2D Generation)
    MESHY_API_KEY       - For Stage 4 (2D to 3D)
    DISCORD_BOT_TOKEN   - For approval gates
    DISCORD_APPROVAL_CHANNEL_ID
"""

import csv
import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# CSV file location
CSV_PATH = Path(__file__).parent.parent / "assets" / "MEOW_PING_NFT_ASSET_TRACKING.csv"

# Output directories
OUTPUT_BASE = Path(__file__).parent.parent / "assets" / "pipeline_outputs"


def load_csv_assets(csv_path: Path) -> List[Dict]:
    """Load all assets from the tracking CSV."""
    assets = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            assets.append(row)
    print(f"[CSV] Loaded {len(assets)} assets from {csv_path.name}")
    return assets


def filter_assets(
    assets: List[Dict],
    category: Optional[str] = None,
    faction: Optional[str] = None,
    biome: Optional[str] = None,
    priority: Optional[str] = None,
    status: str = "PENDING",
    limit: Optional[int] = None
) -> List[Dict]:
    """Filter assets based on criteria."""
    filtered = []

    for asset in assets:
        # Check Stage1_Status for PENDING
        if status and asset.get('Stage1_Status', '').upper() != status.upper():
            continue

        if category and asset.get('Category', '').lower() != category.lower():
            continue

        if faction and asset.get('Faction', '').lower() != faction.lower():
            continue

        if biome and asset.get('Biome', '').lower() != biome.lower():
            continue

        if priority and asset.get('Priority', '').upper() != priority.upper():
            continue

        filtered.append(asset)

        if limit and len(filtered) >= limit:
            break

    print(f"[Filter] {len(filtered)} assets match criteria")
    return filtered


def update_csv_status(
    csv_path: Path,
    asset_id: str,
    stage: int,
    status: str,
    output_path: Optional[str] = None,
    quality_rating: Optional[str] = None
):
    """Update the status of an asset in the CSV."""
    # Read all rows
    rows = []
    fieldnames = None

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    # Find and update the asset
    for row in rows:
        if row['Asset_ID'] == asset_id:
            stage_col = f'Stage{stage}_Status'
            if stage_col in row:
                row[stage_col] = status

            if output_path:
                row['Notes'] = f"{row.get('Notes', '')} | Stage{stage}: {output_path}"

            if quality_rating:
                row['Quality_Rating'] = quality_rating
            break

    # Write back
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[CSV] Updated {asset_id} Stage{stage}_Status = {status}")


def run_pipeline_for_asset(
    asset: Dict,
    dry_run: bool = False,
    skip_approval: bool = False
) -> Dict:
    """Run the full Stage 1-7 pipeline for a single asset."""
    asset_id = asset['Asset_ID']
    prompt = asset['Base_Prompt']
    negative_prompt = asset['Negative_Prompt']
    resolution = asset.get('Resolution', '1024x1024')

    print(f"\n{'='*60}")
    print(f"PROCESSING: {asset_id} - {asset['Asset_Name']}")
    print(f"Category: {asset['Category']} | Faction: {asset['Faction']} | Biome: {asset['Biome']}")
    print(f"{'='*60}")

    if dry_run:
        print("[DRY RUN] Would execute pipeline with:")
        print(f"  Prompt: {prompt[:100]}...")
        print(f"  Negative: {negative_prompt[:50]}...")
        print(f"  Resolution: {resolution}")
        return {"success": True, "dry_run": True, "asset_id": asset_id}

    # Import pipeline functions
    try:
        from automated_pipeline import (
            stage1_generate_2d,
            stage2_background_removal,
            stage3_upscale,
            stage4_2d_to_3d,
            stage5_8dir_sprites,
            stage6_sprite_sheet,
            stage7_faction_colors,
            human_approval_gate
        )
    except ImportError as e:
        print(f"[ERROR] Could not import pipeline: {e}")
        return {"success": False, "error": str(e), "asset_id": asset_id}

    results = {
        "asset_id": asset_id,
        "stages": {}
    }

    # Create output directory for this asset
    asset_output_dir = OUTPUT_BASE / asset['Category'].lower() / asset_id
    asset_output_dir.mkdir(parents=True, exist_ok=True)

    current_image = None

    # Stage 1: 2D Generation
    print(f"\n[Stage 1] Generating 2D image...")
    update_csv_status(CSV_PATH, asset_id, 1, "IN_PROGRESS")

    try:
        stage1_result = stage1_generate_2d(prompt, negative_prompt)
        if stage1_result['success']:
            current_image = stage1_result['output']
            results['stages']['stage1'] = {"success": True, "output": current_image}
            update_csv_status(CSV_PATH, asset_id, 1, "SUCCESS", current_image)
        else:
            update_csv_status(CSV_PATH, asset_id, 1, "FAILED")
            results['stages']['stage1'] = {"success": False, "error": stage1_result.get('error')}
            return results
    except Exception as e:
        update_csv_status(CSV_PATH, asset_id, 1, "FAILED")
        results['stages']['stage1'] = {"success": False, "error": str(e)}
        return results

    # Approval Gate 1
    if not skip_approval:
        approved, _ = human_approval_gate(
            stage_name="Stage 1: 2D Generation",
            asset_name=asset['Asset_Name'],
            description=f"Generated 2D concept for {asset_id}",
            image_path=current_image,
            stage_number=1
        )
        if not approved:
            update_csv_status(CSV_PATH, asset_id, 1, "REJECTED")
            return results

    # Stage 2: Background Removal
    print(f"\n[Stage 2] Removing background...")
    update_csv_status(CSV_PATH, asset_id, 2, "IN_PROGRESS")

    try:
        stage2_result = stage2_background_removal(current_image)
        if stage2_result['success']:
            current_image = stage2_result['output']
            results['stages']['stage2'] = {"success": True, "output": current_image}
            update_csv_status(CSV_PATH, asset_id, 2, "SUCCESS", current_image)
        else:
            update_csv_status(CSV_PATH, asset_id, 2, "FAILED")
            results['stages']['stage2'] = {"success": False}
            return results
    except Exception as e:
        update_csv_status(CSV_PATH, asset_id, 2, "FAILED")
        results['stages']['stage2'] = {"success": False, "error": str(e)}
        return results

    # Stage 3: Upscaling
    print(f"\n[Stage 3] Upscaling image...")
    update_csv_status(CSV_PATH, asset_id, 3, "IN_PROGRESS")

    try:
        stage3_result = stage3_upscale(current_image)
        if stage3_result['success']:
            current_image = stage3_result['output']
            results['stages']['stage3'] = {"success": True, "output": current_image}
            update_csv_status(CSV_PATH, asset_id, 3, "SUCCESS", current_image)
        else:
            update_csv_status(CSV_PATH, asset_id, 3, "FAILED")
            results['stages']['stage3'] = {"success": False}
            return results
    except Exception as e:
        update_csv_status(CSV_PATH, asset_id, 3, "FAILED")
        results['stages']['stage3'] = {"success": False, "error": str(e)}
        return results

    # Stage 4: 2D to 3D
    print(f"\n[Stage 4] Converting to 3D...")
    update_csv_status(CSV_PATH, asset_id, 4, "IN_PROGRESS")

    try:
        stage4_result = stage4_2d_to_3d(current_image)
        if stage4_result['success']:
            current_model = stage4_result['output']
            results['stages']['stage4'] = {"success": True, "output": current_model}
            update_csv_status(CSV_PATH, asset_id, 4, "SUCCESS", current_model)
        else:
            update_csv_status(CSV_PATH, asset_id, 4, "FAILED")
            results['stages']['stage4'] = {"success": False}
            return results
    except Exception as e:
        update_csv_status(CSV_PATH, asset_id, 4, "FAILED")
        results['stages']['stage4'] = {"success": False, "error": str(e)}
        return results

    # Stage 5: 8-Direction Sprites
    print(f"\n[Stage 5] Rendering 8-direction sprites...")
    update_csv_status(CSV_PATH, asset_id, 5, "IN_PROGRESS")

    try:
        stage5_result = stage5_8dir_sprites(current_model)
        if stage5_result['success']:
            sprite_outputs = stage5_result['output']
            results['stages']['stage5'] = {"success": True, "output": sprite_outputs}
            update_csv_status(CSV_PATH, asset_id, 5, "SUCCESS")
        else:
            update_csv_status(CSV_PATH, asset_id, 5, "FAILED")
            results['stages']['stage5'] = {"success": False}
            return results
    except Exception as e:
        update_csv_status(CSV_PATH, asset_id, 5, "FAILED")
        results['stages']['stage5'] = {"success": False, "error": str(e)}
        return results

    # Stage 6: Sprite Sheet Assembly
    print(f"\n[Stage 6] Assembling sprite sheet...")
    update_csv_status(CSV_PATH, asset_id, 6, "IN_PROGRESS")

    try:
        stage6_result = stage6_sprite_sheet(sprite_outputs)
        if stage6_result['success']:
            spritesheet = stage6_result['output']
            results['stages']['stage6'] = {"success": True, "output": spritesheet}
            update_csv_status(CSV_PATH, asset_id, 6, "SUCCESS", spritesheet)
        else:
            update_csv_status(CSV_PATH, asset_id, 6, "FAILED")
            results['stages']['stage6'] = {"success": False}
            return results
    except Exception as e:
        update_csv_status(CSV_PATH, asset_id, 6, "FAILED")
        results['stages']['stage6'] = {"success": False, "error": str(e)}
        return results

    # Stage 7: Faction Color Variants
    print(f"\n[Stage 7] Creating faction color variants...")
    update_csv_status(CSV_PATH, asset_id, 7, "IN_PROGRESS")

    try:
        stage7_result = stage7_faction_colors(spritesheet)
        if stage7_result['success']:
            variants = stage7_result['output']
            results['stages']['stage7'] = {"success": True, "output": variants}
            update_csv_status(CSV_PATH, asset_id, 7, "SUCCESS")

            # Final success
            update_csv_status(CSV_PATH, asset_id, 7, "SUCCESS", quality_rating="PENDING_REVIEW")
        else:
            update_csv_status(CSV_PATH, asset_id, 7, "FAILED")
            results['stages']['stage7'] = {"success": False}
            return results
    except Exception as e:
        update_csv_status(CSV_PATH, asset_id, 7, "FAILED")
        results['stages']['stage7'] = {"success": False, "error": str(e)}
        return results

    results['success'] = True
    print(f"\n[COMPLETE] {asset_id} processed through all 7 stages!")
    return results


def generate_batch_report(results: List[Dict], output_path: Path):
    """Generate a summary report of batch processing."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_processed": len(results),
        "successful": sum(1 for r in results if r.get('success')),
        "failed": sum(1 for r in results if not r.get('success')),
        "results": results
    }

    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n[REPORT] Saved to {output_path}")
    print(f"  Total: {report['total_processed']}")
    print(f"  Success: {report['successful']}")
    print(f"  Failed: {report['failed']}")


def main():
    parser = argparse.ArgumentParser(
        description="Run Stage 1-7 pipeline from CSV tracking spreadsheet"
    )
    parser.add_argument('--category', help='Filter by category (Hero, Unit, Building, Enemy, Prop)')
    parser.add_argument('--faction', help='Filter by faction (Sand_Vanguard, Cinder_Forgers, etc.)')
    parser.add_argument('--biome', help='Filter by biome (Desert_Wastes, Volcanic_Lands, etc.)')
    parser.add_argument('--priority', help='Filter by priority (P0, P1, P2)')
    parser.add_argument('--limit', type=int, help='Maximum number of assets to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be processed without executing')
    parser.add_argument('--skip-approval', action='store_true', help='Skip Discord approval gates')
    parser.add_argument('--asset-id', help='Process a specific asset by ID')

    args = parser.parse_args()

    print("=" * 60)
    print("MEOW PING NFT - CSV PIPELINE RUNNER")
    print("=" * 60)

    # Load assets
    if not CSV_PATH.exists():
        print(f"[ERROR] CSV not found: {CSV_PATH}")
        sys.exit(1)

    assets = load_csv_assets(CSV_PATH)

    # Filter or select specific asset
    if args.asset_id:
        filtered = [a for a in assets if a['Asset_ID'] == args.asset_id]
        if not filtered:
            print(f"[ERROR] Asset not found: {args.asset_id}")
            sys.exit(1)
    else:
        filtered = filter_assets(
            assets,
            category=args.category,
            faction=args.faction,
            biome=args.biome,
            priority=args.priority,
            limit=args.limit
        )

    if not filtered:
        print("[INFO] No assets match the criteria")
        sys.exit(0)

    # Process assets
    results = []
    for asset in filtered:
        result = run_pipeline_for_asset(
            asset,
            dry_run=args.dry_run,
            skip_approval=args.skip_approval
        )
        results.append(result)

    # Generate report
    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_BASE / f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    generate_batch_report(results, report_path)


if __name__ == "__main__":
    main()
