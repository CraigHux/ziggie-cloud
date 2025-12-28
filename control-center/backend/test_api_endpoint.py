"""
Test API endpoint for agent stats
Quick test to verify /api/agents/stats returns correct counts
"""

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from api.agents import get_agent_stats, list_all_agents
import asyncio


async def test_api_endpoints():
    """Test API endpoints directly"""

    print("=" * 80)
    print("TESTING API ENDPOINTS")
    print("=" * 80)
    print()

    # Test /api/agents/stats
    print("Testing GET /api/agents/stats...")
    print("-" * 80)

    stats = await get_agent_stats()

    print(f"Total Agents: {stats['total']}")
    print(f"L1 Count: {stats['l1_count']}")
    print(f"L2 Count: {stats['l2_count']}")
    print(f"L3 Count: {stats['l3_count']}")
    print()

    print("Expected vs Actual:")
    print(f"  L1: {stats['actual']['l1']}/{stats['expected']['l1']}")
    print(f"  L2: {stats['actual']['l2']}/{stats['expected']['l2']}")
    print(f"  L3: {stats['actual']['l3']}/{stats['expected']['l3']}")
    print(f"  Total: {stats['actual']['total']}/{stats['expected']['total']}")
    print()

    # Test /api/agents (list all)
    print("Testing GET /api/agents...")
    print("-" * 80)

    all_agents_response = await list_all_agents(level=None, parent=None, search=None, limit=500, offset=0)

    print(f"Total agents returned: {all_agents_response['total']}")
    print(f"Limit: {all_agents_response['limit']}")
    print(f"Offset: {all_agents_response['offset']}")
    print(f"Agents in response: {len(all_agents_response['agents'])}")
    print()

    # Count by level
    by_level = {}
    for agent in all_agents_response['agents']:
        level = agent.get('level', 'unknown')
        by_level[level] = by_level.get(level, 0) + 1

    print("Agents by level:")
    for level in sorted(by_level.keys()):
        print(f"  {level}: {by_level[level]}")
    print()

    # Verify counts
    print("=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    l1_ok = stats['actual']['l1'] == 12
    l2_ok = stats['actual']['l2'] == 144
    l3_expected = 1728
    l3_partial = stats['actual']['l3'] < l3_expected

    print(f"L1 Complete: {'[OK]' if l1_ok else '[FAIL]'} - {stats['actual']['l1']}/12")
    print(f"L2 Complete: {'[OK]' if l2_ok else '[FAIL]'} - {stats['actual']['l2']}/144")
    print(f"L3 Partial: {'[INFO]' if l3_partial else '[OK]'} - {stats['actual']['l3']}/1,728")
    print()

    if l1_ok and l2_ok:
        print("[SUCCESS] API correctly reports 12 L1 + 144 L2 agents")
        print(f"[INFO] L3 agents: {stats['actual']['l3']} documented (target: 1,728)")
        print()
        print("Backend is ready to detect all 1,884 agents when L3 documentation is complete!")
        return True
    else:
        print("[ERROR] API counts do not match expected values")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_api_endpoints())
    sys.exit(0 if result else 1)
