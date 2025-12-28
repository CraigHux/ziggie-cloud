"""
Knowledge Writer - Writes extracted insights to agent KB files
"""

from pathlib import Path
from datetime import datetime
import json
import re

from config import Config
from logger import logger


class KnowledgeWriter:
    """Writes insights to agent knowledge base files"""

    def __init__(self):
        self.kb_root = Config.KB_PATH.parent / "ai-agents"
        self.routing_rules = self._load_routing_rules()

    def _load_routing_rules(self):
        """Load knowledge routing rules"""
        routing_file = Config.METADATA_PATH / "routing-rules.json"

        if routing_file.exists():
            with open(routing_file, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Routing rules not found: {routing_file}")
            return {}

    def write_insights(self, insights, video_data, creator_info):
        """
        Write insights to appropriate agent KB files

        Args:
            insights: Extracted insights dict
            video_data: Video metadata
            creator_info: Creator information

        Returns:
            List of files written
        """
        written_files = []

        target_agents = insights.get('target_agents', [])
        knowledge_category = insights.get('knowledge_category', 'general')

        logger.info(f"Writing insights to {len(target_agents)} agents")

        for agent_id in target_agents:
            try:
                file_path = self._write_to_agent(
                    agent_id=agent_id,
                    insights=insights,
                    video_data=video_data,
                    creator_info=creator_info,
                    knowledge_category=knowledge_category
                )

                if file_path:
                    written_files.append(str(file_path))
                    logger.info(f"  -> Written to: {agent_id}")

            except Exception as e:
                logger.error(f"Failed to write to {agent_id}: {e}")

        return written_files

    def _write_to_agent(self, agent_id, insights, video_data, creator_info, knowledge_category):
        """Write insights to a specific agent's KB"""

        # Determine agent directory
        agent_dir = self._get_agent_directory(agent_id)

        if not agent_dir:
            logger.warning(f"Could not find directory for agent: {agent_id}")
            return None

        # Create category subdirectory
        category_dir = agent_dir / knowledge_category
        category_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        creator_slug = self._slugify(creator_info.get('name', 'unknown'))
        timestamp = datetime.now().strftime('%Y%m%d')
        video_id = video_data.get('video_id', 'unknown')

        filename = f"{creator_slug}-{video_id}-{timestamp}.md"
        file_path = category_dir / filename

        # Generate markdown content
        content = self._generate_markdown(
            insights=insights,
            video_data=video_data,
            creator_info=creator_info
        )

        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.debug(f"Wrote {len(content)} characters to {file_path}")

        return file_path

    def _get_agent_directory(self, agent_id):
        """Get the directory for an agent's knowledge base"""

        # Parse agent ID (e.g., "L1.2-character-pipeline")
        match = re.match(r'L(\d+)\.(\d+)', agent_id)

        if not match:
            logger.warning(f"Invalid agent ID format: {agent_id}")
            return None

        level = int(match.group(1))

        if level == 1:
            # L1 agents have their own directories
            agent_name = agent_id.split('-', 1)[1] if '-' in agent_id else agent_id
            agent_dir = self.kb_root / f"{agent_name}"

        elif level == 2:
            # L2 agents are subdirectories of L1
            # L2.2.1 -> L1.2/sub-agents/L2.2.1
            l1_id = f"L1.{agent_id.split('.')[1]}"
            l1_dir = self._get_agent_directory(l1_id)
            if l1_dir:
                agent_dir = l1_dir / "sub-agents" / agent_id
            else:
                return None

        elif level == 3:
            # L3 agents are subdirectories of L2
            # L3.2.1.1 -> L1.2/sub-agents/L2.2.1/micro-agents/L3.2.1.1
            parts = agent_id.split('.')
            l2_id = f"L2.{parts[1]}.{parts[2]}"
            l2_dir = self._get_agent_directory(l2_id)
            if l2_dir:
                agent_dir = l2_dir / "micro-agents" / agent_id
            else:
                return None
        else:
            logger.warning(f"Unsupported agent level: {level}")
            return None

        # Create directory if it doesn't exist
        agent_dir.mkdir(parents=True, exist_ok=True)

        return agent_dir

    def _generate_markdown(self, insights, video_data, creator_info):
        """Generate markdown content for knowledge entry"""

        md = []

        # Header
        md.append(f"# {video_data.get('title', 'Untitled')}")
        md.append("")
        md.append(f"**Source:** {creator_info.get('name', 'Unknown')}")
        md.append(f"**Video ID:** {video_data.get('video_id', 'N/A')}")
        md.append(f"**URL:** {video_data.get('url', 'N/A')}")
        md.append(f"**Added:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        md.append(f"**Confidence:** {insights.get('confidence_score', 0)}%")
        md.append("")
        md.append("---")
        md.append("")

        # Primary Topic
        md.append(f"## Topic: {insights.get('primary_topic', 'General')}")
        md.append("")

        # Key Insights
        key_insights = insights.get('key_insights', [])
        if key_insights:
            md.append("## Key Insights")
            md.append("")
            for i, insight in enumerate(key_insights, 1):
                md.append(f"{i}. {insight}")
            md.append("")

        # Technical Settings
        technical_settings = insights.get('technical_settings', {})
        if technical_settings:
            md.append("## Technical Settings")
            md.append("")
            md.append("```")
            for key, value in technical_settings.items():
                md.append(f"{key}: {value}")
            md.append("```")
            md.append("")

        # Workflow Steps
        workflow_steps = insights.get('workflow_steps', [])
        if workflow_steps:
            md.append("## Workflow Steps")
            md.append("")
            for step in workflow_steps:
                md.append(f"- {step}")
            md.append("")

        # Code Snippets
        code_snippets = insights.get('code_snippets', [])
        if code_snippets:
            md.append("## Code Examples")
            md.append("")
            for snippet in code_snippets:
                md.append("```")
                md.append(snippet)
                md.append("```")
                md.append("")

        # Tools Mentioned
        tools = insights.get('tools_mentioned', [])
        if tools:
            md.append("## Tools & Technologies")
            md.append("")
            md.append(", ".join(tools))
            md.append("")

        # Key Takeaways
        takeaways = insights.get('key_takeaways', [])
        if takeaways:
            md.append("## Key Takeaways")
            md.append("")
            for takeaway in takeaways:
                md.append(f"- {takeaway}")
            md.append("")

        # Timestamp References
        timestamps = insights.get('timestamp_references', [])
        if timestamps:
            md.append("## Timestamp References")
            md.append("")
            for ts in timestamps:
                md.append(f"- {ts}")
            md.append("")

        # Metadata
        md.append("---")
        md.append("")
        md.append("## Metadata")
        md.append("")
        md.append(f"- **Category:** {insights.get('knowledge_category', 'general')}")
        md.append(f"- **Model:** {insights.get('model', 'unknown')}")
        md.append(f"- **Analyzed:** {insights.get('analyzed_at', 'N/A')}")
        md.append("")

        return "\n".join(md)

    def _slugify(self, text):
        """Convert text to URL-friendly slug"""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')


def test_knowledge_writer():
    """Test the knowledge writer with mock data"""

    writer = KnowledgeWriter()

    # Mock data
    insights = {
        "primary_topic": "ComfyUI Workflows",
        "key_insights": [
            "IP-Adapter locks BOTH face AND colors at weights above 0.70",
            "Reduce to 0.40 for equipment variations"
        ],
        "technical_settings": {
            "denoise": "0.40",
            "ip_adapter_weight": "0.40",
            "controlnet_strength": "0.60"
        },
        "workflow_steps": [
            "Set Denoise to 0.40",
            "Set IP-Adapter to 0.40",
            "Set ControlNet to 0.60"
        ],
        "target_agents": ["L1.2-character-pipeline"],
        "knowledge_category": "comfyui-workflows",
        "confidence_score": 90,
        "model": "claude-sonnet-4-20250514",
        "analyzed_at": datetime.now().isoformat(),
        "tools_mentioned": ["ComfyUI", "IP-Adapter", "ControlNet"],
        "key_takeaways": [
            "Lower IP-Adapter weights enable color flexibility"
        ]
    }

    video_data = {
        "video_id": "TEST123",
        "title": "ComfyUI IP-Adapter Deep Dive",
        "url": "https://youtube.com/watch?v=TEST123"
    }

    creator_info = {
        "name": "InstaSD",
        "focus": "ComfyUI"
    }

    files = writer.write_insights(insights, video_data, creator_info)

    print(f"Written {len(files)} files:")
    for file in files:
        print(f"  - {file}")


if __name__ == "__main__":
    test_knowledge_writer()
