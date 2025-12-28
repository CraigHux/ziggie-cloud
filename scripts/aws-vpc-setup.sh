#!/bin/bash

###############################################################################
# AWS VPC Setup Script for Ziggie Cloud
#
# Description: Automated VPC infrastructure deployment for hybrid VPS + AWS
# Version: 1.0
# Date: 2025-12-23
#
# Prerequisites:
#   - AWS CLI installed and configured (aws configure)
#   - jq installed (for JSON parsing)
#   - Permissions: ec2:*, iam:*, route53:*, acm:*
#
# Usage:
#   ./aws-vpc-setup.sh [phase]
#   Phases: all, vpc, security-groups, endpoints, bastion, gpu, s3, dns
#
# Example:
#   ./aws-vpc-setup.sh all          # Deploy everything
#   ./aws-vpc-setup.sh vpc          # Only VPC setup
#   ./aws-vpc-setup.sh bastion      # Only bastion host
###############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REGION="eu-north-1"
VPC_CIDR="10.0.0.0/16"
PUBLIC_SUBNET_CIDR="10.0.1.0/24"
PRIVATE_SUBNET_CIDR="10.0.10.0/24"
VPS_IP="82.25.112.73/32"
PROJECT_TAG="Ziggie"
ENVIRONMENT_TAG="Production"

# Resource names
VPC_NAME="ziggie-cloud-vpc"
PUBLIC_SUBNET_NAME="ziggie-public-subnet-1a"
PRIVATE_SUBNET_NAME="ziggie-private-subnet-1b"
IGW_NAME="ziggie-igw"
RT_PUBLIC_NAME="ziggie-public-rt"
SG_GPU_NAME="ziggie-gpu-sg"
SG_BASTION_NAME="ziggie-bastion-sg"
SG_ENDPOINT_NAME="ziggie-endpoint-sg"
BASTION_NAME="ziggie-bastion"
GPU_NAME="ziggie-gpu"

# State file to store resource IDs
STATE_FILE="$HOME/.aws-ziggie-state.json"

###############################################################################
# Helper Functions
###############################################################################

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

save_state() {
    local key=$1
    local value=$2
    if [ ! -f "$STATE_FILE" ]; then
        echo "{}" > "$STATE_FILE"
    fi
    jq --arg k "$key" --arg v "$value" '.[$k] = $v' "$STATE_FILE" > "${STATE_FILE}.tmp"
    mv "${STATE_FILE}.tmp" "$STATE_FILE"
    log_info "Saved $key = $value to state file"
}

get_state() {
    local key=$1
    if [ -f "$STATE_FILE" ]; then
        jq -r --arg k "$key" '.[$k] // empty' "$STATE_FILE"
    fi
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not found. Install: https://aws.amazon.com/cli/"
        exit 1
    fi

    if ! command -v jq &> /dev/null; then
        log_error "jq not found. Install: sudo apt-get install jq"
        exit 1
    fi

    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Run: aws configure"
        exit 1
    fi

    log_info "Prerequisites OK"
}

###############################################################################
# Phase 1: VPC Setup
###############################################################################

setup_vpc() {
    log_info "=== Phase 1: VPC Setup ==="

    # Check if VPC already exists
    VPC_ID=$(get_state "VPC_ID")
    if [ -z "$VPC_ID" ]; then
        log_info "Creating VPC ($VPC_CIDR)..."
        VPC_ID=$(aws ec2 create-vpc \
            --cidr-block "$VPC_CIDR" \
            --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=$VPC_NAME},{Key=Project,Value=$PROJECT_TAG},{Key=Environment,Value=$ENVIRONMENT_TAG}]" \
            --region "$REGION" \
            --query 'Vpc.VpcId' \
            --output text)
        save_state "VPC_ID" "$VPC_ID"
    else
        log_warn "VPC already exists: $VPC_ID"
    fi

    # Enable DNS
    log_info "Enabling DNS support and hostnames..."
    aws ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-support --region "$REGION"
    aws ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-hostnames --region "$REGION"

    # Create public subnet
    SUBNET_PUBLIC=$(get_state "SUBNET_PUBLIC")
    if [ -z "$SUBNET_PUBLIC" ]; then
        log_info "Creating public subnet ($PUBLIC_SUBNET_CIDR)..."
        SUBNET_PUBLIC=$(aws ec2 create-subnet \
            --vpc-id "$VPC_ID" \
            --cidr-block "$PUBLIC_SUBNET_CIDR" \
            --availability-zone "${REGION}a" \
            --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PUBLIC_SUBNET_NAME},{Key=Type,Value=public}]" \
            --region "$REGION" \
            --query 'Subnet.SubnetId' \
            --output text)
        save_state "SUBNET_PUBLIC" "$SUBNET_PUBLIC"

        # Enable auto-assign public IP
        aws ec2 modify-subnet-attribute \
            --subnet-id "$SUBNET_PUBLIC" \
            --map-public-ip-on-launch \
            --region "$REGION"
    else
        log_warn "Public subnet already exists: $SUBNET_PUBLIC"
    fi

    # Create private subnet
    SUBNET_PRIVATE=$(get_state "SUBNET_PRIVATE")
    if [ -z "$SUBNET_PRIVATE" ]; then
        log_info "Creating private subnet ($PRIVATE_SUBNET_CIDR)..."
        SUBNET_PRIVATE=$(aws ec2 create-subnet \
            --vpc-id "$VPC_ID" \
            --cidr-block "$PRIVATE_SUBNET_CIDR" \
            --availability-zone "${REGION}b" \
            --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PRIVATE_SUBNET_NAME},{Key=Type,Value=private}]" \
            --region "$REGION" \
            --query 'Subnet.SubnetId' \
            --output text)
        save_state "SUBNET_PRIVATE" "$SUBNET_PRIVATE"
    else
        log_warn "Private subnet already exists: $SUBNET_PRIVATE"
    fi

    # Create Internet Gateway
    IGW_ID=$(get_state "IGW_ID")
    if [ -z "$IGW_ID" ]; then
        log_info "Creating Internet Gateway..."
        IGW_ID=$(aws ec2 create-internet-gateway \
            --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=$IGW_NAME}]" \
            --region "$REGION" \
            --query 'InternetGateway.InternetGatewayId' \
            --output text)
        save_state "IGW_ID" "$IGW_ID"

        # Attach to VPC
        aws ec2 attach-internet-gateway \
            --vpc-id "$VPC_ID" \
            --internet-gateway-id "$IGW_ID" \
            --region "$REGION"
    else
        log_warn "Internet Gateway already exists: $IGW_ID"
    fi

    # Create public route table
    RT_PUBLIC=$(get_state "RT_PUBLIC")
    if [ -z "$RT_PUBLIC" ]; then
        log_info "Creating public route table..."
        RT_PUBLIC=$(aws ec2 create-route-table \
            --vpc-id "$VPC_ID" \
            --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=$RT_PUBLIC_NAME}]" \
            --region "$REGION" \
            --query 'RouteTable.RouteTableId' \
            --output text)
        save_state "RT_PUBLIC" "$RT_PUBLIC"

        # Add default route to IGW
        aws ec2 create-route \
            --route-table-id "$RT_PUBLIC" \
            --destination-cidr-block "0.0.0.0/0" \
            --gateway-id "$IGW_ID" \
            --region "$REGION"

        # Associate with public subnet
        aws ec2 associate-route-table \
            --subnet-id "$SUBNET_PUBLIC" \
            --route-table-id "$RT_PUBLIC" \
            --region "$REGION"
    else
        log_warn "Public route table already exists: $RT_PUBLIC"
    fi

    log_info "VPC setup complete!"
    log_info "VPC ID: $VPC_ID"
    log_info "Public Subnet: $SUBNET_PUBLIC"
    log_info "Private Subnet: $SUBNET_PRIVATE"
}

###############################################################################
# Phase 2: Security Groups
###############################################################################

setup_security_groups() {
    log_info "=== Phase 2: Security Groups ==="

    VPC_ID=$(get_state "VPC_ID")
    if [ -z "$VPC_ID" ]; then
        log_error "VPC not found. Run 'vpc' phase first."
        exit 1
    fi

    # GPU Security Group
    SG_GPU=$(get_state "SG_GPU")
    if [ -z "$SG_GPU" ]; then
        log_info "Creating GPU Security Group..."
        SG_GPU=$(aws ec2 create-security-group \
            --group-name "$SG_GPU_NAME" \
            --description "Security group for GPU instances (ComfyUI)" \
            --vpc-id "$VPC_ID" \
            --region "$REGION" \
            --query 'GroupId' \
            --output text)
        save_state "SG_GPU" "$SG_GPU"

        # ComfyUI API from VPS
        aws ec2 authorize-security-group-ingress \
            --group-id "$SG_GPU" \
            --protocol tcp --port 8188 \
            --cidr "$VPS_IP" \
            --region "$REGION"

        # HTTPS from VPS
        aws ec2 authorize-security-group-ingress \
            --group-id "$SG_GPU" \
            --protocol tcp --port 443 \
            --cidr "$VPS_IP" \
            --region "$REGION"

        # Tag SG
        aws ec2 create-tags \
            --resources "$SG_GPU" \
            --tags Key=Name,Value="$SG_GPU_NAME" Key=Service,Value=ComfyUI \
            --region "$REGION"
    else
        log_warn "GPU Security Group already exists: $SG_GPU"
    fi

    # Bastion Security Group
    SG_BASTION=$(get_state "SG_BASTION")
    if [ -z "$SG_BASTION" ]; then
        log_info "Creating Bastion Security Group..."
        SG_BASTION=$(aws ec2 create-security-group \
            --group-name "$SG_BASTION_NAME" \
            --description "Security group for SSH bastion host" \
            --vpc-id "$VPC_ID" \
            --region "$REGION" \
            --query 'GroupId' \
            --output text)
        save_state "SG_BASTION" "$SG_BASTION"

        # SSH from VPS
        aws ec2 authorize-security-group-ingress \
            --group-id "$SG_BASTION" \
            --protocol tcp --port 22 \
            --cidr "$VPS_IP" \
            --region "$REGION"

        # Tag SG
        aws ec2 create-tags \
            --resources "$SG_BASTION" \
            --tags Key=Name,Value="$SG_BASTION_NAME" Key=Service,Value=Bastion \
            --region "$REGION"
    else
        log_warn "Bastion Security Group already exists: $SG_BASTION"
    fi

    # Add bastion to GPU SSH rule
    log_info "Adding SSH rule to GPU Security Group (from Bastion)..."
    aws ec2 authorize-security-group-ingress \
        --group-id "$SG_GPU" \
        --protocol tcp --port 22 \
        --source-group "$SG_BASTION" \
        --region "$REGION" 2>/dev/null || log_warn "SSH rule already exists"

    # VPC Endpoint Security Group
    SG_ENDPOINT=$(get_state "SG_ENDPOINT")
    if [ -z "$SG_ENDPOINT" ]; then
        log_info "Creating VPC Endpoint Security Group..."
        SG_ENDPOINT=$(aws ec2 create-security-group \
            --group-name "$SG_ENDPOINT_NAME" \
            --description "Security group for VPC endpoints" \
            --vpc-id "$VPC_ID" \
            --region "$REGION" \
            --query 'GroupId' \
            --output text)
        save_state "SG_ENDPOINT" "$SG_ENDPOINT"

        # HTTPS from GPU
        aws ec2 authorize-security-group-ingress \
            --group-id "$SG_ENDPOINT" \
            --protocol tcp --port 443 \
            --source-group "$SG_GPU" \
            --region "$REGION"

        # HTTPS from VPS
        aws ec2 authorize-security-group-ingress \
            --group-id "$SG_ENDPOINT" \
            --protocol tcp --port 443 \
            --cidr "$VPS_IP" \
            --region "$REGION"

        # Tag SG
        aws ec2 create-tags \
            --resources "$SG_ENDPOINT" \
            --tags Key=Name,Value="$SG_ENDPOINT_NAME" Key=Service,Value=VPCEndpoint \
            --region "$REGION"
    else
        log_warn "VPC Endpoint Security Group already exists: $SG_ENDPOINT"
    fi

    log_info "Security Groups setup complete!"
    log_info "GPU SG: $SG_GPU"
    log_info "Bastion SG: $SG_BASTION"
    log_info "Endpoint SG: $SG_ENDPOINT"
}

###############################################################################
# Phase 3: VPC Endpoints
###############################################################################

setup_vpc_endpoints() {
    log_info "=== Phase 3: VPC Endpoints ==="

    VPC_ID=$(get_state "VPC_ID")
    RT_PUBLIC=$(get_state "RT_PUBLIC")
    SUBNET_PUBLIC=$(get_state "SUBNET_PUBLIC")
    SG_ENDPOINT=$(get_state "SG_ENDPOINT")

    if [ -z "$VPC_ID" ] || [ -z "$RT_PUBLIC" ]; then
        log_error "VPC or route table not found. Run 'vpc' phase first."
        exit 1
    fi

    # S3 Gateway Endpoint (FREE)
    VPCE_S3=$(get_state "VPCE_S3")
    if [ -z "$VPCE_S3" ]; then
        log_info "Creating S3 Gateway Endpoint (FREE)..."
        VPCE_S3=$(aws ec2 create-vpc-endpoint \
            --vpc-id "$VPC_ID" \
            --service-name "com.amazonaws.${REGION}.s3" \
            --route-table-ids "$RT_PUBLIC" \
            --region "$REGION" \
            --query 'VpcEndpoint.VpcEndpointId' \
            --output text)
        save_state "VPCE_S3" "$VPCE_S3"

        # Tag endpoint
        aws ec2 create-tags \
            --resources "$VPCE_S3" \
            --tags Key=Name,Value=ziggie-s3-endpoint Key=Service,Value=S3 \
            --region "$REGION"
    else
        log_warn "S3 Gateway Endpoint already exists: $VPCE_S3"
    fi

    # Secrets Manager Interface Endpoint ($7.20/month)
    VPCE_SECRETS=$(get_state "VPCE_SECRETS")
    if [ -z "$VPCE_SECRETS" ]; then
        log_info "Creating Secrets Manager Interface Endpoint ($7.20/month)..."
        VPCE_SECRETS=$(aws ec2 create-vpc-endpoint \
            --vpc-id "$VPC_ID" \
            --vpc-endpoint-type Interface \
            --service-name "com.amazonaws.${REGION}.secretsmanager" \
            --subnet-ids "$SUBNET_PUBLIC" \
            --security-group-ids "$SG_ENDPOINT" \
            --private-dns-enabled \
            --region "$REGION" \
            --query 'VpcEndpoint.VpcEndpointId' \
            --output text)
        save_state "VPCE_SECRETS" "$VPCE_SECRETS"

        # Tag endpoint
        aws ec2 create-tags \
            --resources "$VPCE_SECRETS" \
            --tags Key=Name,Value=ziggie-secrets-endpoint Key=Service,Value=SecretsManager \
            --region "$REGION"
    else
        log_warn "Secrets Manager Endpoint already exists: $VPCE_SECRETS"
    fi

    log_info "VPC Endpoints setup complete!"
    log_info "S3 Endpoint: $VPCE_S3 (FREE)"
    log_info "Secrets Manager Endpoint: $VPCE_SECRETS ($7.20/month)"
}

###############################################################################
# Phase 4: Bastion Host
###############################################################################

setup_bastion() {
    log_info "=== Phase 4: Bastion Host ==="

    SUBNET_PUBLIC=$(get_state "SUBNET_PUBLIC")
    SG_BASTION=$(get_state "SG_BASTION")

    if [ -z "$SUBNET_PUBLIC" ] || [ -z "$SG_BASTION" ]; then
        log_error "Subnet or Security Group not found. Run previous phases first."
        exit 1
    fi

    # Check if key pair exists
    KEY_NAME="ziggie-bastion-key"
    if ! aws ec2 describe-key-pairs --key-names "$KEY_NAME" --region "$REGION" &>/dev/null; then
        log_info "Creating SSH key pair: $KEY_NAME"
        aws ec2 create-key-pair \
            --key-name "$KEY_NAME" \
            --region "$REGION" \
            --query 'KeyMaterial' \
            --output text > "$HOME/.ssh/${KEY_NAME}.pem"
        chmod 400 "$HOME/.ssh/${KEY_NAME}.pem"
        log_info "Key saved to: $HOME/.ssh/${KEY_NAME}.pem"
    else
        log_warn "SSH key pair already exists: $KEY_NAME"
    fi

    # Launch bastion instance
    BASTION_ID=$(get_state "BASTION_ID")
    if [ -z "$BASTION_ID" ]; then
        log_info "Launching bastion host (t3.nano)..."

        # Get latest Ubuntu 24.04 AMI
        AMI_ID=$(aws ec2 describe-images \
            --owners 099720109477 \
            --filters "Name=name,Values=ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*" \
            --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
            --region "$REGION" \
            --output text)

        BASTION_ID=$(aws ec2 run-instances \
            --image-id "$AMI_ID" \
            --instance-type t3.nano \
            --key-name "$KEY_NAME" \
            --security-group-ids "$SG_BASTION" \
            --subnet-id "$SUBNET_PUBLIC" \
            --associate-public-ip-address \
            --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$BASTION_NAME},{Key=Role,Value=bastion}]" \
            --region "$REGION" \
            --query 'Instances[0].InstanceId' \
            --output text)
        save_state "BASTION_ID" "$BASTION_ID"

        log_info "Waiting for bastion to start..."
        aws ec2 wait instance-running --instance-ids "$BASTION_ID" --region "$REGION"
    else
        log_warn "Bastion host already exists: $BASTION_ID"
    fi

    # Get public IP
    BASTION_IP=$(aws ec2 describe-instances \
        --instance-ids "$BASTION_ID" \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --region "$REGION" \
        --output text)
    save_state "BASTION_IP" "$BASTION_IP"

    log_info "Bastion Host setup complete!"
    log_info "Instance ID: $BASTION_ID"
    log_info "Public IP: $BASTION_IP"
    log_info "SSH: ssh -i $HOME/.ssh/${KEY_NAME}.pem ubuntu@$BASTION_IP"
}

###############################################################################
# Phase 5: Display Summary
###############################################################################

display_summary() {
    log_info "=== Deployment Summary ==="

    echo ""
    echo "Resource IDs:"
    echo "-------------"
    cat "$STATE_FILE" | jq -r 'to_entries[] | "\(.key): \(.value)"'

    echo ""
    echo "Next Steps:"
    echo "-----------"
    echo "1. SSH to bastion: ssh -i ~/.ssh/ziggie-bastion-key.pem ubuntu@$(get_state 'BASTION_IP')"
    echo "2. Deploy GPU instance: ./aws-vpc-setup.sh gpu"
    echo "3. Create S3 bucket: ./aws-vpc-setup.sh s3"
    echo "4. Configure DNS: ./aws-vpc-setup.sh dns"
    echo ""
    echo "Estimated Monthly Cost: \$133.87"
    echo "  - GPU (spot): \$112.97"
    echo "  - Bastion: \$3.80"
    echo "  - VPC Endpoints: \$7.20"
    echo "  - S3 + other: \$9.90"
    echo ""
}

###############################################################################
# Main
###############################################################################

main() {
    check_prerequisites

    PHASE="${1:-all}"

    case $PHASE in
        all)
            setup_vpc
            setup_security_groups
            setup_vpc_endpoints
            setup_bastion
            display_summary
            ;;
        vpc)
            setup_vpc
            ;;
        security-groups)
            setup_security_groups
            ;;
        endpoints)
            setup_vpc_endpoints
            ;;
        bastion)
            setup_bastion
            ;;
        summary)
            display_summary
            ;;
        *)
            log_error "Unknown phase: $PHASE"
            echo "Usage: $0 [all|vpc|security-groups|endpoints|bastion|summary]"
            exit 1
            ;;
    esac
}

main "$@"
