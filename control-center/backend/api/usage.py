"""
API Usage Tracking
Monitor API usage across Claude, OpenAI, YouTube, etc.
"""

from fastapi import Request, APIRouter, HTTPException, Query
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json
import os
import glob
import re
from middleware.rate_limit import limiter

router = APIRouter(prefix="/api/usage", tags=["usage"])

# Paths
KB_ROOT = Path("C:/meowping-rts/ai-agents/knowledge-base")
LOGS_DIR = KB_ROOT / "logs"
USAGE_DB = KB_ROOT / "metadata" / "usage-tracking.json"


# API Pricing (USD)
PRICING = {
    "claude": {
        "claude-3-opus-20240229": {
            "input": 15.00 / 1_000_000,
            "output": 75.00 / 1_000_000
        },
        "claude-3-sonnet-20240229": {
            "input": 3.00 / 1_000_000,
            "output": 15.00 / 1_000_000
        },
        "claude-3-haiku-20240307": {
            "input": 0.25 / 1_000_000,
            "output": 1.25 / 1_000_000
        }
    },
    "openai": {
        "gpt-4": {
            "input": 30.00 / 1_000_000,
            "output": 60.00 / 1_000_000
        },
        "gpt-4-turbo": {
            "input": 10.00 / 1_000_000,
            "output": 30.00 / 1_000_000
        },
        "gpt-3.5-turbo": {
            "input": 0.50 / 1_000_000,
            "output": 1.50 / 1_000_000
        }
    },
    "youtube": {
        "api_call": 0.01  # Estimated cost per API call
    }
}


def load_usage_db() -> Dict:
    """Load usage tracking database"""
    if not USAGE_DB.exists():
        return {
            "created": datetime.now().isoformat(),
            "total_calls": 0,
            "total_cost_usd": 0.0,
            "history": []
        }

    try:
        with open(USAGE_DB, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {
            "created": datetime.now().isoformat(),
            "total_calls": 0,
            "total_cost_usd": 0.0,
            "history": []
        }


def save_usage_db(data: Dict):
    """Save usage tracking database"""
    try:
        USAGE_DB.parent.mkdir(parents=True, exist_ok=True)
        with open(USAGE_DB, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving usage DB: {e}")


def parse_log_files_for_usage() -> Dict:
    """Parse log files to extract API usage statistics"""
    usage = {
        "claude": {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0},
        "openai": {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0},
        "youtube": {"calls": 0, "videos_processed": 0, "cost": 0.0}
    }

    if not LOGS_DIR.exists():
        return usage

    # Scan log files
    log_files = list(LOGS_DIR.glob("*.log")) + list(LOGS_DIR.glob("*.txt"))

    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Look for Claude API calls
            claude_pattern = r'claude.*?tokens.*?(\d+)'
            claude_matches = re.findall(claude_pattern, content, re.IGNORECASE)
            usage["claude"]["calls"] += len(claude_matches)

            # Look for token counts
            input_token_pattern = r'input.*?tokens?.*?[:\s](\d+)'
            output_token_pattern = r'output.*?tokens?.*?[:\s](\d+)'

            input_matches = re.findall(input_token_pattern, content, re.IGNORECASE)
            output_matches = re.findall(output_token_pattern, content, re.IGNORECASE)

            for match in input_matches:
                usage["claude"]["input_tokens"] += int(match)

            for match in output_matches:
                usage["claude"]["output_tokens"] += int(match)

            # Look for OpenAI API calls
            openai_pattern = r'openai|gpt-[34]'
            openai_matches = re.findall(openai_pattern, content, re.IGNORECASE)
            usage["openai"]["calls"] += len(openai_matches)

            # Look for YouTube API calls
            youtube_pattern = r'youtube.*?api|processing.*?video'
            youtube_matches = re.findall(youtube_pattern, content, re.IGNORECASE)
            usage["youtube"]["calls"] += len(youtube_matches)

            # Count videos processed
            video_processed_pattern = r'processing video:|video.*?processed'
            video_matches = re.findall(video_processed_pattern, content, re.IGNORECASE)
            usage["youtube"]["videos_processed"] += len(video_matches)

        except Exception:
            continue

    # Estimate costs (using Haiku pricing for Claude as default)
    if usage["claude"]["input_tokens"] > 0 or usage["claude"]["output_tokens"] > 0:
        usage["claude"]["cost"] = (
            usage["claude"]["input_tokens"] * PRICING["claude"]["claude-3-haiku-20240307"]["input"] +
            usage["claude"]["output_tokens"] * PRICING["claude"]["claude-3-haiku-20240307"]["output"]
        )

    # Estimate OpenAI cost (using GPT-3.5 as default)
    if usage["openai"]["calls"] > 0:
        # Estimate tokens (rough average: 500 input, 200 output per call)
        estimated_input = usage["openai"]["calls"] * 500
        estimated_output = usage["openai"]["calls"] * 200
        usage["openai"]["cost"] = (
            estimated_input * PRICING["openai"]["gpt-3.5-turbo"]["input"] +
            estimated_output * PRICING["openai"]["gpt-3.5-turbo"]["output"]
        )

    # YouTube cost
    usage["youtube"]["cost"] = usage["youtube"]["calls"] * PRICING["youtube"]["api_call"]

    return usage


@router.get("/stats")
@limiter.limit("60/minute")
async def get_usage_stats(request: Request, ):
    """Get current API usage statistics"""
    try:
        # Parse logs for real-time usage
        current_usage = parse_log_files_for_usage()

        # Load historical data
        usage_db = load_usage_db()

        # Calculate total cost
        total_cost = (
            current_usage["claude"]["cost"] +
            current_usage["openai"]["cost"] +
            current_usage["youtube"]["cost"]
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "total_cost_usd": round(total_cost, 4),
            "breakdown": {
                "claude": {
                    "calls": current_usage["claude"]["calls"],
                    "input_tokens": current_usage["claude"]["input_tokens"],
                    "output_tokens": current_usage["claude"]["output_tokens"],
                    "cost_usd": round(current_usage["claude"]["cost"], 4)
                },
                "openai": {
                    "calls": current_usage["openai"]["calls"],
                    "estimated_cost_usd": round(current_usage["openai"]["cost"], 4)
                },
                "youtube": {
                    "api_calls": current_usage["youtube"]["calls"],
                    "videos_processed": current_usage["youtube"]["videos_processed"],
                    "cost_usd": round(current_usage["youtube"]["cost"], 4)
                }
            },
            "historical_total": usage_db.get("total_cost_usd", 0.0)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting usage stats: {str(e)}")


@router.get("/history")
@limiter.limit("60/minute")
async def get_usage_history(request: Request, 
    days: int = Query(30, ge=1, le=365),
    api: Optional[str] = None
):
    """Get usage history over time"""
    try:
        usage_db = load_usage_db()
        history = usage_db.get("history", [])

        # Filter by date range
        cutoff_date = datetime.now() - timedelta(days=days)

        filtered_history = [
            entry for entry in history
            if datetime.fromisoformat(entry.get("timestamp", "2020-01-01")) > cutoff_date
        ]

        # Filter by API if specified
        if api:
            filtered_history = [
                entry for entry in filtered_history
                if entry.get("api") == api
            ]

        # Aggregate by day
        daily_usage = {}

        for entry in filtered_history:
            date_str = entry.get("timestamp", "")[:10]  # Get YYYY-MM-DD

            if date_str not in daily_usage:
                daily_usage[date_str] = {
                    "date": date_str,
                    "total_calls": 0,
                    "total_cost": 0.0,
                    "by_api": {}
                }

            api_name = entry.get("api", "unknown")
            daily_usage[date_str]["total_calls"] += 1
            daily_usage[date_str]["total_cost"] += entry.get("cost", 0.0)

            if api_name not in daily_usage[date_str]["by_api"]:
                daily_usage[date_str]["by_api"][api_name] = {
                    "calls": 0,
                    "cost": 0.0
                }

            daily_usage[date_str]["by_api"][api_name]["calls"] += 1
            daily_usage[date_str]["by_api"][api_name]["cost"] += entry.get("cost", 0.0)

        # Convert to list and sort
        daily_list = sorted(daily_usage.values(), key=lambda x: x["date"])

        return {
            "days": days,
            "api_filter": api,
            "total_entries": len(filtered_history),
            "daily_usage": daily_list
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting usage history: {str(e)}")


@router.post("/track")
async def track_api_call(
    api: str,
    model: Optional[str] = None,
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None,
    cost: Optional[float] = None,
    metadata: Optional[Dict] = None
):
    """Track an API call (for internal use)"""
    try:
        # Load usage DB
        usage_db = load_usage_db()

        # Calculate cost if not provided
        calculated_cost = cost

        if calculated_cost is None and api == "claude" and model and input_tokens and output_tokens:
            if model in PRICING["claude"]:
                calculated_cost = (
                    input_tokens * PRICING["claude"][model]["input"] +
                    output_tokens * PRICING["claude"][model]["output"]
                )

        if calculated_cost is None and api == "openai" and model and input_tokens and output_tokens:
            if model in PRICING["openai"]:
                calculated_cost = (
                    input_tokens * PRICING["openai"][model]["input"] +
                    output_tokens * PRICING["openai"][model]["output"]
                )

        # Create entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "api": api,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": calculated_cost or 0.0,
            "metadata": metadata or {}
        }

        # Add to history
        usage_db["history"].append(entry)

        # Update totals
        usage_db["total_calls"] = usage_db.get("total_calls", 0) + 1
        usage_db["total_cost_usd"] = usage_db.get("total_cost_usd", 0.0) + (calculated_cost or 0.0)
        usage_db["last_updated"] = datetime.now().isoformat()

        # Save
        save_usage_db(usage_db)

        return {
            "status": "tracked",
            "entry": entry
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking API call: {str(e)}")


@router.get("/pricing")
async def get_api_pricing():
    """Get current API pricing information"""
    return {
        "pricing": PRICING,
        "currency": "USD",
        "note": "Prices per 1M tokens for Claude/OpenAI, per API call for YouTube"
    }


@router.get("/estimate")
@limiter.limit("30/minute")
async def estimate_cost(request: Request, 
    api: str,
    model: str,
    input_tokens: int,
    output_tokens: int
):
    """Estimate cost for an API call"""
    try:
        if api not in PRICING:
            raise HTTPException(status_code=400, detail=f"Unknown API: {api}")

        if model not in PRICING[api]:
            raise HTTPException(status_code=400, detail=f"Unknown model: {model}")

        pricing = PRICING[api][model]

        cost = (
            input_tokens * pricing["input"] +
            output_tokens * pricing["output"]
        )

        return {
            "api": api,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": round(cost, 6),
            "pricing": pricing
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error estimating cost: {str(e)}")


@router.get("/summary")
@limiter.limit("60/minute")
async def get_usage_summary(request: Request, ):
    """Get a comprehensive usage summary"""
    try:
        # Get current stats
        current_usage = parse_log_files_for_usage()

        # Load historical data
        usage_db = load_usage_db()

        # Calculate totals
        total_claude_cost = current_usage["claude"]["cost"]
        total_openai_cost = current_usage["openai"]["cost"]
        total_youtube_cost = current_usage["youtube"]["cost"]
        total_cost = total_claude_cost + total_openai_cost + total_youtube_cost

        # Get recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_entries = [
            entry for entry in usage_db.get("history", [])
            if datetime.fromisoformat(entry.get("timestamp", "2020-01-01")) > week_ago
        ]

        recent_cost = sum(entry.get("cost", 0.0) for entry in recent_entries)

        # Cost breakdown percentage
        breakdown_pct = {}
        if total_cost > 0:
            breakdown_pct = {
                "claude": round((total_claude_cost / total_cost) * 100, 1),
                "openai": round((total_openai_cost / total_cost) * 100, 1),
                "youtube": round((total_youtube_cost / total_cost) * 100, 1)
            }

        return {
            "summary": {
                "total_cost_usd": round(total_cost, 4),
                "total_calls": (
                    current_usage["claude"]["calls"] +
                    current_usage["openai"]["calls"] +
                    current_usage["youtube"]["calls"]
                ),
                "last_7_days_cost_usd": round(recent_cost, 4),
                "last_7_days_calls": len(recent_entries)
            },
            "breakdown": current_usage,
            "breakdown_percentage": breakdown_pct,
            "recommendations": get_cost_recommendations(current_usage)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


def get_cost_recommendations(usage: Dict) -> List[str]:
    """Generate cost optimization recommendations"""
    recommendations = []

    # Check if using expensive models
    if usage["claude"]["calls"] > 100:
        recommendations.append(
            "Consider using Claude Haiku for simple tasks (20x cheaper than Opus)"
        )

    if usage["openai"]["calls"] > 100:
        recommendations.append(
            "Review if GPT-4 is needed for all tasks, GPT-3.5-Turbo is 20x cheaper"
        )

    # Check token usage
    if usage["claude"]["input_tokens"] > 1_000_000:
        recommendations.append(
            "High input token usage detected. Consider summarizing inputs or caching."
        )

    if usage["youtube"]["videos_processed"] > 50:
        recommendations.append(
            "Processing many videos. Consider batch processing during off-peak hours."
        )

    # Check total cost
    total_cost = usage["claude"]["cost"] + usage["openai"]["cost"] + usage["youtube"]["cost"]

    if total_cost > 100:
        recommendations.append(
            "Monthly cost exceeds $100. Review usage patterns and optimize API calls."
        )
    elif total_cost > 50:
        recommendations.append(
            "Approaching $50/month. Monitor usage to avoid unexpected costs."
        )

    if not recommendations:
        recommendations.append("Usage is within reasonable limits. No immediate optimizations needed.")

    return recommendations
