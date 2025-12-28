# Ziggie GPU Spot Instance Launcher
# Usage: .\launch-gpu.ps1 [-InstanceType g4dn.xlarge] [-MaxPrice 0.25]

param(
    [string]$InstanceType = "g4dn.xlarge",
    [string]$MaxPrice = "0.25",
    [string]$SubnetId = "subnet-040ca7f02458c6f42"
)

$aws = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
$Region = "eu-north-1"

Write-Host "=== Ziggie GPU Spot Instance Launcher ===" -ForegroundColor Cyan
Write-Host "Instance Type: $InstanceType"
Write-Host "Max Spot Price: `$$MaxPrice/hour"
Write-Host "Subnet: $SubnetId (eu-north-1c)"
Write-Host ""

# Check current spot price
Write-Host "Checking current spot prices..." -ForegroundColor Yellow
$spotPrice = & $aws ec2 describe-spot-price-history `
    --instance-types $InstanceType `
    --product-descriptions "Linux/UNIX" `
    --region $Region `
    --max-items 1 `
    --query "SpotPriceHistory[0].SpotPrice" `
    --output text

Write-Host "Current spot price: `$$spotPrice/hour" -ForegroundColor Green

# Launch instance
Write-Host ""
Write-Host "Launching spot instance..." -ForegroundColor Yellow

$result = & $aws ec2 run-instances `
    --launch-template LaunchTemplateName=ziggie-gpu-spot `
    --instance-market-options "MarketType=spot,SpotOptions={MaxPrice=$MaxPrice,SpotInstanceType=one-time}" `
    --subnet-id $SubnetId `
    --region $Region `
    --output json 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error launching instance:" -ForegroundColor Red
    Write-Host $result
    exit 1
}

$instanceData = $result | ConvertFrom-Json
$instanceId = $instanceData.Instances[0].InstanceId

Write-Host "Instance launched: $instanceId" -ForegroundColor Green
Write-Host ""
Write-Host "Waiting for instance to get public IP..." -ForegroundColor Yellow

# Wait for public IP
Start-Sleep -Seconds 10

$publicIp = & $aws ec2 describe-instances `
    --instance-ids $instanceId `
    --query "Reservations[0].Instances[0].PublicIpAddress" `
    --output text `
    --region $Region

Write-Host ""
Write-Host "=== Instance Ready ===" -ForegroundColor Cyan
Write-Host "Instance ID: $instanceId"
Write-Host "Public IP: $publicIp"
Write-Host ""
Write-Host "Connect via SSH:" -ForegroundColor Yellow
Write-Host "  ssh -i C:\Ziggie\aws-config\ziggie-gpu-key.pem ubuntu@$publicIp"
Write-Host ""
Write-Host "ComfyUI will be available at (after ~5 min bootstrap):" -ForegroundColor Yellow
Write-Host "  http://${publicIp}:8188"
Write-Host ""
Write-Host "To terminate:" -ForegroundColor Yellow
Write-Host "  .\stop-gpu.ps1 $instanceId"
