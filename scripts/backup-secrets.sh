#!/bin/bash
set -euo pipefail

REGION="${AWS_REGION:-eu-north-1}"
BACKUP_DIR="./secrets-backup-$(date +%Y%m%d-%H%M%S)"
S3_BUCKET="${BACKUP_S3_BUCKET:-ziggie-disaster-recovery}"
ENCRYPTION_KEY_ID="${KMS_KEY_ID}"

mkdir -p "$BACKUP_DIR"

echo "=== AWS Secrets Manager Backup ==="
echo "Region: $REGION"
echo "Backup directory: $BACKUP_DIR"
echo "S3 Bucket: $S3_BUCKET"

# List all secrets with Ziggie tag
SECRETS=$(aws secretsmanager list-secrets \
    --region "$REGION" \
    --query 'SecretList[?Tags[?Key==`Service` && Value==`Ziggie`]].Name' \
    --output text)

if [ -z "$SECRETS" ]; then
    echo "ERROR: No secrets found with Service=Ziggie tag"
    exit 1
fi

SECRET_COUNT=$(echo "$SECRETS" | wc -w)
echo "Found $SECRET_COUNT secrets to backup"

# Backup each secret
COUNTER=0
for SECRET_NAME in $SECRETS; do
    COUNTER=$((COUNTER + 1))
    echo "[$COUNTER/$SECRET_COUNT] Backing up: $SECRET_NAME"

    # Sanitize filename
    SAFE_NAME=$(echo "$SECRET_NAME" | sed 's/\//_/g')

    # Get secret metadata
    aws secretsmanager describe-secret \
        --secret-id "$SECRET_NAME" \
        --region "$REGION" \
        > "$BACKUP_DIR/${SAFE_NAME}_metadata.json" 2>/dev/null || {
            echo "WARNING: Failed to get metadata for $SECRET_NAME"
            continue
        }

    # Get secret value
    aws secretsmanager get-secret-value \
        --secret-id "$SECRET_NAME" \
        --region "$REGION" \
        > "$BACKUP_DIR/${SAFE_NAME}_value.json" 2>/dev/null || {
            echo "WARNING: Failed to get value for $SECRET_NAME"
            continue
        }

    # Get all versions
    aws secretsmanager list-secret-version-ids \
        --secret-id "$SECRET_NAME" \
        --region "$REGION" \
        > "$BACKUP_DIR/${SAFE_NAME}_versions.json" 2>/dev/null || {
            echo "WARNING: Failed to get versions for $SECRET_NAME"
        }
done

# Create backup manifest
cat > "$BACKUP_DIR/manifest.json" <<EOF
{
  "backup_date": "$(date -Iseconds)",
  "region": "$REGION",
  "secret_count": $SECRET_COUNT,
  "secrets": $(echo "$SECRETS" | tr ' ' '\n' | jq -R . | jq -s .)
}
EOF

echo "Creating backup archive..."
tar czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"
BACKUP_SIZE=$(du -h "${BACKUP_DIR}.tar.gz" | cut -f1)
echo "Backup archive created: ${BACKUP_DIR}.tar.gz ($BACKUP_SIZE)"

# Cleanup uncompressed directory
rm -rf "$BACKUP_DIR"

# Upload to S3 with encryption
echo "Uploading to S3..."
if [ -n "${ENCRYPTION_KEY_ID:-}" ]; then
    aws s3 cp "${BACKUP_DIR}.tar.gz" \
        "s3://${S3_BUCKET}/secrets-manager/$(basename ${BACKUP_DIR}).tar.gz" \
        --server-side-encryption aws:kms \
        --sse-kms-key-id "$ENCRYPTION_KEY_ID" \
        --region "$REGION"
else
    aws s3 cp "${BACKUP_DIR}.tar.gz" \
        "s3://${S3_BUCKET}/secrets-manager/$(basename ${BACKUP_DIR}).tar.gz" \
        --server-side-encryption AES256 \
        --region "$REGION"
fi

echo ""
echo "=== Backup Complete ==="
echo "Local file: ${BACKUP_DIR}.tar.gz"
echo "S3 location: s3://${S3_BUCKET}/secrets-manager/$(basename ${BACKUP_DIR}).tar.gz"
echo "Secrets backed up: $SECRET_COUNT"
echo "Backup size: $BACKUP_SIZE"
echo ""
echo "To restore: ./restore-secrets.sh s3://${S3_BUCKET}/secrets-manager/$(basename ${BACKUP_DIR}).tar.gz"
