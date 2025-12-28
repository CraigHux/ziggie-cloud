#!/bin/bash
set -euo pipefail

REGION="${AWS_REGION:-eu-north-1}"
BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup-file.tar.gz or s3://path/to/backup.tar.gz>"
    exit 1
fi

echo "=== AWS Secrets Manager Restore ==="
echo "Backup file: $BACKUP_FILE"

# Download from S3 if URL provided
if [[ "$BACKUP_FILE" == s3://* ]]; then
    echo "Downloading from S3..."
    LOCAL_BACKUP="/tmp/$(basename $BACKUP_FILE)"
    aws s3 cp "$BACKUP_FILE" "$LOCAL_BACKUP" --region "$REGION"
    BACKUP_FILE="$LOCAL_BACKUP"
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Extract backup
BACKUP_DIR="${BACKUP_FILE%.tar.gz}"
echo "Extracting backup..."
tar xzf "$BACKUP_FILE" -C /tmp
BACKUP_DIR="/tmp/$(basename $BACKUP_DIR)"

# Read manifest
MANIFEST="$BACKUP_DIR/manifest.json"
if [ ! -f "$MANIFEST" ]; then
    echo "ERROR: Manifest file not found in backup"
    exit 1
fi

SECRETS=$(jq -r '.secrets[]' "$MANIFEST")
SECRET_COUNT=$(jq -r '.secret_count' "$MANIFEST")
BACKUP_DATE=$(jq -r '.backup_date' "$MANIFEST")

echo "Backup date: $BACKUP_DATE"
echo "Secrets to restore: $SECRET_COUNT"
echo ""

# Confirmation prompt
read -p "This will overwrite existing secrets. Continue? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Restore each secret
COUNTER=0
SUCCESS=0
FAILED=0

for SECRET_NAME in $SECRETS; do
    COUNTER=$((COUNTER + 1))
    SAFE_NAME=$(echo "$SECRET_NAME" | sed 's/\//_/g')

    echo "[$COUNTER/$SECRET_COUNT] Restoring: $SECRET_NAME"

    VALUE_FILE="$BACKUP_DIR/${SAFE_NAME}_value.json"
    METADATA_FILE="$BACKUP_DIR/${SAFE_NAME}_metadata.json"

    if [ ! -f "$VALUE_FILE" ]; then
        echo "WARNING: Value file not found, skipping: $SECRET_NAME"
        FAILED=$((FAILED + 1))
        continue
    fi

    # Extract secret value
    SECRET_STRING=$(jq -r '.SecretString' "$VALUE_FILE" 2>/dev/null)
    if [ -z "$SECRET_STRING" ] || [ "$SECRET_STRING" = "null" ]; then
        echo "WARNING: Invalid secret value, skipping: $SECRET_NAME"
        FAILED=$((FAILED + 1))
        continue
    fi

    # Get tags from metadata
    TAGS=""
    if [ -f "$METADATA_FILE" ]; then
        TAGS=$(jq -r '.Tags // [] | map("Key=\(.Key),Value=\(.Value)") | join(" ")' "$METADATA_FILE" 2>/dev/null || echo "")
    fi

    # Try to create secret (will fail if exists)
    if aws secretsmanager create-secret \
        --name "$SECRET_NAME" \
        --secret-string "$SECRET_STRING" \
        ${TAGS:+--tags $TAGS} \
        --region "$REGION" \
        > /dev/null 2>&1; then
        echo "  Created new secret"
        SUCCESS=$((SUCCESS + 1))
    else
        # Secret exists, update it
        if aws secretsmanager update-secret \
            --secret-id "$SECRET_NAME" \
            --secret-string "$SECRET_STRING" \
            --region "$REGION" \
            > /dev/null 2>&1; then
            echo "  Updated existing secret"
            SUCCESS=$((SUCCESS + 1))
        else
            echo "  ERROR: Failed to restore secret"
            FAILED=$((FAILED + 1))
        fi
    fi
done

# Cleanup
rm -rf "$BACKUP_DIR"
[ -f "${LOCAL_BACKUP:-}" ] && rm "$LOCAL_BACKUP"

echo ""
echo "=== Restore Complete ==="
echo "Total secrets: $SECRET_COUNT"
echo "Successfully restored: $SUCCESS"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "All secrets restored successfully!"
    exit 0
else
    echo "Some secrets failed to restore. Review the logs above."
    exit 1
fi
