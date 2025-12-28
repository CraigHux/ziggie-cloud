#!/bin/bash
set -euo pipefail

echo "=== Redis Startup ==="
echo "Fetching Redis password from AWS Secrets Manager..."

# Fetch password from Secrets Manager
REDIS_PASSWORD=$(aws secretsmanager get-secret-value \
    --secret-id ziggie/prod/redis-password \
    --region "${AWS_REGION:-eu-north-1}" \
    --query SecretString \
    --output text 2>/dev/null | jq -r '.password')

# Create Redis config with password
cat > /tmp/redis-runtime.conf <<EOF
# Runtime generated Redis configuration
requirepass ${REDIS_PASSWORD}

# Security settings
protected-mode yes
bind 0.0.0.0
port 6379

# Persistence
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /data

# Logging
loglevel notice
logfile ""

# Memory management
maxmemory 2gb
maxmemory-policy allkeys-lru

# Performance
tcp-backlog 511
timeout 300
tcp-keepalive 300
EOF

echo "Redis configuration generated with password"

# Start Redis with generated config
exec redis-server /tmp/redis-runtime.conf
