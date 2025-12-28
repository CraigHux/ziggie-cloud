#!/bin/bash
# n8n Workflow Export Script
# Usage: ./n8n-export-workflows.sh <N8N_API_KEY>
#
# Get API key from n8n: Settings > API > Create API Key
#
# Example:
#   export N8N_API_KEY="your-api-key-here"
#   ./n8n-export-workflows.sh

N8N_HOST="${N8N_HOST:-http://82.25.112.73:5678}"
N8N_API_KEY="${1:-$N8N_API_KEY}"
OUTPUT_DIR="${2:-C:/Ziggie/ziggie-cloud-repo/n8n-workflows}"

if [ -z "$N8N_API_KEY" ]; then
    echo "Error: N8N_API_KEY required"
    echo "Usage: $0 <api-key> [output-dir]"
    echo ""
    echo "To get API key:"
    echo "1. Login to n8n at $N8N_HOST"
    echo "2. Go to Settings > API"
    echo "3. Create new API key"
    exit 1
fi

echo "Exporting n8n workflows from $N8N_HOST..."
mkdir -p "$OUTPUT_DIR"

# Get all workflows
WORKFLOWS=$(curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_HOST/api/v1/workflows")

# Check for errors
if echo "$WORKFLOWS" | grep -q '"message"'; then
    echo "Error: $(echo "$WORKFLOWS" | jq -r '.message')"
    exit 1
fi

# Export each workflow
echo "$WORKFLOWS" | jq -c '.data[]' | while read -r workflow; do
    ID=$(echo "$workflow" | jq -r '.id')
    NAME=$(echo "$workflow" | jq -r '.name' | tr ' ' '_' | tr -cd '[:alnum:]_-')

    echo "Exporting: $NAME (ID: $ID)"

    # Get full workflow with nodes
    curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_HOST/api/v1/workflows/$ID" > "$OUTPUT_DIR/${NAME}_${ID}.json"
done

echo ""
echo "Exported to: $OUTPUT_DIR"
ls -la "$OUTPUT_DIR"
