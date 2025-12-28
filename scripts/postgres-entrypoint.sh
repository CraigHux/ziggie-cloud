#!/bin/bash
set -euo pipefail

echo "=== PostgreSQL Startup ==="
echo "Fetching database password from AWS Secrets Manager..."

# Fetch password from Secrets Manager
POSTGRES_PASSWORD=$(aws secretsmanager get-secret-value \
    --secret-id ziggie/prod/postgres-master \
    --region "${AWS_REGION:-eu-north-1}" \
    --query SecretString \
    --output text 2>/dev/null | jq -r '.password')

export POSTGRES_PASSWORD

# Fetch username
POSTGRES_USER=$(aws secretsmanager get-secret-value \
    --secret-id ziggie/prod/postgres-master \
    --region "${AWS_REGION:-eu-north-1}" \
    --query SecretString \
    --output text 2>/dev/null | jq -r '.username')

export POSTGRES_USER

echo "Database credentials loaded"
echo "Database: ${POSTGRES_DB:-ziggie_prod}"
echo "User: ${POSTGRES_USER}"

# Run original PostgreSQL entrypoint
exec docker-entrypoint.sh postgres
