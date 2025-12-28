# AWS Cost Monitoring Setup Script
# Sets up AWS Budgets and Cost Anomaly Detection for Ziggie ecosystem
# Usage: .\setup-cost-monitoring.ps1
#
# Prerequisites:
# - AWS CLI installed at "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
# - Configured AWS credentials with budgets and ce permissions
# - SNS topic ziggie-alerts already exists
#
# Created: 2025-12-27
# Account: 785186659442
# Region: eu-north-1 (for SNS), us-east-1 (for Budgets API)

$ErrorActionPreference = "Stop"
$aws = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
$configDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$accountId = "785186659442"
$region = "eu-north-1"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "         ZIGGIE COST MONITORING SETUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Verify AWS access
Write-Host "[1/6] Verifying AWS credentials..." -ForegroundColor Yellow
try {
    $identity = & $aws sts get-caller-identity --output json | ConvertFrom-Json
    Write-Host "  OK - Authenticated as: $($identity.Arn)" -ForegroundColor Green
    $accountId = $identity.Account
} catch {
    Write-Host "  FAILED - Could not authenticate with AWS" -ForegroundColor Red
    exit 1
}

# Step 2: Verify SNS topic exists
Write-Host "[2/6] Verifying SNS topic ziggie-alerts..." -ForegroundColor Yellow
try {
    $snsArn = "arn:aws:sns:${region}:${accountId}:ziggie-alerts"
    $topics = & $aws sns list-topics --region $region --output json | ConvertFrom-Json
    $found = $topics.Topics | Where-Object { $_.TopicArn -eq $snsArn }
    if ($found) {
        Write-Host "  OK - SNS topic exists: $snsArn" -ForegroundColor Green
    } else {
        Write-Host "  WARNING - SNS topic not found, creating..." -ForegroundColor Yellow
        & $aws sns create-topic --name ziggie-alerts --region $region
        Write-Host "  OK - SNS topic created" -ForegroundColor Green
    }
} catch {
    Write-Host "  FAILED - SNS check failed: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Check if budget already exists
Write-Host "[3/6] Checking existing budgets..." -ForegroundColor Yellow
try {
    $budgets = & $aws budgets describe-budgets --account-id $accountId --region us-east-1 --output json 2>$null | ConvertFrom-Json
    $existingBudget = $budgets.Budgets | Where-Object { $_.BudgetName -eq "ziggie-monthly" }
    if ($existingBudget) {
        Write-Host "  INFO - Budget 'ziggie-monthly' already exists" -ForegroundColor Yellow
        Write-Host "  Current limit: $($existingBudget.BudgetLimit.Amount) $($existingBudget.BudgetLimit.Unit)" -ForegroundColor Yellow
        $response = Read-Host "  Do you want to delete and recreate? (y/n)"
        if ($response -eq "y") {
            Write-Host "  Deleting existing budget..." -ForegroundColor Yellow
            & $aws budgets delete-budget --account-id $accountId --budget-name "ziggie-monthly" --region us-east-1
            Write-Host "  OK - Deleted" -ForegroundColor Green
        } else {
            Write-Host "  SKIPPED - Keeping existing budget" -ForegroundColor Yellow
            $skipBudget = $true
        }
    } else {
        Write-Host "  OK - No existing budget found" -ForegroundColor Green
    }
} catch {
    Write-Host "  OK - No existing budgets (first time setup)" -ForegroundColor Green
}

# Step 4: Create the budget
if (-not $skipBudget) {
    Write-Host "[4/6] Creating AWS Budget 'ziggie-monthly' ($150/month)..." -ForegroundColor Yellow
    try {
        $budgetFile = Join-Path $configDir "budget-ziggie-monthly.json"
        $notificationsFile = Join-Path $configDir "budget-notifications.json"

        if (-not (Test-Path $budgetFile)) {
            Write-Host "  FAILED - Budget config file not found: $budgetFile" -ForegroundColor Red
            exit 1
        }

        if (-not (Test-Path $notificationsFile)) {
            Write-Host "  FAILED - Notifications config file not found: $notificationsFile" -ForegroundColor Red
            exit 1
        }

        # Create budget with notifications
        & $aws budgets create-budget `
            --account-id $accountId `
            --budget file://$budgetFile `
            --notifications-with-subscribers file://$notificationsFile `
            --region us-east-1

        Write-Host "  OK - Budget created with 4 alert thresholds:" -ForegroundColor Green
        Write-Host "       - 50% ($75) - ACTUAL" -ForegroundColor Gray
        Write-Host "       - 80% ($120) - ACTUAL" -ForegroundColor Gray
        Write-Host "       - 100% ($150) - ACTUAL" -ForegroundColor Gray
        Write-Host "       - 120% ($180) - FORECASTED" -ForegroundColor Gray
    } catch {
        Write-Host "  FAILED - Could not create budget: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[4/6] SKIPPED - Budget creation" -ForegroundColor Yellow
}

# Step 5: Create Cost Anomaly Detection
Write-Host "[5/6] Setting up Cost Anomaly Detection..." -ForegroundColor Yellow
try {
    # Check for existing monitors
    $monitors = & $aws ce get-anomaly-monitors --region us-east-1 --output json 2>$null | ConvertFrom-Json
    $existingMonitor = $monitors.AnomalyMonitors | Where-Object { $_.MonitorName -eq "ziggie-cost-anomaly-monitor" }

    if ($existingMonitor) {
        Write-Host "  INFO - Anomaly monitor already exists" -ForegroundColor Yellow
        $monitorArn = $existingMonitor.MonitorArn
    } else {
        # Create the monitor
        $monitorFile = Join-Path $configDir "cost-anomaly-monitor.json"
        $result = & $aws ce create-anomaly-monitor `
            --anomaly-monitor file://$monitorFile `
            --region us-east-1 `
            --output json | ConvertFrom-Json
        $monitorArn = $result.MonitorArn
        Write-Host "  OK - Anomaly monitor created: $monitorArn" -ForegroundColor Green
    }

    # Check for existing subscription
    $subscriptions = & $aws ce get-anomaly-subscriptions --region us-east-1 --output json 2>$null | ConvertFrom-Json
    $existingSub = $subscriptions.AnomalySubscriptions | Where-Object { $_.SubscriptionName -eq "ziggie-anomaly-alerts" }

    if ($existingSub) {
        Write-Host "  INFO - Anomaly subscription already exists" -ForegroundColor Yellow
    } else {
        # Create the subscription with the monitor ARN
        $subscriptionJson = @{
            SubscriptionName = "ziggie-anomaly-alerts"
            Frequency = "IMMEDIATE"
            MonitorArnList = @($monitorArn)
            Subscribers = @(
                @{
                    Type = "SNS"
                    Address = "arn:aws:sns:${region}:${accountId}:ziggie-alerts"
                }
            )
            ThresholdExpression = @{
                Dimensions = @{
                    Key = "ANOMALY_TOTAL_IMPACT_ABSOLUTE"
                    MatchOptions = @("GREATER_THAN_OR_EQUAL")
                    Values = @("10")
                }
            }
        } | ConvertTo-Json -Depth 10

        $tempFile = Join-Path $env:TEMP "anomaly-subscription-temp.json"
        $subscriptionJson | Out-File -FilePath $tempFile -Encoding utf8

        & $aws ce create-anomaly-subscription `
            --anomaly-subscription file://$tempFile `
            --region us-east-1

        Remove-Item $tempFile -ErrorAction SilentlyContinue
        Write-Host "  OK - Anomaly subscription created (alerts for anomalies > $10)" -ForegroundColor Green
    }
} catch {
    Write-Host "  WARNING - Cost Anomaly Detection setup failed: $_" -ForegroundColor Yellow
    Write-Host "  This may require Cost Explorer to be enabled in your account" -ForegroundColor Yellow
}

# Step 6: Verify setup
Write-Host "[6/6] Verifying cost monitoring setup..." -ForegroundColor Yellow
try {
    # List budgets
    $budgets = & $aws budgets describe-budgets --account-id $accountId --region us-east-1 --output json | ConvertFrom-Json
    $ziggieBudget = $budgets.Budgets | Where-Object { $_.BudgetName -eq "ziggie-monthly" }

    if ($ziggieBudget) {
        Write-Host "  OK - Budget verified:" -ForegroundColor Green
        Write-Host "       Name: $($ziggieBudget.BudgetName)" -ForegroundColor Gray
        Write-Host "       Limit: $($ziggieBudget.BudgetLimit.Amount) $($ziggieBudget.BudgetLimit.Unit)" -ForegroundColor Gray
        Write-Host "       Type: $($ziggieBudget.BudgetType)" -ForegroundColor Gray
    }

    # List anomaly monitors
    $monitors = & $aws ce get-anomaly-monitors --region us-east-1 --output json | ConvertFrom-Json
    $ziggieMonitor = $monitors.AnomalyMonitors | Where-Object { $_.MonitorName -eq "ziggie-cost-anomaly-monitor" }

    if ($ziggieMonitor) {
        Write-Host "  OK - Anomaly Monitor verified:" -ForegroundColor Green
        Write-Host "       Name: $($ziggieMonitor.MonitorName)" -ForegroundColor Gray
        Write-Host "       ARN: $($ziggieMonitor.MonitorArn)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  WARNING - Could not verify all components" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "         COST MONITORING SETUP COMPLETE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "SUMMARY:" -ForegroundColor White
Write-Host "  - Budget: ziggie-monthly ($150/month)" -ForegroundColor Gray
Write-Host "  - Alerts: 50%, 80%, 100%, 120% thresholds" -ForegroundColor Gray
Write-Host "  - Anomaly Detection: >$10 unexpected costs" -ForegroundColor Gray
Write-Host "  - Notifications: SNS topic ziggie-alerts" -ForegroundColor Gray
Write-Host ""
Write-Host "VIEW COST REPORTS:" -ForegroundColor White
Write-Host "  Console: https://console.aws.amazon.com/cost-management/home" -ForegroundColor Cyan
Write-Host "  Budgets: https://console.aws.amazon.com/billing/home#/budgets" -ForegroundColor Cyan
Write-Host ""
Write-Host "CLI Commands:" -ForegroundColor White
Write-Host '  Current month costs:' -ForegroundColor Gray
Write-Host '  & $aws ce get-cost-and-usage --time-period Start=2025-12-01,End=2025-12-31 --granularity MONTHLY --metrics BlendedCost --region us-east-1' -ForegroundColor DarkGray
Write-Host ""
Write-Host '  Budget status:' -ForegroundColor Gray
Write-Host '  & $aws budgets describe-budget --account-id $accountId --budget-name ziggie-monthly --region us-east-1' -ForegroundColor DarkGray
Write-Host ""
