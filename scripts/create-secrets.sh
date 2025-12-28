#!/bin/bash
set -euo pipefail

REGION="${AWS_REGION:-eu-north-1}"

echo "=== Creating Ziggie Cloud Secrets ==="
echo "Region: $REGION"
echo ""

# Function to create secret
create_secret() {
    local name=$1
    local description=$2
    local prompt_for_value=${3:-true}

    echo "Creating secret: $name"
    echo "Description: $description"

    if [ "$prompt_for_value" = "true" ]; then
        echo -n "Enter value (hidden): "
        read -s SECRET_VALUE
        echo ""
    fi

    # Create JSON format for API keys
    SECRET_JSON=$(jq -n --arg key "$SECRET_VALUE" '{api_key: $key}')

    aws secretsmanager create-secret \
        --name "$name" \
        --description "$description" \
        --secret-string "$SECRET_JSON" \
        --tags Key=Environment,Value=Production Key=Service,Value=Ziggie \
        --region "$REGION" \
        > /dev/null 2>&1 && echo "  ✓ Created successfully" || echo "  ✗ Failed (may already exist)"

    echo ""
}

# Function to create database secret
create_db_secret() {
    local name=$1
    local description=$2

    echo "Creating database secret: $name"
    echo "Description: $description"

    echo -n "Enter database host: "
    read DB_HOST
    echo -n "Enter database port (default 5432): "
    read DB_PORT
    DB_PORT=${DB_PORT:-5432}
    echo -n "Enter database name: "
    read DB_NAME
    echo -n "Enter database username: "
    read DB_USER
    echo -n "Enter database password (hidden): "
    read -s DB_PASSWORD
    echo ""

    # Create connection string
    CONNECTION_STRING="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

    # Create JSON with all fields
    SECRET_JSON=$(jq -n \
        --arg host "$DB_HOST" \
        --arg port "$DB_PORT" \
        --arg dbname "$DB_NAME" \
        --arg username "$DB_USER" \
        --arg password "$DB_PASSWORD" \
        --arg connection_string "$CONNECTION_STRING" \
        '{
            host: $host,
            port: ($port | tonumber),
            dbname: $dbname,
            username: $username,
            password: $password,
            connection_string: $connection_string,
            engine: "postgres"
        }')

    aws secretsmanager create-secret \
        --name "$name" \
        --description "$description" \
        --secret-string "$SECRET_JSON" \
        --tags Key=Environment,Value=Production Key=Service,Value=Ziggie \
        --region "$REGION" \
        > /dev/null 2>&1 && echo "  ✓ Created successfully" || echo "  ✗ Failed (may already exist)"

    echo ""
}

# Function to create simple secret (just value, not JSON)
create_simple_secret() {
    local name=$1
    local description=$2

    echo "Creating secret: $name"
    echo "Description: $description"
    echo -n "Enter value (hidden): "
    read -s SECRET_VALUE
    echo ""

    SECRET_JSON=$(jq -n --arg val "$SECRET_VALUE" '{secret: $val}')

    aws secretsmanager create-secret \
        --name "$name" \
        --description "$description" \
        --secret-string "$SECRET_JSON" \
        --tags Key=Environment,Value=Production Key=Service,Value=Ziggie \
        --region "$REGION" \
        > /dev/null 2>&1 && echo "  ✓ Created successfully" || echo "  ✗ Failed (may already exist)"

    echo ""
}

# Create all secrets
echo "This script will create all required secrets for Ziggie Cloud."
echo "Press Enter to continue or Ctrl+C to cancel..."
read

# AI API Keys
create_secret "ziggie/prod/openai-api-key" "OpenAI API Key for Ziggie Cloud production"
create_secret "ziggie/prod/elevenlabs-api-key" "ElevenLabs API Key for voice synthesis"
create_secret "ziggie/prod/meshy-api-key" "Meshy.ai API Key for 3D generation"

# Payment and Email
create_secret "ziggie/prod/stripe-secret-key" "Stripe Secret Key for payment processing"
create_secret "ziggie/prod/sendgrid-api-key" "SendGrid API Key for email"

# Database
create_db_secret "ziggie/prod/postgres-master" "PostgreSQL master database credentials"

# Application secrets
create_simple_secret "ziggie/prod/jwt-secret" "JWT signing secret"
create_simple_secret "ziggie/prod/n8n-encryption-key" "n8n encryption key"

# Infrastructure passwords
create_simple_secret "ziggie/prod/redis-password" "Redis password"
create_simple_secret "ziggie/prod/rabbitmq-password" "RabbitMQ password"

echo "=== Secret Creation Complete ==="
echo ""
echo "Verify all secrets were created:"
echo "aws secretsmanager list-secrets --region $REGION --query 'SecretList[?Tags[?Key==\`Service\` && Value==\`Ziggie\`]].Name' --output table"
