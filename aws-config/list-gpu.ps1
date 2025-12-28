# Ziggie GPU Instance Status
# Usage: .\list-gpu.ps1

$aws = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
$Region = "eu-north-1"

Write-Host "=== Ziggie GPU Instance Status ===" -ForegroundColor Cyan
Write-Host ""

# Get all Ziggie GPU instances
$instances = & $aws ec2 describe-instances `
    --filters "Name=tag:Project,Values=Ziggie" "Name=tag:Type,Values=GPU" `
    --query "Reservations[*].Instances[*].[InstanceId,PublicIpAddress,InstanceType,State.Name,LaunchTime]" `
    --output json `
    --region $Region | ConvertFrom-Json

$running = 0
$total = 0

foreach ($reservation in $instances) {
    foreach ($instance in $reservation) {
        $total++
        $state = $instance[3]
        $color = switch ($state) {
            "running" { $running++; "Green" }
            "pending" { "Yellow" }
            "stopping" { "Yellow" }
            "stopped" { "Gray" }
            "terminated" { "Red" }
            default { "White" }
        }

        Write-Host "Instance: $($instance[0])" -ForegroundColor $color
        Write-Host "  Public IP: $($instance[1] ?? 'N/A')"
        Write-Host "  Type: $($instance[2])"
        Write-Host "  State: $state"
        Write-Host "  Launched: $($instance[4])"

        if ($state -eq "running" -and $instance[1]) {
            Write-Host "  ComfyUI: http://$($instance[1]):8188" -ForegroundColor Cyan
            Write-Host "  SSH: ssh -i C:\Ziggie\aws-config\ziggie-gpu-key.pem ubuntu@$($instance[1])"
        }
        Write-Host ""
    }
}

if ($total -eq 0) {
    Write-Host "No Ziggie GPU instances found." -ForegroundColor Yellow
} else {
    Write-Host "Summary: $running running / $total total instances" -ForegroundColor Cyan
}

# Show current spot prices
Write-Host ""
Write-Host "Current Spot Prices (eu-north-1c):" -ForegroundColor Cyan
& $aws ec2 describe-spot-price-history `
    --instance-types g4dn.xlarge g4dn.2xlarge g5.xlarge `
    --product-descriptions "Linux/UNIX" `
    --region $Region `
    --max-items 3 `
    --query "SpotPriceHistory[*].[InstanceType,SpotPrice]" `
    --output table
