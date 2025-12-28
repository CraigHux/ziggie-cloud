"""
Knowledge Base Manager
Centralized service for KB operations
"""

from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json
import subprocess
import glob


class KnowledgeBaseManager:
    """Manager for Knowledge Base operations"""

    def __init__(self):
        self.kb_root = Path("C:/meowping-rts/ai-agents/knowledge-base")
        self.ai_agents_root = Path("C:/meowping-rts/ai-agents")
        self.creator_db_path = self.kb_root / "metadata" / "creator-database.json"
        self.manage_py = self.kb_root / "manage.py"

    def load_creator_database(self) -> Dict:
        """Load the creator database"""
        try:
            if not self.creator_db_path.exists():
                return {
                    "metadata": {"total_creators": 0, "status": "not_found"},
                    "creators": []
                }

            with open(self.creator_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {
                "metadata": {"total_creators": 0, "status": "error", "error": str(e)},
                "creators": []
            }

    def get_creator_by_id(self, creator_id: str) -> Optional[Dict]:
        """Get a specific creator by ID"""
        db = self.load_creator_database()
        creators = db.get("creators", [])
        return next((c for c in creators if c.get("id") == creator_id), None)

    def get_creators_by_priority(self, priority: str) -> List[Dict]:
        """Get creators filtered by priority"""
        db = self.load_creator_database()
        creators = db.get("creators", [])
        return [c for c in creators if c.get("priority") == priority]

    def scan_kb_directories(self) -> Dict[str, List[Path]]:
        """Scan knowledge base directories for files"""
        kb_structure = {
            "L1_directories": [],
            "agent_directories": [],
            "markdown_files": [],
            "json_files": []
        }

        # Scan L1 directories in knowledge-base
        if self.kb_root.exists():
            for item in self.kb_root.iterdir():
                if item.is_dir() and item.name.startswith("L1-"):
                    kb_structure["L1_directories"].append(item)

        # Scan agent directories
        agent_dirs = [
            "art-director",
            "character-pipeline",
            "environment-pipeline",
            "game-systems",
            "ui-ux",
            "content-designer",
            "integration",
            "qa-testing"
        ]

        for agent_dir in agent_dirs:
            dir_path = self.ai_agents_root / "ai-agents" / agent_dir
            if dir_path.exists():
                kb_structure["agent_directories"].append(dir_path)

        # Scan for markdown files
        for directory in kb_structure["L1_directories"] + kb_structure["agent_directories"]:
            kb_structure["markdown_files"].extend(directory.rglob("*.md"))
            kb_structure["json_files"].extend(directory.rglob("*.json"))

        return kb_structure

    def get_kb_stats(self) -> Dict:
        """Get comprehensive KB statistics"""
        structure = self.scan_kb_directories()
        db = self.load_creator_database()

        stats = {
            "creators": {
                "total": db.get("metadata", {}).get("total_creators", 0),
                "by_priority": {}
            },
            "directories": {
                "L1": len(structure["L1_directories"]),
                "agent": len(structure["agent_directories"])
            },
            "files": {
                "markdown": len(structure["markdown_files"]),
                "json": len(structure["json_files"]),
                "total": len(structure["markdown_files"]) + len(structure["json_files"])
            },
            "storage": {
                "total_size_bytes": 0,
                "total_size_mb": 0
            }
        }

        # Count creators by priority
        for creator in db.get("creators", []):
            priority = creator.get("priority", "unknown")
            stats["creators"]["by_priority"][priority] = \
                stats["creators"]["by_priority"].get(priority, 0) + 1

        # Calculate total size
        total_size = 0
        for file_path in structure["markdown_files"] + structure["json_files"]:
            try:
                total_size += file_path.stat().st_size
            except:
                pass

        stats["storage"]["total_size_bytes"] = total_size
        stats["storage"]["total_size_mb"] = round(total_size / (1024 * 1024), 2)

        return stats

    def find_kb_files_for_agent(self, agent_id: str) -> List[Dict]:
        """Find all KB files associated with an agent"""
        # Map agent IDs to directory names
        agent_mapping = {
            "01_art_director": ["art-director", "L1-art-director"],
            "02_character_pipeline": ["character-pipeline", "L1-character-pipeline"],
            "03_environment_pipeline": ["environment-pipeline", "L1-environment-pipeline"],
            "04_game_systems_developer": ["game-systems", "L1-game-systems"],
            "05_ui_ux_developer": ["ui-ux", "L1-ui-ux"],
            "06_content_designer": ["content-designer", "L1-content-designer"],
            "07_integration": ["integration", "L1-integration"],
            "08_qa_testing": ["qa-testing", "L1-qa-testing"]
        }

        directories = agent_mapping.get(agent_id, [])
        files = []

        for dir_name in directories:
            # Check in ai-agents
            agent_path = self.ai_agents_root / "ai-agents" / dir_name
            if agent_path.exists():
                for md_file in agent_path.rglob("*.md"):
                    files.append({
                        "path": str(md_file),
                        "name": md_file.name,
                        "category": md_file.parent.name,
                        "location": "ai-agents",
                        "size": md_file.stat().st_size,
                        "modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                    })

            # Check in knowledge-base
            kb_path = self.kb_root / dir_name
            if kb_path.exists():
                for md_file in kb_path.rglob("*.md"):
                    files.append({
                        "path": str(md_file),
                        "name": md_file.name,
                        "category": md_file.parent.name,
                        "location": "knowledge-base",
                        "size": md_file.stat().st_size,
                        "modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                    })

        return files

    def search_kb_content(self, query: str, agent_filter: Optional[str] = None) -> List[Dict]:
        """Search KB content for a query"""
        structure = self.scan_kb_directories()
        results = []

        query_lower = query.lower()

        for md_file in structure["markdown_files"]:
            try:
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                if query_lower in content.lower():
                    # Count occurrences
                    count = content.lower().count(query_lower)

                    # Find context (first occurrence)
                    lines = content.split('\n')
                    context_line = ""
                    for line in lines:
                        if query_lower in line.lower():
                            context_line = line.strip()
                            break

                    results.append({
                        "file": str(md_file),
                        "name": md_file.name,
                        "occurrences": count,
                        "context": context_line[:200],
                        "size": md_file.stat().st_size,
                        "modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                    })
            except Exception:
                continue

        # Sort by number of occurrences
        results.sort(key=lambda x: x["occurrences"], reverse=True)

        return results

    def trigger_scan(
        self,
        creator_id: Optional[str] = None,
        priority: Optional[str] = None,
        force: bool = False
    ) -> Dict:
        """Trigger a KB scan using manage.py"""
        if not self.manage_py.exists():
            return {
                "success": False,
                "error": f"manage.py not found at {self.manage_py}"
            }

        # Build command
        cmd = ["python", str(self.manage_py), "scan"]

        if creator_id:
            cmd.extend(["--creator", creator_id])
        elif priority:
            cmd.extend(["--priority", priority])

        if force:
            cmd.append("--force")

        try:
            # Start process
            result = subprocess.Popen(
                cmd,
                cwd=str(self.kb_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            return {
                "success": True,
                "pid": result.pid,
                "command": " ".join(cmd),
                "message": "Scan started successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_recent_insights(self, limit: int = 10) -> List[Dict]:
        """Get recently created insight files"""
        structure = self.scan_kb_directories()
        files_with_time = []

        for md_file in structure["markdown_files"]:
            try:
                stat = md_file.stat()
                files_with_time.append({
                    "file": str(md_file),
                    "name": md_file.name,
                    "modified": datetime.fromtimestamp(stat.st_mtime),
                    "modified_iso": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "size": stat.st_size
                })
            except Exception:
                continue

        # Sort by modified time (newest first)
        files_with_time.sort(key=lambda x: x["modified"], reverse=True)

        return files_with_time[:limit]

    def analyze_kb_health(self) -> Dict:
        """Analyze KB health and provide recommendations"""
        stats = self.get_kb_stats()
        db = self.load_creator_database()

        health = {
            "status": "healthy",
            "issues": [],
            "warnings": [],
            "recommendations": []
        }

        # Check if creators are configured
        if stats["creators"]["total"] == 0:
            health["status"] = "error"
            health["issues"].append("No creators configured in database")

        # Check if any content exists
        if stats["files"]["total"] == 0:
            health["status"] = "warning"
            health["warnings"].append("No knowledge base files found - needs initial scan")
            health["recommendations"].append("Run a manual scan to populate the knowledge base")

        # Check for recent activity
        recent_files = self.get_recent_insights(limit=1)
        if recent_files:
            latest = recent_files[0]
            days_old = (datetime.now() - latest["modified"]).days

            if days_old > 7:
                health["warnings"].append(f"No new insights in {days_old} days")
                health["recommendations"].append("Consider running a manual scan or checking scheduler")

        # Check critical creators
        critical_creators = self.get_creators_by_priority("critical")
        if len(critical_creators) == 0:
            health["warnings"].append("No critical priority creators configured")

        # Check storage
        if stats["storage"]["total_size_mb"] > 1000:
            health["warnings"].append(f"KB size is {stats['storage']['total_size_mb']} MB")
            health["recommendations"].append("Consider archiving old insights")

        return health

    def get_creator_stats(self, creator_id: str) -> Dict:
        """Get statistics for a specific creator"""
        creator = self.get_creator_by_id(creator_id)

        if not creator:
            return {
                "found": False,
                "error": "Creator not found"
            }

        # Find related files
        structure = self.scan_kb_directories()
        related_files = []

        for md_file in structure["markdown_files"]:
            if creator_id in str(md_file).lower():
                related_files.append({
                    "file": str(md_file),
                    "name": md_file.name,
                    "size": md_file.stat().st_size,
                    "modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                })

        return {
            "found": True,
            "creator": creator,
            "file_count": len(related_files),
            "files": related_files,
            "agents_served": len(creator.get("primary_agents", [])) + len(creator.get("sub_agents", []))
        }


# Global instance
kb_manager = KnowledgeBaseManager()
