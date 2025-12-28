"""
Ziggie Bedrock Integration Module
Provides easy access to AWS Bedrock LLMs for game content generation.

Usage:
    from ziggie_bedrock import BedrockClient

    client = BedrockClient()
    response = client.chat("Generate a magic sword description")
    print(response)
"""

import boto3
import json
from typing import Optional, List, Dict, Any

class BedrockClient:
    """AWS Bedrock client for Ziggie ecosystem."""

    # Available models with EU inference profiles
    MODELS = {
        "nova-micro": "eu.amazon.nova-micro-v1:0",
        "nova-lite": "eu.amazon.nova-lite-v1:0",
        "nova-pro": "eu.amazon.nova-pro-v1:0",
        "claude-haiku": "eu.anthropic.claude-haiku-4-5-20251001-v1:0",
        "claude-sonnet": "eu.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "claude-opus": "eu.anthropic.claude-opus-4-5-20251101-v1:0",
    }

    def __init__(self, region: str = "eu-north-1", default_model: str = "nova-lite"):
        """Initialize Bedrock client.

        Args:
            region: AWS region (default: eu-north-1)
            default_model: Default model to use (nova-lite, nova-pro, claude-sonnet, etc.)
        """
        self.region = region
        self.default_model = default_model
        self.client = boto3.client("bedrock-runtime", region_name=region)

    def chat(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Send a chat message and get a response.

        Args:
            prompt: User message
            model: Model to use (defaults to self.default_model)
            max_tokens: Maximum tokens in response
            temperature: Creativity (0.0-1.0)
            system_prompt: Optional system prompt

        Returns:
            Response text from the model
        """
        model_name = model or self.default_model
        model_id = self.MODELS.get(model_name, model_name)

        messages = [{"role": "user", "content": [{"text": prompt}]}]

        kwargs = {
            "modelId": model_id,
            "messages": messages,
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature,
            },
        }

        if system_prompt:
            kwargs["system"] = [{"text": system_prompt}]

        response = self.client.converse(**kwargs)

        return response["output"]["message"]["content"][0]["text"]

    def generate_item(self, name: str, rarity: str = "Rare") -> Dict[str, Any]:
        """Generate a game item description.

        Args:
            name: Item name
            rarity: Item rarity (Common, Uncommon, Rare, Epic, Legendary)

        Returns:
            Dictionary with item details
        """
        prompt = f"""Generate a game item for Meow Ping RTS:
Name: {name}
Rarity: {rarity}

Return JSON with: name, rarity, description, stats (attack, defense, speed bonuses), special_ability, flavor_text"""

        response = self.chat(prompt, model="nova-pro", max_tokens=500)

        # Try to parse as JSON
        try:
            # Find JSON in response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except json.JSONDecodeError:
            pass

        return {"raw_response": response}

    def generate_dialogue(self, character: str, situation: str) -> List[str]:
        """Generate character dialogue lines.

        Args:
            character: Character name/type
            situation: Context for dialogue

        Returns:
            List of dialogue lines
        """
        prompt = f"""Generate 5 dialogue lines for a {character} in Meow Ping RTS.
Situation: {situation}
Style: Medieval fantasy with cat warrior theme.

Return as JSON array of strings."""

        response = self.chat(prompt, model="nova-lite", max_tokens=300)

        try:
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except json.JSONDecodeError:
            pass

        return [response]

    def generate_quest(self, title: str, difficulty: str = "Medium") -> Dict[str, Any]:
        """Generate a quest description.

        Args:
            title: Quest title
            difficulty: Quest difficulty

        Returns:
            Dictionary with quest details
        """
        prompt = f"""Design a quest for Meow Ping RTS:
Title: {title}
Difficulty: {difficulty}

Return JSON with: title, description, objectives (array), rewards, estimated_time, story_context"""

        response = self.chat(prompt, model="nova-pro", max_tokens=700)

        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except json.JSONDecodeError:
            pass

        return {"raw_response": response}

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics (placeholder for future implementation)."""
        return {
            "region": self.region,
            "default_model": self.default_model,
            "available_models": list(self.MODELS.keys()),
        }


# Quick test
if __name__ == "__main__":
    client = BedrockClient()

    print("=== Ziggie Bedrock Test ===")
    print()

    # Test basic chat
    response = client.chat("Say hello to the Ziggie development team in one sentence.")
    print(f"Chat response: {response}")
    print()

    # Test item generation
    item = client.generate_item("Whisker Blade", "Epic")
    print(f"Generated item: {json.dumps(item, indent=2)}")
