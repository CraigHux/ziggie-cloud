#!/bin/bash
# =============================================================================
# S3 Asset Sync Script for Ziggie
# =============================================================================
# Syncs game assets between local directories and S3 bucket
# Usage: ./s3-sync.sh [upload|download|sync] [asset-type]
# =============================================================================

set -euo pipefail

# Configuration
S3_BUCKET="${S3_BUCKET:-ziggie-assets-prod}"
AWS_REGION="${AWS_REGION:-eu-north-1}"
LOCAL_ASSETS_DIR="${LOCAL_ASSETS_DIR:-./assets}"
S3_PREFIX="${S3_PREFIX:-game-assets}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check AWS CLI is installed
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
}

# Check AWS credentials
check_aws_credentials() {
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
    log_info "AWS credentials verified"
}

# Upload assets to S3
upload_assets() {
    local asset_type="${1:-all}"
    local source_dir="$LOCAL_ASSETS_DIR"
    local s3_path="s3://$S3_BUCKET/$S3_PREFIX"

    if [ "$asset_type" != "all" ]; then
        source_dir="$LOCAL_ASSETS_DIR/$asset_type"
        s3_path="s3://$S3_BUCKET/$S3_PREFIX/$asset_type"
    fi

    if [ ! -d "$source_dir" ]; then
        log_error "Source directory does not exist: $source_dir"
        exit 1
    fi

    log_info "Uploading assets from $source_dir to $s3_path..."

    aws s3 sync "$source_dir" "$s3_path" \
        --region "$AWS_REGION" \
        --delete \
        --exclude "*.tmp" \
        --exclude "*.bak" \
        --exclude ".DS_Store" \
        --exclude "Thumbs.db" \
        --include "*.png" \
        --include "*.jpg" \
        --include "*.jpeg" \
        --include "*.webp" \
        --include "*.svg" \
        --include "*.gif" \
        --include "*.glb" \
        --include "*.gltf" \
        --include "*.fbx" \
        --include "*.obj" \
        --include "*.blend" \
        --include "*.json" \
        --include "*.wav" \
        --include "*.mp3" \
        --include "*.ogg"

    log_info "Upload complete!"
}

# Download assets from S3
download_assets() {
    local asset_type="${1:-all}"
    local dest_dir="$LOCAL_ASSETS_DIR"
    local s3_path="s3://$S3_BUCKET/$S3_PREFIX"

    if [ "$asset_type" != "all" ]; then
        dest_dir="$LOCAL_ASSETS_DIR/$asset_type"
        s3_path="s3://$S3_BUCKET/$S3_PREFIX/$asset_type"
    fi

    mkdir -p "$dest_dir"

    log_info "Downloading assets from $s3_path to $dest_dir..."

    aws s3 sync "$s3_path" "$dest_dir" \
        --region "$AWS_REGION" \
        --exclude "*.tmp" \
        --exclude "*.bak"

    log_info "Download complete!"
}

# Bidirectional sync (local changes take precedence)
sync_assets() {
    local asset_type="${1:-all}"

    log_info "Performing bidirectional sync for: $asset_type"

    # First pull remote changes
    download_assets "$asset_type"

    # Then push local changes (local wins conflicts)
    upload_assets "$asset_type"

    log_info "Sync complete!"
}

# List assets in S3
list_assets() {
    local asset_type="${1:-}"
    local s3_path="s3://$S3_BUCKET/$S3_PREFIX"

    if [ -n "$asset_type" ]; then
        s3_path="$s3_path/$asset_type"
    fi

    log_info "Listing assets in $s3_path..."
    aws s3 ls "$s3_path" --recursive --region "$AWS_REGION" --human-readable --summarize
}

# Get S3 bucket stats
bucket_stats() {
    log_info "Getting bucket statistics..."

    echo ""
    echo "=== S3 Bucket: $S3_BUCKET ==="
    echo ""

    # Total size
    aws s3 ls "s3://$S3_BUCKET/$S3_PREFIX/" --recursive --region "$AWS_REGION" --summarize | tail -2

    echo ""
    echo "=== Asset Types ==="

    # Count by folder
    for folder in units buildings terrain effects ui audio; do
        count=$(aws s3 ls "s3://$S3_BUCKET/$S3_PREFIX/$folder/" --recursive --region "$AWS_REGION" 2>/dev/null | wc -l || echo "0")
        echo "  $folder: $count files"
    done
}

# Print usage
usage() {
    echo "Usage: $0 [command] [asset-type]"
    echo ""
    echo "Commands:"
    echo "  upload [type]   - Upload local assets to S3"
    echo "  download [type] - Download assets from S3"
    echo "  sync [type]     - Bidirectional sync (local wins)"
    echo "  list [type]     - List assets in S3"
    echo "  stats           - Show bucket statistics"
    echo ""
    echo "Asset types: units, buildings, terrain, effects, ui, audio, all (default)"
    echo ""
    echo "Environment variables:"
    echo "  S3_BUCKET       - S3 bucket name (default: ziggie-assets-prod)"
    echo "  AWS_REGION      - AWS region (default: eu-north-1)"
    echo "  LOCAL_ASSETS_DIR - Local assets directory (default: ./assets)"
    echo ""
    echo "Examples:"
    echo "  $0 upload units      - Upload only unit sprites"
    echo "  $0 download all      - Download all assets"
    echo "  $0 sync              - Full bidirectional sync"
    echo "  $0 list buildings    - List building assets in S3"
}

# Main
main() {
    local command="${1:-help}"
    local asset_type="${2:-all}"

    check_aws_cli

    case "$command" in
        upload)
            check_aws_credentials
            upload_assets "$asset_type"
            ;;
        download)
            check_aws_credentials
            download_assets "$asset_type"
            ;;
        sync)
            check_aws_credentials
            sync_assets "$asset_type"
            ;;
        list)
            check_aws_credentials
            list_assets "$asset_type"
            ;;
        stats)
            check_aws_credentials
            bucket_stats
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            log_error "Unknown command: $command"
            usage
            exit 1
            ;;
    esac
}

main "$@"
