"""
Test script to verify agent detection for 12x12x12 structure
Tests that backend can detect all L1, L2, and L3 agents
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

from services.agent_loader import agent_loader
from api.agents import load_l1_agents, load_l2_agents, load_l3_agents


def test_agent_detection():
    """Test that all agents are detected correctly"""

    print("=" * 80)
    print("ZIGGIE AGENT DETECTION TEST - 12x12x12 Structure")
    print("=" * 80)
    print()

    # Test L1 Agents
    print("Testing L1 Agent Detection...")
    print("-" * 80)
    l1_agents = load_l1_agents()
    print(f"L1 Agents Found: {len(l1_agents)}/12 expected")

    for agent in l1_agents:
        status = "[OK]" if agent.get("exists") or not agent.get("error") else "[FAIL]"
        name = agent.get("name", agent.get("display_name", agent.get("filename", "Unknown")))
        print(f"  {status} {agent['id']}: {name}")
        if agent.get("error"):
            print(f"    ERROR: {agent['error']}")

    print()

    # Test L2 Agents
    print("Testing L2 Agent Detection...")
    print("-" * 80)
    l2_agents = load_l2_agents()
    print(f"L2 Agents Found: {len(l2_agents)}/144 expected")

    # Count by L1 parent
    l2_by_l1 = {}
    for agent in l2_agents:
        parent = agent.get("parent_l1", "unknown")
        l2_by_l1[parent] = l2_by_l1.get(parent, 0) + 1

    print("\nL2 Distribution by L1 Parent:")
    for l1_num in sorted(l2_by_l1.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        count = l2_by_l1[l1_num]
        status = "[OK]" if count == 12 else "[WARN]"
        print(f"  {status} L1.{l1_num}: {count}/12 L2 agents")

    print()

    # Test L3 Agents
    print("Testing L3 Agent Detection...")
    print("-" * 80)
    l3_agents = load_l3_agents()
    print(f"L3 Agents Found: {len(l3_agents)}/1,728 expected")

    # Count by L1 parent
    l3_by_l1 = {}
    for agent in l3_agents:
        parent = agent.get("parent_l1", "unknown")
        l3_by_l1[parent] = l3_by_l1.get(parent, 0) + 1

    print("\nL3 Distribution by L1 Parent:")
    for l1_num in sorted(l3_by_l1.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        count = l3_by_l1[l1_num]
        expected = 144  # 12 L2 x 12 L3
        status = "[OK]" if count == expected else "[PARTIAL]"
        print(f"  {status} L1.{l1_num}: {count}/{expected} L3 agents")

    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    total_found = len(l1_agents) + len(l2_agents) + len(l3_agents)
    total_expected = 1884  # 12 + 144 + 1,728

    print(f"L1 Agents: {len(l1_agents)}/12 ({len(l1_agents)/12*100:.1f}% complete)")
    print(f"L2 Agents: {len(l2_agents)}/144 ({len(l2_agents)/144*100:.1f}% complete)")
    print(f"L3 Agents: {len(l3_agents)}/1,728 ({len(l3_agents)/1728*100:.1f}% complete)")
    print(f"TOTAL: {total_found}/1,884 agents ({total_found/total_expected*100:.1f}% complete)")
    print()

    # Status
    if len(l1_agents) == 12 and len(l2_agents) == 144:
        print("[SUCCESS] L1 and L2 layers COMPLETE!")
    else:
        print("[WARN] L1 and/or L2 layers incomplete")

    if len(l3_agents) == 1728:
        print("[SUCCESS] L3 layer COMPLETE!")
    else:
        print(f"[INFO] L3 layer in progress: {1728 - len(l3_agents)} agents remaining")

    print()
    print("=" * 80)

    return {
        "l1_count": len(l1_agents),
        "l2_count": len(l2_agents),
        "l3_count": len(l3_agents),
        "total_count": total_found,
        "l1_complete": len(l1_agents) == 12,
        "l2_complete": len(l2_agents) == 144,
        "l3_complete": len(l3_agents) == 1728
    }


def test_agent_loader_service():
    """Test the agent_loader service"""

    print("\n" + "=" * 80)
    print("TESTING AGENT LOADER SERVICE")
    print("=" * 80)
    print()

    # Get stats
    stats = agent_loader.get_agent_stats()

    print(f"Total Agents: {stats['total']}")
    print(f"By Level:")
    print(f"  L1: {stats['by_level']['L1']}")
    print(f"  L2: {stats['by_level']['L2']}")
    print(f"  L3: {stats['by_level']['L3']}")
    print()

    print(f"Expected:")
    print(f"  L1: {stats['expected']['L1']}")
    print(f"  L2: {stats['expected']['L2']}")
    print(f"  L3: {stats['expected']['L3']}")
    print(f"  Total: {stats['expected']['total']}")
    print()

    print(f"Completion:")
    print(f"  L1: {stats['completion']['L1']}%")
    print(f"  L2: {stats['completion']['L2']}%")
    print(f"  L3: {stats['completion']['L3']}%")
    print()

    # Validate
    validation = agent_loader.validate_agent_structure()
    print(f"Validation Status: {'[VALID]' if validation['valid'] else '[INVALID]'}")

    if validation['warnings']:
        print("\nWarnings:")
        for warning in validation['warnings']:
            print(f"  [WARN] {warning}")

    if validation['issues']:
        print("\nIssues:")
        for issue in validation['issues']:
            print(f"  [ERROR] {issue}")

    print()

    return stats


if __name__ == "__main__":
    # Run tests
    api_results = test_agent_detection()
    service_stats = test_agent_loader_service()

    # Exit with appropriate code
    if api_results['l1_complete'] and api_results['l2_complete']:
        print("[SUCCESS] Backend successfully detects L1 and L2 agents!")
        if api_results['l3_complete']:
            print("[SUCCESS] All 1,884 agents detected - COMPLETE!")
            sys.exit(0)
        else:
            print(f"[INFO] L3 layer partially complete: {api_results['l3_count']}/1,728 agents")
            sys.exit(0)  # Still success - partial L3 is expected
    else:
        print("[ERROR] Backend agent detection has issues")
        sys.exit(1)
