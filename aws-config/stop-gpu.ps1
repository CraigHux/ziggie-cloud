# Ziggie GPU Instance Stopper
# Usage: .\stop-gpu.ps1 [InstanceId]
# If no InstanceId provided, stops all Ziggie GPU instances

param(
    [string]$InstanceId
)

$aws = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
$Region = "eu-north-1"

Write-Host "=== Ziggie GPU Instance Manager ===" -ForegroundColor Cyan

if ($InstanceId) {
    # Stop specific instance
    Write-Host "Terminating instance: $InstanceId" -ForegroundColor Yellow
    & $aws ec2 terminate-instances --instance-ids $InstanceId --region $Region --output table
} else {
    # List and optionally stop all Ziggie GPU instances
    Write-Host "Finding all running Ziggie GPU instances..." -ForegroundColor Yellow

    $instances = & $aws ec2 describe-instances `
        --filters "Name=tag:Project,Values=Ziggie" "Name=tag:Type,Values=GPU" "Name=instance-state-name,Values=running,pending" `
        --query "Reservations[*].Instances[*].[InstanceId,PublicIpAddress,InstanceType,State.Name]" `
        --output json `
        --region $Region | ConvertFrom-Json

    if ($instances.Count -eq 0 -or $instances[0].Count -eq 0) {
        Write-Host "No running Ziggie GPU instances found." -ForegroundColor Green
        exit 0
    }

    Write-Host ""
    Write-Host "Running Ziggie GPU instances:" -ForegroundColor Cyan
    Write-Host "-----------------------------------------"

    $flatInstances = @()
    foreach ($reservation in $instances) {
        foreach ($instance in $reservation) {
            $flatInstances += $instance
            Write-Host "  ID: $($instance[0])"
            Write-Host "  IP: $($instance[1])"
            Write-Host "  Type: $($instance[2])"
            Write-Host "  State: $($instance[3])"
            Write-Host "-----------------------------------------"
        }
    }

    $confirm = Read-Host "Terminate ALL $($flatInstances.Count) instance(s)? (y/N)"
    if ($confirm -eq 'y' -or $confirm -eq 'Y') {
        $ids = $flatInstances | ForEach-Object { $_[0] }
        Write-Host "Terminating instances: $($ids -join ', ')" -ForegroundColor Yellow
        & $aws ec2 terminate-instances --instance-ids $ids --region $Region --output table
    } else {
        Write-Host "Cancelled." -ForegroundColor Yellow
    }
}
