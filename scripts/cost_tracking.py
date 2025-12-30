#!/usr/bin/env python3
"""
Cost Tracking & Forecasting System for Meow Ping NFT Pipeline

This module handles:
- Per-stage cost estimation and tracking
- Asset value calculation based on rarity/tier
- ROI forecasting and variance analysis
- Budget projections for production scaling
- VPS infrastructure cost amortization

DEPLOYMENT MODEL (as of Dec 2025):
- Stage 1: RunPod Cloud (serverless GPU)
- Stages 2-7: VPS (Hostinger) - runs 24/7

Service Pricing (as of Dec 2025):
- RunPod SDXL Serverless: ~$0.00025/sec (~$0.003-0.005 per image)
- BRIA RMBG: FREE (VPS local processing)
- PIL Lanczos Upscale: FREE (VPS local processing)
- Meshy.ai: 200 free/mo, then ~$0.08 per model ($16/mo unlimited)
- Tripo AI: ~$0.10 per model
- Blender Render: FREE (VPS local processing)
- Sprite Assembly: FREE (VPS local processing)
- Faction Variants: FREE (VPS local processing)

Monthly Infrastructure Costs:
- Hostinger VPS: $12/mo (24/7 operation)
- RunPod (estimated): ~$20/mo (5000 generations)
- Meshy.ai (after free): $16/mo (unlimited)
- Discord Bot: FREE (runs on VPS)
- Total Fixed: ~$48/mo
"""

import csv
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# =============================================================================
# COST CONFIGURATION
# =============================================================================

class ServiceTier(Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    UNLIMITED = "unlimited"


# =============================================================================
# VPS INFRASTRUCTURE COSTS (Monthly)
# =============================================================================

VPS_INFRASTRUCTURE = {
    "hostinger_vps": 12.00,        # KVM 4 VPS - 24/7 operation
    "runpod_estimated": 20.00,     # ~5000 generations/month
    "meshy_subscription": 16.00,   # After 200 free tier
    "discord_bot": 0.00,           # Runs on VPS
}

MONTHLY_FIXED_COSTS = sum(VPS_INFRASTRUCTURE.values())  # ~$48/mo

# VPS status and uptime tracking
VPS_CONFIG = {
    "host": "82.25.112.73",
    "provider": "Hostinger",
    "plan": "KVM 4",
    "services": [
        "n8n", "postgres", "mongodb", "redis", "grafana",
        "prometheus", "nginx", "ollama", "flowise", "open-webui",
        "mcp-gateway", "discord-bot"
    ],
    "pipeline_stages_on_vps": [2, 3, 4, 5, 6, 7],  # Stage 1 uses cloud GPU
}

# Per-execution costs by stage (USD)
STAGE_COSTS = {
    "stage1_2d_gen": {
        "runpod_sdxl": 0.004,      # ~$0.00025/sec * 16 sec avg
        "comfyui_local": 0.00,     # Free if local GPU
        "replicate_sdxl": 0.0023,  # Replicate pricing
    },
    "stage2_bg_removal": {
        "bria_rmbg": 0.00,         # Free - runs on VPS
        "remove_bg_api": 0.01,     # remove.bg API (cloud alternative)
        "local_rembg": 0.00,       # VPS rembg
    },
    "stage3_upscale": {
        "pil_lanczos": 0.00,       # Free - runs on VPS
        "replicate_esrgan": 0.01,  # Replicate Real-ESRGAN (cloud alternative)
        "topaz_api": 0.02,         # Topaz Labs API (cloud alternative)
    },
    "stage4_2d_to_3d": {
        "meshy_free": 0.00,        # Free tier (200/mo) - API call from VPS
        "meshy_paid": 0.08,        # Paid tier - API call from VPS
        "tripo_ai": 0.10,          # Tripo AI - API call from VPS
        "triposr_colab": 0.00,     # Free Colab (manual)
    },
    "stage5_sprites": {
        "blender_local": 0.00,     # Free - Blender runs on VPS
        "blender_cloud": 0.02,     # Cloud render farm (alternative)
    },
    "stage6_spritesheet": {
        "pil_local": 0.00,         # Free - PIL runs on VPS
    },
    "stage7_factions": {
        "pil_local": 0.00,         # Free - PIL runs on VPS
    },
}

# Asset value multipliers by rarity
RARITY_VALUE_MULTIPLIERS = {
    "Common": 1.0,
    "Uncommon": 1.5,
    "Rare": 2.5,
    "Epic": 5.0,
    "Legendary": 10.0,
    "Mythic": 25.0,
}

# Base values by category (USD)
CATEGORY_BASE_VALUES = {
    "Hero": 50.0,
    "Unit": 10.0,
    "Building": 25.0,
    "Terrain": 5.0,
    "Prop": 3.0,
    "Effect": 8.0,
}

# NFT tier multipliers
NFT_TIER_MULTIPLIERS = {
    "Heroes": 3.0,
    "Commanders": 2.0,
    "Units": 1.0,
    "Structures": 1.5,
    "Terrain": 0.5,
}

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class StageCost:
    """Cost data for a single pipeline stage."""
    estimated: float = 0.0
    actual: float = 0.0
    service_used: str = ""
    duration_sec: float = 0.0

@dataclass
class AssetCosts:
    """Complete cost tracking for an asset."""
    asset_id: str
    stage1: StageCost = None
    stage2: StageCost = None
    stage3: StageCost = None
    stage4: StageCost = None
    stage5: StageCost = None
    stage6: StageCost = None
    stage7: StageCost = None
    total_estimated: float = 0.0
    total_actual: float = 0.0
    cost_variance: float = 0.0
    cost_variance_pct: float = 0.0

    def __post_init__(self):
        for i in range(1, 8):
            if getattr(self, f"stage{i}") is None:
                setattr(self, f"stage{i}", StageCost())

@dataclass
class AssetValue:
    """Value calculations for an asset."""
    base_value: float = 0.0
    rarity_multiplier: float = 1.0
    tier_multiplier: float = 1.0
    market_value_est: float = 0.0
    mint_price_target: float = 0.0
    cost_per_variant: float = 0.0
    roi_multiplier: float = 0.0

# =============================================================================
# COST CALCULATION FUNCTIONS
# =============================================================================

def estimate_stage_costs(category: str, service_config: Dict[str, str] = None) -> Dict[str, float]:
    """
    Estimate costs for each stage based on selected services.

    Args:
        category: Asset category (Hero, Unit, Building, etc.)
        service_config: Override default service selections

    Returns:
        Dict with estimated cost per stage
    """
    # Default service selections (most cost-effective)
    defaults = {
        "stage1": "runpod_sdxl",
        "stage2": "bria_rmbg",
        "stage3": "pil_lanczos",
        "stage4": "meshy_free",  # Assumes free tier available
        "stage5": "blender_local",
        "stage6": "pil_local",
        "stage7": "pil_local",
    }

    config = {**defaults, **(service_config or {})}

    estimates = {}
    for stage_num in range(1, 8):
        stage_key = f"stage{stage_num}"
        cost_key = list(STAGE_COSTS.keys())[stage_num - 1]
        service = config.get(stage_key, list(STAGE_COSTS[cost_key].keys())[0])
        estimates[stage_key] = STAGE_COSTS[cost_key].get(service, 0.0)

    return estimates


def calculate_asset_value(category: str, rarity: str, nft_tier: str) -> AssetValue:
    """
    Calculate estimated market value for an asset.

    Args:
        category: Asset category
        rarity: Rarity level
        nft_tier: NFT collection tier

    Returns:
        AssetValue with all calculated fields
    """
    base = CATEGORY_BASE_VALUES.get(category, 10.0)
    rarity_mult = RARITY_VALUE_MULTIPLIERS.get(rarity, 1.0)
    tier_mult = NFT_TIER_MULTIPLIERS.get(nft_tier, 1.0)

    market_value = base * rarity_mult * tier_mult

    # Mint price typically 60-80% of expected market value
    mint_price = market_value * 0.7

    return AssetValue(
        base_value=base,
        rarity_multiplier=rarity_mult,
        tier_multiplier=tier_mult,
        market_value_est=round(market_value, 2),
        mint_price_target=round(mint_price, 2),
    )


def calculate_roi(total_cost: float, market_value: float, variant_count: int = 4) -> Tuple[float, float]:
    """
    Calculate ROI metrics.

    Returns:
        Tuple of (cost_per_variant, roi_multiplier)
    """
    cost_per_variant = total_cost / variant_count if variant_count > 0 else total_cost
    roi_mult = market_value / total_cost if total_cost > 0 else float('inf')
    return round(cost_per_variant, 4), round(roi_mult, 2)


# =============================================================================
# CSV ENHANCEMENT
# =============================================================================

# New columns to add to the tracking CSV
NEW_COST_COLUMNS = [
    # Per-stage estimated costs
    "Stage1_Est_Cost",
    "Stage1_Act_Cost",
    "Stage1_Service",
    "Stage2_Est_Cost",
    "Stage2_Act_Cost",
    "Stage2_Service",
    "Stage3_Est_Cost",
    "Stage3_Act_Cost",
    "Stage3_Service",
    "Stage4_Est_Cost",
    "Stage4_Act_Cost",
    "Stage4_Service",
    "Stage5_Est_Cost",
    "Stage5_Act_Cost",
    "Stage5_Service",
    "Stage6_Est_Cost",
    "Stage6_Act_Cost",
    "Stage6_Service",
    "Stage7_Est_Cost",
    "Stage7_Act_Cost",
    "Stage7_Service",
    # Totals
    "Total_Est_Cost",
    "Total_Act_Cost",
    "Cost_Variance",
    "Cost_Variance_Pct",
    # Asset value
    "Base_Value",
    "Market_Value_Est",
    "Mint_Price_Target",
    # ROI
    "Cost_Per_Variant",
    "ROI_Multiplier",
    # Timing
    "Pipeline_Start",
    "Pipeline_End",
    "Duration_Minutes",
]


def add_cost_columns_to_csv(csv_path: Path, output_path: Path = None) -> Path:
    """
    Add cost tracking columns to existing asset CSV.

    Args:
        csv_path: Path to existing CSV
        output_path: Optional output path (defaults to overwrite)

    Returns:
        Path to updated CSV
    """
    if output_path is None:
        output_path = csv_path

    # Read existing data
    rows = []
    fieldnames = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    # Add new columns if not present
    for col in NEW_COST_COLUMNS:
        if col not in fieldnames:
            fieldnames.append(col)

    # Calculate default estimates for each row
    for row in rows:
        category = row.get('Category', 'Unit')
        rarity = row.get('Rarity', 'Common')
        nft_tier = row.get('NFT_Tier', 'Units')

        # Stage cost estimates
        estimates = estimate_stage_costs(category)
        for stage_num in range(1, 8):
            est_col = f"Stage{stage_num}_Est_Cost"
            act_col = f"Stage{stage_num}_Act_Cost"
            svc_col = f"Stage{stage_num}_Service"

            if not row.get(est_col):
                row[est_col] = f"{estimates[f'stage{stage_num}']:.4f}"
            if not row.get(act_col):
                row[act_col] = ""
            if not row.get(svc_col):
                # Default service names
                services = ["runpod_sdxl", "bria_rmbg", "pil_lanczos",
                           "meshy_free", "blender_local", "pil_local", "pil_local"]
                row[svc_col] = services[stage_num - 1]

        # Total estimates
        total_est = sum(float(row.get(f"Stage{i}_Est_Cost", 0) or 0) for i in range(1, 8))
        row["Total_Est_Cost"] = f"{total_est:.4f}"

        # Asset value
        value = calculate_asset_value(category, rarity, nft_tier)
        row["Base_Value"] = f"{value.base_value:.2f}"
        row["Market_Value_Est"] = f"{value.market_value_est:.2f}"
        row["Mint_Price_Target"] = f"{value.mint_price_target:.2f}"

        # ROI (using estimated cost)
        cost_per_var, roi_mult = calculate_roi(total_est, value.market_value_est)
        row["Cost_Per_Variant"] = f"{cost_per_var:.4f}"
        row["ROI_Multiplier"] = f"{roi_mult:.2f}"

        # Initialize empty timing fields
        if not row.get("Pipeline_Start"):
            row["Pipeline_Start"] = ""
        if not row.get("Pipeline_End"):
            row["Pipeline_End"] = ""
        if not row.get("Duration_Minutes"):
            row["Duration_Minutes"] = ""

    # Write updated CSV
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[Cost Tracking] Updated CSV with {len(NEW_COST_COLUMNS)} new columns")
    print(f"[Cost Tracking] Output: {output_path}")

    return output_path


def update_actual_cost(csv_path: Path, asset_id: str, stage: int,
                       actual_cost: float, service: str = None,
                       duration_sec: float = None):
    """
    Update actual cost for a completed stage.

    Args:
        csv_path: Path to tracking CSV
        asset_id: Asset identifier
        stage: Stage number (1-7)
        actual_cost: Actual cost incurred
        service: Service used (optional)
        duration_sec: Processing duration in seconds (optional)
    """
    rows = []
    fieldnames = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    for row in rows:
        if row['Asset_ID'] == asset_id:
            row[f"Stage{stage}_Act_Cost"] = f"{actual_cost:.4f}"
            if service:
                row[f"Stage{stage}_Service"] = service

            # Recalculate totals
            total_act = sum(float(row.get(f"Stage{i}_Act_Cost", 0) or 0) for i in range(1, 8))
            total_est = float(row.get("Total_Est_Cost", 0) or 0)

            row["Total_Act_Cost"] = f"{total_act:.4f}"

            if total_act > 0:
                variance = total_act - total_est
                variance_pct = (variance / total_est * 100) if total_est > 0 else 0
                row["Cost_Variance"] = f"{variance:.4f}"
                row["Cost_Variance_Pct"] = f"{variance_pct:.1f}%"

                # Update ROI with actual cost
                market_value = float(row.get("Market_Value_Est", 0) or 0)
                cost_per_var, roi_mult = calculate_roi(total_act, market_value)
                row["Cost_Per_Variant"] = f"{cost_per_var:.4f}"
                row["ROI_Multiplier"] = f"{roi_mult:.2f}"

            break

    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def record_pipeline_timing(csv_path: Path, asset_id: str,
                           start_time: datetime = None,
                           end_time: datetime = None):
    """Record pipeline execution timing."""
    rows = []
    fieldnames = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    for row in rows:
        if row['Asset_ID'] == asset_id:
            if start_time:
                row["Pipeline_Start"] = start_time.isoformat()
            if end_time:
                row["Pipeline_End"] = end_time.isoformat()

            # Calculate duration if both times present
            if row.get("Pipeline_Start") and row.get("Pipeline_End"):
                start = datetime.fromisoformat(row["Pipeline_Start"])
                end = datetime.fromisoformat(row["Pipeline_End"])
                duration_min = (end - start).total_seconds() / 60
                row["Duration_Minutes"] = f"{duration_min:.1f}"
            break

    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# =============================================================================
# FORECASTING & REPORTING
# =============================================================================

def generate_cost_forecast(csv_path: Path) -> Dict:
    """
    Generate cost forecast report based on current data.

    Returns:
        Dict with forecast data including:
        - Total estimated cost for all assets
        - Total estimated value
        - Projected ROI
        - Cost breakdown by category/faction/rarity
    """
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Initialize aggregations
    total_assets = len(rows)
    total_est_cost = 0.0
    total_act_cost = 0.0
    total_market_value = 0.0

    by_category = {}
    by_faction = {}
    by_rarity = {}
    by_status = {"completed": 0, "in_progress": 0, "pending": 0}

    completed_costs = []

    for row in rows:
        category = row.get('Category', 'Unknown')
        faction = row.get('Faction', 'Unknown')
        rarity = row.get('Rarity', 'Common')

        est_cost = float(row.get('Total_Est_Cost', 0) or 0)
        act_cost = float(row.get('Total_Act_Cost', 0) or 0)
        market_val = float(row.get('Market_Value_Est', 0) or 0)

        total_est_cost += est_cost
        total_act_cost += act_cost
        total_market_value += market_val

        # By category
        if category not in by_category:
            by_category[category] = {"count": 0, "est_cost": 0, "market_value": 0}
        by_category[category]["count"] += 1
        by_category[category]["est_cost"] += est_cost
        by_category[category]["market_value"] += market_val

        # By faction
        if faction not in by_faction:
            by_faction[faction] = {"count": 0, "est_cost": 0, "market_value": 0}
        by_faction[faction]["count"] += 1
        by_faction[faction]["est_cost"] += est_cost
        by_faction[faction]["market_value"] += market_val

        # By rarity
        if rarity not in by_rarity:
            by_rarity[rarity] = {"count": 0, "est_cost": 0, "market_value": 0}
        by_rarity[rarity]["count"] += 1
        by_rarity[rarity]["est_cost"] += est_cost
        by_rarity[rarity]["market_value"] += market_val

        # Status tracking
        stage7_status = row.get('Stage7_Status', 'PENDING')
        if stage7_status == 'SUCCESS':
            by_status["completed"] += 1
            if act_cost > 0:
                completed_costs.append(act_cost)
        elif any(row.get(f'Stage{i}_Status') == 'IN_PROGRESS' for i in range(1, 8)):
            by_status["in_progress"] += 1
        else:
            by_status["pending"] += 1

    # Calculate averages from completed assets
    avg_actual_cost = sum(completed_costs) / len(completed_costs) if completed_costs else est_cost / total_assets if total_assets > 0 else 0

    # Project total cost using actual average where available
    projected_total_cost = avg_actual_cost * total_assets

    # Calculate infrastructure cost amortization per asset
    # Assumes ~500 assets/month capacity on VPS
    assets_per_month_capacity = 500
    infra_cost_per_asset = MONTHLY_FIXED_COSTS / assets_per_month_capacity  # ~$0.096/asset

    # Total cost including infrastructure amortization
    total_cost_with_infra = projected_total_cost + (total_assets * infra_cost_per_asset)

    forecast = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_assets": total_assets,
            "completed": by_status["completed"],
            "in_progress": by_status["in_progress"],
            "pending": by_status["pending"],
            "completion_pct": round(by_status["completed"] / total_assets * 100, 1) if total_assets > 0 else 0,
        },
        "infrastructure": {
            "vps_host": VPS_CONFIG["host"],
            "vps_provider": VPS_CONFIG["provider"],
            "monthly_fixed_costs": round(MONTHLY_FIXED_COSTS, 2),
            "cost_breakdown": VPS_INFRASTRUCTURE,
            "amortized_per_asset": round(infra_cost_per_asset, 4),
            "stages_on_vps": VPS_CONFIG["pipeline_stages_on_vps"],
            "deployment_model": "Stage 1: Cloud GPU (RunPod), Stages 2-7: VPS (24/7)",
        },
        "costs": {
            "total_estimated": round(total_est_cost, 2),
            "total_actual": round(total_act_cost, 2),
            "avg_per_asset_est": round(total_est_cost / total_assets, 4) if total_assets > 0 else 0,
            "avg_per_asset_actual": round(avg_actual_cost, 4),
            "projected_total": round(projected_total_cost, 2),
            "projected_with_infra": round(total_cost_with_infra, 2),
            "variance": round(total_act_cost - total_est_cost, 2) if total_act_cost > 0 else 0,
        },
        "value": {
            "total_market_value": round(total_market_value, 2),
            "avg_per_asset": round(total_market_value / total_assets, 2) if total_assets > 0 else 0,
            "total_mint_revenue": round(total_market_value * 0.7, 2),  # 70% of market value
        },
        "roi": {
            "projected_roi_multiplier": round(total_market_value / projected_total_cost, 2) if projected_total_cost > 0 else 0,
            "roi_with_infra": round(total_market_value / total_cost_with_infra, 2) if total_cost_with_infra > 0 else 0,
            "gross_profit_projected": round(total_market_value * 0.7 - projected_total_cost, 2),
            "gross_profit_with_infra": round(total_market_value * 0.7 - total_cost_with_infra, 2),
            "profit_margin_pct": round((total_market_value * 0.7 - projected_total_cost) / (total_market_value * 0.7) * 100, 1) if total_market_value > 0 else 0,
        },
        "by_category": by_category,
        "by_faction": by_faction,
        "by_rarity": by_rarity,
    }

    return forecast


def generate_forecast_report(csv_path: Path, output_path: Path = None) -> Path:
    """
    Generate a detailed forecast report as JSON.
    """
    forecast = generate_cost_forecast(csv_path)

    if output_path is None:
        output_path = csv_path.parent / "cost_forecast_report.json"

    with open(output_path, 'w') as f:
        json.dump(forecast, f, indent=2)

    print(f"[Forecast] Generated report: {output_path}")
    return output_path


def print_forecast_summary(csv_path: Path):
    """Print a formatted forecast summary to console."""
    forecast = generate_cost_forecast(csv_path)

    print("\n" + "=" * 60)
    print("MEOW PING NFT - COST FORECAST SUMMARY")
    print("=" * 60)

    # Infrastructure section (NEW)
    i = forecast["infrastructure"]
    print(f"\nInfrastructure (VPS @ {i['vps_host']}):")
    print(f"  - Provider: {i['vps_provider']}")
    print(f"  - Monthly Fixed: ${i['monthly_fixed_costs']:.2f}/mo")
    print(f"  - Cost/Asset (amortized): ${i['amortized_per_asset']:.4f}")
    print(f"  - Deployment: {i['deployment_model']}")

    s = forecast["summary"]
    print(f"\nAssets: {s['total_assets']} total")
    print(f"  - Completed: {s['completed']} ({s['completion_pct']}%)")
    print(f"  - In Progress: {s['in_progress']}")
    print(f"  - Pending: {s['pending']}")

    c = forecast["costs"]
    print(f"\nCosts (USD):")
    print(f"  - Estimated Total: ${c['total_estimated']:.2f}")
    print(f"  - Actual Total: ${c['total_actual']:.2f}")
    print(f"  - Projected (API only): ${c['projected_total']:.2f}")
    print(f"  - Projected (with infra): ${c['projected_with_infra']:.2f}")
    print(f"  - Avg per Asset: ${c['avg_per_asset_est']:.4f}")

    v = forecast["value"]
    print(f"\nValue (USD):")
    print(f"  - Total Market Value: ${v['total_market_value']:.2f}")
    print(f"  - Avg per Asset: ${v['avg_per_asset']:.2f}")
    print(f"  - Projected Mint Revenue: ${v['total_mint_revenue']:.2f}")

    r = forecast["roi"]
    print(f"\nROI Projections:")
    print(f"  - ROI (API costs only): {r['projected_roi_multiplier']:.0f}x")
    print(f"  - ROI (with infra): {r['roi_with_infra']:.0f}x")
    print(f"  - Gross Profit (API only): ${r['gross_profit_projected']:.2f}")
    print(f"  - Gross Profit (with infra): ${r['gross_profit_with_infra']:.2f}")
    print(f"  - Profit Margin: {r['profit_margin_pct']:.1f}%")

    print("\n" + "=" * 60)

    print("\nBy Category:")
    for cat, data in forecast["by_category"].items():
        print(f"  {cat}: {data['count']} assets, ${data['est_cost']:.2f} cost, ${data['market_value']:.2f} value")

    print("\nBy Rarity:")
    for rarity, data in forecast["by_rarity"].items():
        print(f"  {rarity}: {data['count']} assets, ${data['market_value']:.2f} value")

    print("\n" + "=" * 60)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cost tracking and forecasting for Meow Ping NFT pipeline")
    parser.add_argument('--csv', default='C:/Ziggie/assets/MEOW_PING_NFT_ASSET_TRACKING.csv',
                        help='Path to asset tracking CSV')
    parser.add_argument('--add-columns', action='store_true',
                        help='Add cost tracking columns to CSV')
    parser.add_argument('--forecast', action='store_true',
                        help='Generate cost forecast report')
    parser.add_argument('--summary', action='store_true',
                        help='Print forecast summary')
    parser.add_argument('--output', help='Output path for reports')

    args = parser.parse_args()
    csv_path = Path(args.csv)

    if args.add_columns:
        add_cost_columns_to_csv(csv_path)

    if args.forecast:
        output = Path(args.output) if args.output else None
        generate_forecast_report(csv_path, output)

    if args.summary:
        print_forecast_summary(csv_path)

    if not any([args.add_columns, args.forecast, args.summary]):
        # Default: add columns and show summary
        add_cost_columns_to_csv(csv_path)
        print_forecast_summary(csv_path)
