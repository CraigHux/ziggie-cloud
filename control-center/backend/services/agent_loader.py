"""
Agent Loader Service
Load and parse agent definitions from markdown files
"""

from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import re


class AgentLoader:
    """Service for loading agent definitions"""

    def __init__(self):
        self.ai_agents_root = Path("C:/Ziggie/ai-agents")
        self._cache = {
            "l1": None,
            "l2": None,
            "l3": None,
            "last_loaded": None
        }

    def _parse_markdown_file(self, file_path: Path) -> Dict:
        """Parse agent definition from markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')

            # Extract title
            title = ""
            for line in lines:
                if line.startswith('# '):
                    title = line.strip('# ').strip()
                    break

            # Extract sections
            sections = {}
            current_section = None
            section_content = []

            for line in lines:
                if line.startswith('## '):
                    # Save previous section
                    if current_section:
                        sections[current_section] = '\n'.join(section_content)

                    # Start new section
                    current_section = line.strip('# ').strip()
                    section_content = []
                else:
                    if current_section:
                        section_content.append(line)

            # Save last section
            if current_section:
                sections[current_section] = '\n'.join(section_content)

            # Extract specific fields
            role = ""
            objective = ""
            responsibilities = []

            # Look for role
            for key in sections:
                if 'ROLE' in key.upper():
                    role = sections[key].strip().split('\n')[0].strip()
                    break

            # Look for objective
            for key in sections:
                if 'OBJECTIVE' in key.upper():
                    objective = sections[key].strip().split('\n')[0].strip()
                    break

            # Look for responsibilities
            for key in sections:
                if 'RESPONSIBILITIES' in key.upper():
                    resp_content = sections[key]
                    # Extract ### headers
                    for line in resp_content.split('\n'):
                        if line.startswith('### '):
                            responsibilities.append(line.strip('# ').strip())

            return {
                "title": title,
                "role": role,
                "objective": objective,
                "responsibilities": responsibilities,
                "sections": list(sections.keys()),
                "word_count": len(content.split()),
                "line_count": len(lines)
            }

        except Exception as e:
            return {
                "error": str(e),
                "file": str(file_path)
            }

    def load_l1_agents(self, force_reload: bool = False) -> List[Dict]:
        """Load all L1 main agents"""
        if not force_reload and self._cache["l1"]:
            return self._cache["l1"]

        agents = []

        l1_files = [
            ("01_ART_DIRECTOR_AGENT.md", "01_art_director", "Art Director"),
            ("02_CHARACTER_PIPELINE_AGENT.md", "02_character_pipeline", "Character Pipeline"),
            ("03_ENVIRONMENT_PIPELINE_AGENT.md", "03_environment_pipeline", "Environment Pipeline"),
            ("04_GAME_SYSTEMS_DEVELOPER_AGENT.md", "04_game_systems_developer", "Game Systems Developer"),
            ("05_UI_UX_DEVELOPER_AGENT.md", "05_ui_ux_developer", "UI/UX Developer"),
            ("06_CONTENT_DESIGNER_AGENT.md", "06_content_designer", "Content Designer"),
            ("07_INTEGRATION_AGENT.md", "07_integration", "Integration"),
            ("08_QA_TESTING_AGENT.md", "08_qa_testing", "QA Testing"),
            ("09_MIGRATION_AGENT.md", "09_migration", "Migration"),
            ("10_DIRECTOR_AGENT.md", "10_director", "Director"),
            ("11_STORYBOARD_CREATOR_AGENT.md", "11_storyboard_creator", "Storyboard Creator"),
            ("12_COPYWRITER_SCRIPTER_AGENT.md", "12_copywriter_scripter", "Copywriter/Scripter")
        ]

        for filename, agent_id, display_name in l1_files:
            file_path = self.ai_agents_root / filename

            if file_path.exists():
                parsed = self._parse_markdown_file(file_path)

                stat = file_path.stat()

                agents.append({
                    "id": agent_id,
                    "level": "L1",
                    "display_name": display_name,
                    "filename": filename,
                    "path": str(file_path),
                    "exists": True,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "size": stat.st_size,
                    **parsed
                })
            else:
                agents.append({
                    "id": agent_id,
                    "level": "L1",
                    "display_name": display_name,
                    "filename": filename,
                    "exists": False,
                    "error": "File not found"
                })

        self._cache["l1"] = agents
        self._cache["last_loaded"] = datetime.now()

        return agents

    def load_l2_agents(self, force_reload: bool = False) -> List[Dict]:
        """Load all L2 sub-agents from SUB_AGENT_ARCHITECTURE.md"""
        if not force_reload and self._cache["l2"]:
            return self._cache["l2"]

        agents = []
        sub_agent_file = self.ai_agents_root / "SUB_AGENT_ARCHITECTURE.md"

        if not sub_agent_file.exists():
            return agents

        try:
            with open(sub_agent_file, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')

            # Pattern for sub-agents: ### Sub-Agent X.Y: **Name**
            pattern = re.compile(r'###\s+Sub-Agent\s+(\d+)\.(\d+):\s+\*\*(.+?)\*\*')

            current_l1 = None

            for i, line in enumerate(lines):
                # Track which L1 agent section we're in
                if line.startswith('# ') and 'AGENT' in line.upper():
                    match = re.search(r'(\d+)\.', line)
                    if match:
                        current_l1 = match.group(1)

                # Find sub-agent definitions
                match = pattern.search(line)
                if match:
                    l1_num = match.group(1)
                    l2_num = match.group(2)
                    name = match.group(3)

                    agent_id = f"L2.{l1_num}.{l2_num}"

                    # Extract role (usually next line)
                    role = ""
                    if i + 1 < len(lines) and '**Role:**' in lines[i + 1]:
                        role = lines[i + 1].replace('**Role:**', '').strip()

                    # Extract capabilities
                    capabilities = []
                    for j in range(i + 1, min(i + 20, len(lines))):
                        if '**Capabilities:**' in lines[j]:
                            # Read bullet points
                            for k in range(j + 1, min(j + 10, len(lines))):
                                if lines[k].startswith('- '):
                                    capabilities.append(lines[k].strip('- ').strip())
                                elif lines[k].startswith('#'):
                                    break
                            break

                    agents.append({
                        "id": agent_id,
                        "level": "L2",
                        "name": name,
                        "role": role,
                        "parent_l1": l1_num,
                        "capabilities": capabilities,
                        "source": "SUB_AGENT_ARCHITECTURE.md"
                    })

        except Exception as e:
            pass

        self._cache["l2"] = agents
        return agents

    def load_l3_agents(self, force_reload: bool = False) -> List[Dict]:
        """Load all L3 micro-agents from L3_MICRO_AGENT_ARCHITECTURE.md"""
        if not force_reload and self._cache["l3"]:
            return self._cache["l3"]

        agents = []
        l3_file = self.ai_agents_root / "L3_MICRO_AGENT_ARCHITECTURE.md"

        if not l3_file.exists():
            return agents

        try:
            with open(l3_file, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')

            # Pattern for L3 agents: #### L3.X.Y.Z: Name (note: 4 hashes)
            pattern = re.compile(r'####\s+L3\.(\d+)\.(\d+)\.(\d+):\s+(.+)')

            for i, line in enumerate(lines):
                match = pattern.search(line)
                if match:
                    l1_num = match.group(1)
                    l2_num = match.group(2)
                    l3_num = match.group(3)
                    name = match.group(4)

                    agent_id = f"L3.{l1_num}.{l2_num}.{l3_num}"

                    # Extract task (usually next non-empty line)
                    task = ""
                    for j in range(i + 1, min(i + 5, len(lines))):
                        if lines[j].strip() and not lines[j].startswith('#'):
                            task = lines[j].strip()
                            break

                    agents.append({
                        "id": agent_id,
                        "level": "L3",
                        "name": name,
                        "task": task,
                        "parent_l1": l1_num,
                        "parent_l2": f"L2.{l1_num}.{l2_num}",
                        "source": "L3_MICRO_AGENT_ARCHITECTURE.md"
                    })

        except Exception as e:
            pass

        self._cache["l3"] = agents
        return agents

    def get_all_agents(self, force_reload: bool = False) -> Dict[str, List[Dict]]:
        """Get all agents organized by level"""
        return {
            "l1": self.load_l1_agents(force_reload),
            "l2": self.load_l2_agents(force_reload),
            "l3": self.load_l3_agents(force_reload)
        }

    def get_agent_by_id(self, agent_id: str) -> Optional[Dict]:
        """Get a specific agent by ID"""
        all_agents = self.get_all_agents()

        # Search in all levels
        for level_agents in all_agents.values():
            for agent in level_agents:
                if agent.get("id") == agent_id:
                    return agent

        return None

    def get_agent_hierarchy(self, agent_id: str) -> Dict:
        """Get full hierarchy for an agent (parents and children)"""
        agent = self.get_agent_by_id(agent_id)

        if not agent:
            return {"error": "Agent not found"}

        hierarchy = {
            "agent": agent,
            "parent": None,
            "children": []
        }

        level = agent.get("level")
        all_agents = self.get_all_agents()

        if level == "L1":
            # Find L2 children
            l1_num = agent_id.split('_')[0]
            hierarchy["children"] = [
                a for a in all_agents["l2"]
                if a.get("parent_l1") == l1_num
            ]

        elif level == "L2":
            # Find L1 parent
            parent_l1_num = agent.get("parent_l1")
            if parent_l1_num:
                hierarchy["parent"] = next(
                    (a for a in all_agents["l1"] if parent_l1_num in a.get("id", "")),
                    None
                )

            # Find L3 children
            hierarchy["children"] = [
                a for a in all_agents["l3"]
                if a.get("parent_l2") == agent_id
            ]

        elif level == "L3":
            # Find L2 parent
            parent_l2_id = agent.get("parent_l2")
            if parent_l2_id:
                hierarchy["parent"] = next(
                    (a for a in all_agents["l2"] if a.get("id") == parent_l2_id),
                    None
                )

        return hierarchy

    def get_agent_stats(self) -> Dict:
        """Get comprehensive agent statistics"""
        all_agents = self.get_all_agents()

        stats = {
            "total": len(all_agents["l1"]) + len(all_agents["l2"]) + len(all_agents["l3"]),
            "by_level": {
                "L1": len(all_agents["l1"]),
                "L2": len(all_agents["l2"]),
                "L3": len(all_agents["l3"])
            },
            "expected": {
                "L1": 12,
                "L2": 144,
                "L3": 1728,
                "total": 1884
            },
            "completion": {
                "L1": round((len(all_agents["l1"]) / 12) * 100, 1),
                "L2": round((len(all_agents["l2"]) / 144) * 100, 1),
                "L3": round((len(all_agents["l3"]) / 1728) * 100, 1)
            }
        }

        # Distribution by L1 parent
        distribution = {}
        for l1_agent in all_agents["l1"]:
            agent_id = l1_agent.get("id")
            l1_num = agent_id.split('_')[0]

            distribution[agent_id] = {
                "name": l1_agent.get("display_name", agent_id),
                "l2_count": len([a for a in all_agents["l2"] if a.get("parent_l1") == l1_num]),
                "l3_count": len([a for a in all_agents["l3"] if a.get("parent_l1") == l1_num])
            }

        stats["distribution"] = distribution

        return stats

    def search_agents(self, query: str) -> List[Dict]:
        """Search agents by name, role, or other attributes"""
        all_agents = self.get_all_agents()
        query_lower = query.lower()

        results = []

        for level_agents in all_agents.values():
            for agent in level_agents:
                # Search in various fields
                searchable = [
                    str(agent.get("name", "")),
                    str(agent.get("title", "")),
                    str(agent.get("role", "")),
                    str(agent.get("display_name", "")),
                    str(agent.get("objective", ""))
                ]

                if any(query_lower in field.lower() for field in searchable):
                    results.append(agent)

        return results

    def validate_agent_structure(self) -> Dict:
        """Validate agent structure and relationships"""
        all_agents = self.get_all_agents()
        validation = {
            "valid": True,
            "issues": [],
            "warnings": []
        }

        # Check L1 agents
        if len(all_agents["l1"]) < 12:
            validation["warnings"].append(f"Only {len(all_agents['l1'])}/12 L1 agents found")

        # Check for missing files
        for agent in all_agents["l1"]:
            if not agent.get("exists"):
                validation["issues"].append(f"L1 agent file missing: {agent.get('filename')}")
                validation["valid"] = False

        # Check L2 agent references
        for l2_agent in all_agents["l2"]:
            parent_l1 = l2_agent.get("parent_l1")
            if parent_l1:
                l1_exists = any(
                    parent_l1 in agent.get("id", "")
                    for agent in all_agents["l1"]
                )
                if not l1_exists:
                    validation["issues"].append(
                        f"L2 agent {l2_agent.get('id')} references non-existent L1 parent"
                    )

        # Check L3 agent references
        for l3_agent in all_agents["l3"]:
            parent_l2 = l3_agent.get("parent_l2")
            if parent_l2:
                l2_exists = any(
                    agent.get("id") == parent_l2
                    for agent in all_agents["l2"]
                )
                if not l2_exists:
                    validation["issues"].append(
                        f"L3 agent {l3_agent.get('id')} references non-existent L2 parent"
                    )

        if validation["issues"]:
            validation["valid"] = False

        return validation

    def clear_cache(self):
        """Clear the agent cache"""
        self._cache = {
            "l1": None,
            "l2": None,
            "l3": None,
            "last_loaded": None
        }


# Global instance
agent_loader = AgentLoader()
