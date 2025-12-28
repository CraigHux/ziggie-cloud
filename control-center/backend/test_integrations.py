"""
Test integration endpoints
"""
import sys
sys.path.insert(0, '.')

print("=" * 80)
print("CONTROL CENTER INTEGRATION TEST")
print("=" * 80)

# Test 1: Agent Loader
print("\n[1/6] Testing Agent Loader...")
try:
    from services.agent_loader import agent_loader
    stats = agent_loader.get_agent_stats()
    print(f"   OK Total agents: {stats['total']}")
    print(f"   OK L1: {stats['by_level']['L1']}")
    print(f"   OK L2: {stats['by_level']['L2']}")
    print(f"   OK L3: {stats['by_level']['L3']}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 2: Knowledge Base Manager
print("\n[2/6] Testing Knowledge Base Manager...")
try:
    from services.kb_manager import kb_manager
    stats = kb_manager.get_kb_stats()
    print(f"   OK Total creators: {stats['creators']['total']}")
    print(f"   OK Total files: {stats['files']['total']}")
    print(f"   OK Storage: {stats['storage']['total_size_mb']} MB")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 3: Service Registry
print("\n[3/6] Testing Service Registry...")
try:
    from services.service_registry import get_all_services
    services = get_all_services()
    print(f"   OK Total services: {len(services)}")
    print(f"   OK Services: {', '.join(list(services.keys())[:3])}...")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 4: API Imports
print("\n[4/6] Testing API Imports...")
try:
    from api import knowledge, agents, comfyui, projects, usage, docker
    print(f"   OK knowledge API imported")
    print(f"   OK agents API imported")
    print(f"   OK comfyui API imported")
    print(f"   OK projects API imported")
    print(f"   OK usage API imported")
    print(f"   OK docker API imported")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 5: Load Agent Details
print("\n[5/6] Testing Agent Details...")
try:
    agent = agent_loader.get_agent_by_id("01_art_director")
    if agent:
        print(f"   OK Agent found: {agent.get('display_name')}")
        print(f"   OK Role: {agent.get('role', 'N/A')[:50]}...")
    else:
        print(f"   ERROR Agent not found")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 6: Creator Database
print("\n[6/6] Testing Creator Database...")
try:
    db = kb_manager.load_creator_database()
    creators = db.get('creators', [])
    if creators:
        print(f"   OK First creator: {creators[0].get('name')}")
        print(f"   OK Priority: {creators[0].get('priority')}")
    else:
        print(f"   ERROR No creators found")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 80)
print("INTEGRATION TEST COMPLETE")
print("=" * 80)
