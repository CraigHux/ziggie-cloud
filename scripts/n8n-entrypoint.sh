#!/bin/bash
set -euo pipefail

echo "=== n8n Startup ==="
echo "Fetching credentials from AWS Secrets Manager..."

# Function to fetch secret value
fetch_secret() {
    local secret_name=$1
    local json_key=$2

    aws secretsmanager get-secret-value \
        --secret-id "$secret_name" \
        --region "${AWS_REGION:-eu-north-1}" \
        --query SecretString \
        --output text 2>/dev/null | jq -r ".$json_key"
}

# Fetch n8n encryption key
export N8N_ENCRYPTION_KEY=$(fetch_secret "ziggie/prod/n8n-encryption-key" "key")

# Fetch database credentials
export DB_POSTGRESDB_HOST=postgres
export DB_POSTGRESDB_PORT=5432
export DB_POSTGRESDB_DATABASE=n8n
export DB_POSTGRESDB_USER=$(fetch_secret "ziggie/prod/postgres-master" "username")
export DB_POSTGRESDB_PASSWORD=$(fetch_secret "ziggie/prod/postgres-master" "password")

# Fetch API keys for n8n workflow integrations
export OPENAI_API_KEY=$(fetch_secret "ziggie/prod/openai-api-key" "api_key")
export ELEVENLABS_API_KEY=$(fetch_secret "ziggie/prod/elevenlabs-api-key" "api_key")
export MESHY_API_KEY=$(fetch_secret "ziggie/prod/meshy-api-key" "api_key")

# n8n specific settings
export N8N_HOST="${N8N_HOST:-n8n.ziggie.cloud}"
export N8N_PROTOCOL="${N8N_PROTOCOL:-https}"
export WEBHOOK_URL="${WEBHOOK_URL:-https://n8n.ziggie.cloud}"
export GENERIC_TIMEZONE="${GENERIC_TIMEZONE:-Europe/Stockholm}"
export N8N_LOG_LEVEL="${N8N_LOG_LEVEL:-info}"

echo "Credentials loaded successfully"
echo "Starting n8n..."

# Start n8n
exec n8n start
