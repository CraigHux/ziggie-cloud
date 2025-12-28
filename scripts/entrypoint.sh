#!/bin/bash
set -euo pipefail

echo "=== Ziggie Container Startup ==="
echo "Fetching secrets from AWS Secrets Manager..."
echo "Region: ${AWS_REGION:-eu-north-1}"

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

# Function to fetch entire secret as JSON
fetch_secret_json() {
    local secret_name=$1

    aws secretsmanager get-secret-value \
        --secret-id "$secret_name" \
        --region "${AWS_REGION:-eu-north-1}" \
        --query SecretString \
        --output text 2>/dev/null
}

# Cache file for secrets (reduces API calls)
CACHE_FILE="/tmp/.secrets_cache"
CACHE_TTL=300  # 5 minutes

# Check cache validity
if [ -f "$CACHE_FILE" ]; then
    CACHE_AGE=$(($(date +%s) - $(stat -c %Y "$CACHE_FILE" 2>/dev/null || stat -f %m "$CACHE_FILE")))
    if [ $CACHE_AGE -lt $CACHE_TTL ]; then
        echo "Using cached secrets (age: ${CACHE_AGE}s)"
        source "$CACHE_FILE"
        exec "$@"
    fi
fi

echo "Fetching fresh secrets from AWS..."

# Fetch API keys
export OPENAI_API_KEY=$(fetch_secret "ziggie/prod/openai-api-key" "api_key")
export ELEVENLABS_API_KEY=$(fetch_secret "ziggie/prod/elevenlabs-api-key" "api_key")
export MESHY_API_KEY=$(fetch_secret "ziggie/prod/meshy-api-key" "api_key")
export STRIPE_SECRET_KEY=$(fetch_secret "ziggie/prod/stripe-secret-key" "api_key")
export SENDGRID_API_KEY=$(fetch_secret "ziggie/prod/sendgrid-api-key" "api_key")

# Fetch database credentials
DB_SECRET=$(fetch_secret_json "ziggie/prod/postgres-master")
export DATABASE_URL=$(echo "$DB_SECRET" | jq -r '.connection_string')
export DB_HOST=$(echo "$DB_SECRET" | jq -r '.host')
export DB_PORT=$(echo "$DB_SECRET" | jq -r '.port')
export DB_NAME=$(echo "$DB_SECRET" | jq -r '.dbname')
export DB_USER=$(echo "$DB_SECRET" | jq -r '.username')
export DB_PASSWORD=$(echo "$DB_SECRET" | jq -r '.password')

# Fetch JWT secret
export JWT_SECRET=$(fetch_secret "ziggie/prod/jwt-secret" "secret")

# Fetch Redis password
REDIS_PASSWORD=$(fetch_secret "ziggie/prod/redis-password" "password")
export REDIS_URL="redis://:${REDIS_PASSWORD}@redis:6379/0"

# Fetch RabbitMQ credentials
RABBITMQ_PASSWORD=$(fetch_secret "ziggie/prod/rabbitmq-password" "password")
export RABBITMQ_URL="amqp://ziggie:${RABBITMQ_PASSWORD}@rabbitmq:5672"

# Cache secrets for next startup
{
    echo "export OPENAI_API_KEY='$OPENAI_API_KEY'"
    echo "export ELEVENLABS_API_KEY='$ELEVENLABS_API_KEY'"
    echo "export MESHY_API_KEY='$MESHY_API_KEY'"
    echo "export STRIPE_SECRET_KEY='$STRIPE_SECRET_KEY'"
    echo "export SENDGRID_API_KEY='$SENDGRID_API_KEY'"
    echo "export DATABASE_URL='$DATABASE_URL'"
    echo "export JWT_SECRET='$JWT_SECRET'"
    echo "export REDIS_URL='$REDIS_URL'"
    echo "export RABBITMQ_URL='$RABBITMQ_URL'"
} > "$CACHE_FILE"
chmod 600 "$CACHE_FILE"

echo "Secrets loaded successfully"
echo "Starting application..."

# Execute the main process
exec "$@"
