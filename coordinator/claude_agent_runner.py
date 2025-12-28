#!/usr/bin/env python3
"""
Claude Agent Runner
Executes agent tasks using Anthropic SDK
This allows spawned agents to do REAL work (not simulation)
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

try:
    from anthropic import Anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
    sys.exit(1)


def update_status(status_file: Path, **updates):
    """Update agent status file"""
    try:
        if status_file.exists():
            status = json.loads(status_file.read_text())
        else:
            status = {}

        status.update(updates)
        status['last_updated'] = datetime.now().isoformat()
        status_file.write_text(json.dumps(status, indent=2))
    except Exception as e:
        print(f"Warning: Could not update status: {e}", file=sys.stderr)


def main():
    # Get configuration from environment variables
    agent_id = os.getenv("AGENT_ID", "unknown")
    agent_name = os.getenv("AGENT_NAME", "Unknown Agent")
    agent_type = os.getenv("AGENT_TYPE", "L2")
    model = os.getenv("MODEL", "haiku")
    working_dir = Path(os.getenv("AGENT_WORKING_DIR", "."))

    print(f"=" * 80)
    print(f"AGENT STARTING: {agent_id} - {agent_name}")
    print(f"Type: {agent_type} | Model: {model}")
    print(f"Working Directory: {working_dir}")
    print(f"=" * 80)
    print()

    # Read prompt from file
    prompt_file = working_dir / "prompt.txt"
    if not prompt_file.exists():
        print(f"ERROR: Prompt file not found: {prompt_file}", file=sys.stderr)
        sys.exit(1)

    prompt = prompt_file.read_text(encoding='utf-8')
    print(f"Prompt loaded: {len(prompt)} characters")
    print()

    # Get API key from environment or let SDK find it
    api_key = os.getenv("ANTHROPIC_API_KEY")

    # Map model name to Anthropic model ID
    model_map = {
        "haiku": "claude-3-5-haiku-20241022",
        "sonnet": "claude-3-5-sonnet-20241022",  # Try current version
        "sonnet-legacy": "claude-3-5-sonnet-20240620",  # Fallback to earlier stable version
        "opus": "claude-3-opus-20240229"  # Use stable Opus 3
    }
    model_id = model_map.get(model, model)

    # Update status to working
    status_file = working_dir / "status.json"
    update_status(status_file, status="working", progress=10)

    # Initialize Anthropic client
    # If api_key is None, SDK will try to find it from default locations
    try:
        client = Anthropic(api_key=api_key) if api_key else Anthropic()
    except Exception as e:
        print(f"ERROR: Could not initialize Anthropic client: {e}", file=sys.stderr)
        print("ANTHROPIC_API_KEY not set and SDK could not find API key", file=sys.stderr)
        sys.exit(1)

    print(f"Starting Claude agent with model: {model_id}")
    print("-" * 80)
    print()

    try:
        # Create message using Anthropic SDK
        update_status(status_file, progress=20)

        message = client.messages.create(
            model=model_id,
            max_tokens=8192,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        update_status(status_file, progress=80)

        # Extract and save response
        response_text = ""
        for block in message.content:
            if block.type == "text":
                response_text += block.text
                print(block.text)

        # Save response to file
        response_file = working_dir / "response.txt"
        response_file.write_text(response_text, encoding='utf-8')

        # Save full message metadata
        metadata_file = working_dir / "response_metadata.json"
        metadata_file.write_text(json.dumps({
            "model": message.model,
            "stop_reason": message.stop_reason,
            "usage": {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens
            },
            "completed_at": datetime.now().isoformat()
        }, indent=2), encoding='utf-8')

        print()
        print("-" * 80)
        print(f"Agent completed successfully")
        print(f"Stop reason: {message.stop_reason}")
        print(f"Input tokens: {message.usage.input_tokens}")
        print(f"Output tokens: {message.usage.output_tokens}")
        print(f"Response saved to: {response_file}")
        print("=" * 80)

        # Update final status
        update_status(status_file,
                     status="completed",
                     progress=100,
                     stop_reason=message.stop_reason,
                     input_tokens=message.usage.input_tokens,
                     output_tokens=message.usage.output_tokens)

        sys.exit(0)

    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)

        # Save error
        error_file = working_dir / "error.txt"
        error_file.write_text(f"{datetime.now().isoformat()}\n{str(e)}\n", encoding='utf-8')

        update_status(status_file, status="failed", error=str(e))

        sys.exit(1)


if __name__ == "__main__":
    main()
